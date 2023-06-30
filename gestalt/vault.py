from datetime import datetime, timedelta
from time import sleep
from gestalt.provider import Provider
import requests
from jsonpath_ng import parse  # type: ignore
from typing import Optional, Tuple, Any, Dict, Union, List
import hvac  # type: ignore
import queue
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
                 verify: Optional[bool] = True,
                 scheme: str = "ref+vault://") -> None:
        """Initialized vault client and authenticates vault

        Args:
            client_config (HVAC_ClientConfig): initializes vault. URL can be set in VAULT_ADDR
                environment variable, token can be set to VAULT_TOKEN environment variable.
                These will be picked by default if not set to empty string
            auth_config (HVAC_ClientAuthentication): authenticates the initialized vault client
                with role and jwt string from kubernetes
        """
        self._scheme: str = scheme
        self.dynamic_token_queue: queue.Queue = queue.Queue()
        self.kubes_token_queue: queue.Queue = queue.Queue()

        self.vault_client = hvac.Client(url=url,
                                        token=token,
                                        cert=cert,
                                        verify=verify)
        self._secret_expiry_times: Dict[str, datetime] = dict()
        self._secret_values: Dict[str, Union[str, int, float, bool,
                                             List[Any]]] = dict()

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
                                       target=self.worker,
                                       daemon=True,
                                       args=(self.dynamic_token_queue,))
            kubernetes_ttl_renew = Thread(name="kubes-token-renew",
                                          target=self.worker,
                                          daemon=True,
                                          args=(self.kubes_token_queue,))
            kubernetes_ttl_renew.start()

    @retry(RuntimeError, delay=3, tries=3)  # type: ignore
    def get(
        self,
        key: str,
        path: str,
        filter: str,
        sep: Optional[str] = "."
    ) -> Union[str, int, float, bool, List[Any]]:
        """Gets secret from vault
        Args:
            key (str): key to get secret from
            path (str): path to secret
            filter (str): filter to apply to secret
            sep (str): delimiter used for flattening
        Returns:
            secret (str): secret
        """
        # if the key has been read before and is not a TTL secret
        if key in self._secret_values and key not in self._secret_expiry_times:
            return self._secret_values[key]

        # if the secret can expire but hasn't expired yet
        if key in self._secret_expiry_times and not self._is_secret_expired(
                key):
            return self._secret_values[key]

        try:
            response = self.vault_client.read(path)
            if response is None:
                raise RuntimeError("Gestalt Error: No secrets found")
            if response['lease_id']:
                dynamic_token = ("dynamic", response['lease_id'],
                                 response['lease_duration'])
                self.dynamic_token_queue.put_nowait(dynamic_token)
            requested_data = response["data"].get("data", response["data"])
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

        self._secret_values[key] = returned_value_from_secret
        if "ttl" in requested_data:
            self._set_secrets_ttl(requested_data, key)

        return returned_value_from_secret  # type: ignore

    def _is_secret_expired(self, key: str) -> bool:
        now = datetime.now()
        secret_expires_dt = self._secret_expiry_times[key]
        is_expired = now >= secret_expires_dt
        return is_expired

    def _set_secrets_ttl(self, requested_data: Dict[str, Any],
                         key: str) -> None:
        last_vault_rotation_str = requested_data["last_vault_rotation"].split(
            ".")[0]  # to the nearest second
        last_vault_rotation_dt = datetime.strptime(last_vault_rotation_str,
                                                   '%Y-%m-%dT%H:%M:%S')
        ttl = requested_data["ttl"]
        secret_expires_dt = last_vault_rotation_dt + timedelta(seconds=ttl)
        self._secret_expiry_times[key] = secret_expires_dt

    def worker(self, token_queue: queue.Queue) -> None:
        """
        Worker function to renew lease on expiry
        """

        try:
            while True:
                if not token_queue.empty():
                    token_type, token_id, token_duration = token = token_queue.get(
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

    @property
    def scheme(self) -> str:
        return self._scheme
