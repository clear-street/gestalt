from time import sleep
from gestalt.provider import Provider
import requests
from jsonpath_ng import parse  # type: ignore
from typing import Optional, Tuple, Any
import hvac  # type: ignore
import asyncio
import os
from threading import Thread
from retry import retry


class Vault(Provider):
    @retry(exceptions=RuntimeError, delay=2, tries=5)  # type: ignore
    def __init__(self,
                 cert: Optional[Tuple[str, str]] = None,
                 role: Optional[str] = None,
                 jwt: Optional[str] = None,
                 url: Optional[str] = os.environ.get("VAULT_ADDR"),
                 token: Optional[str] = os.environ.get("VAULT_TOKEN"),
                 verify: Optional[bool] = True) -> None:
        """Initialized vault client and authenticates vault

        Args:
            client_config (HVAC_ClientConfig): initializes vault. URL can be set in VAULT_ADDR
                environment variable, token can be set to VAULT_TOKEN environment variable.
                These will be picked by default if not set to empty string
            auth_config (HVAC_ClientAuthentication): authenticates the initialized vault client
                with role and jwt string from kubernetes
        """
        self.dynamic_token_queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=0)
        self.kubes_token_queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=0)

        self.vault_client = hvac.Client(url=url,
                                        token=token,
                                        cert=cert,
                                        verify=verify)

        try:
            self.vault_client.is_authenticated()
        except requests.exceptions.MissingSchema:
            raise RuntimeError(
                "Gestalt Error: Unable to connect to vault with the given configuration"
            )

        if role and jwt:
            try:
                hvac.api.auth_methods.Kubernetes(
                    self.vault_client.adapter).login(role=role, jwt=jwt)
                token = self.vault_client.auth.token.lookup_self()
                if token is not None:
                    kubes_token = (
                        "kubernetes",
                        token['data']['id'],  # type: ignore
                        token['data']['ttl'])  # type: ignore
                    self.kubes_token_queue.put(kubes_token)
            except hvac.exceptions.InvalidPath:
                raise RuntimeError(
                    "Gestalt Error: Kubernetes auth couldn't be performed")
            except requests.exceptions.ConnectionError:
                raise RuntimeError("Gestalt Error: Couldn't connect to Vault")

            dynamic_ttl_renew = Thread(name='dynamic-token-renew',
                                       target=asyncio.run,
                                       daemon=True,
                                       args=(self.worker(
                                           self.dynamic_token_queue), ))
            kubernetes_ttl_renew = Thread(name="kubes-token-renew",
                                          target=asyncio.run,
                                          daemon=True,
                                          args=(self.worker(
                                              self.kubes_token_queue), ))
            kubernetes_ttl_renew.start()

    @retry(RuntimeError, delay=3, tries=3)  # type: ignore
    def get(self, key: str, path: str, filter: str) -> Any:
        """Gets secret from vault
        Args:
            key (str): key to get secret from
            path (str): path to secret
            filter (str): filter to apply to secret
        Returns:
            secret (str): secret
        """
        try:
            response = self.vault_client.read(path)
            if response is None:
                raise RuntimeError("Gestalt Error: No secrets found")
            if response['lease_id']:
                dynamic_token = ("dynamic", response['lease_id'],
                                 response['lease_duration'])
                self.dynamic_token_queue.put_nowait(dynamic_token)
            requested_data = response["data"]["data"]
        except hvac.exceptions.InvalidPath:
            raise RuntimeError(
                "Gestalt Error: The secret path or mount is set incorrectly")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Gestalt Error: Gestalt couldn't connect to Vault")
        except Exception as err:
            raise RuntimeError(f"Gestalt Error: {err}")
        if filter is None:
            return requested_data
        secret = requested_data
        jsonpath_expression = parse(f"${filter}")
        match = jsonpath_expression.find(secret)
        if len(match) == 0:
            print("Path returned not matches for your secret")
        returned_value_from_secret = match[0].value
        if returned_value_from_secret == "":
            raise RuntimeError("Gestalt Error: Empty secret!")
        return returned_value_from_secret

    async def worker(self, token_queue: Any) -> None:
        """
        Worker function to renew lease on expiry
        """

        try:
            while True:
                if not token_queue.empty():
                    token_type, token_id, token_duration = token = await token_queue.get(
                    )
                    if token_type == "kubernetes":
                        self.vault_client.auth.token.renew(token_id)
                        print("kubernetes token for the app has been renewed")
                    elif token_type == "dynamic":
                        self.vault_client.sys.renew_lease(token_id)
                        print("dynamic token for the app has been renewed")
                    token_queue.task_done()
                    token_queue.put_nowait(token)
                    sleep((token_duration / 3) * 2)
        except hvac.exceptions.InvalidPath:
            raise RuntimeError(
                "Gestalt Error: The lease path or mount is set incorrectly")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Gestalt Error: Gestalt couldn't connect to Vault")
        except Exception as err:
            raise RuntimeError(f"Gestalt Error: {err}")
