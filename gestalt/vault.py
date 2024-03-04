import os
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from time import sleep
from typing import Any, Dict, List, Optional, Tuple, Union

import hvac  # type: ignore
import requests
from jsonpath_ng import parse  # type: ignore
from requests.exceptions import Timeout
from retry.api import retry_call

from gestalt.provider import Provider


class Vault(Provider):
    def __init__(
        self,
        cert: Optional[Tuple[str, str]] = None,
        role: Optional[str] = None,
        jwt: Optional[str] = None,
        url: Optional[str] = os.environ.get("VAULT_ADDR"),
        token: Optional[str] = os.environ.get("VAULT_TOKEN"),
        verify: Optional[bool] = True,
        scheme: str = "ref+vault://",
        delay: int = 60,
        tries: int = 5,
    ) -> None:
        """Initialized vault client and authenticates vault

        Args:
            client_config (HVAC_ClientConfig): initializes vault. URL can be set in VAULT_ADDR
                environment variable, token can be set to VAULT_TOKEN environment variable.
                These will be picked by default if not set to empty string
            auth_config (HVAC_ClientAuthentication): authenticates the initialized vault client
                with role and jwt string from kubernetes
        """
        self._scheme: str = scheme
        self._run_worker = True
        self.dynamic_token_queue: Queue[Tuple[str, str, str]] = Queue()
        self.kubes_token_queue: Queue[Tuple[str, str, str]] = Queue()

        self.vault_client = hvac.Client(url=url, token=token, cert=cert, verify=verify)
        self._secret_expiry_times: Dict[str, datetime] = dict()
        self._secret_values: Dict[str, Union[str, int, float, bool, List[Any]]] = dict()
        self._is_connected: bool = False
        self._role: Optional[str] = role
        self._jwt: Optional[str] = jwt
        self.delay = delay
        self.tries = tries
        print("CALLED VAULT INIT")

    def connect(self) -> None:
        print(f"CALLED CONNECT")
        try:
            retry_call(
                self.vault_client.is_authenticated,
                exceptions=(RuntimeError, Timeout),
                delay=self.delay,
                tries=self.tries,
            )
        except requests.exceptions.MissingSchema:
            raise RuntimeError(
                "Gestalt Error: Unable to connect to vault with the given configuration"
            )

        if self._role and self._jwt:
            try:
                hvac.api.auth_methods.Kubernetes(self.vault_client.adapter).login(
                    role=self._role, jwt=self._jwt
                )
                token = retry_call(
                    self.vault_client.auth.token.lookup_self,
                    exceptions=(RuntimeError, Timeout),
                    delay=self.delay,
                    tries=self.tries,
                )

                if token is not None:
                    kubes_token = (
                        "kubernetes",
                        token["data"]["id"],  # type: ignore
                        token["data"]["ttl"],
                    )  # type: ignore
                    self.kubes_token_queue.put(kubes_token)
            except hvac.exceptions.InvalidPath:
                raise RuntimeError(
                    "Gestalt Error: Kubernetes auth couldn't be performed"
                )
            except requests.exceptions.ConnectionError:
                raise RuntimeError("Gestalt Error: Couldn't connect to Vault")

            dynamic_ttl_renew = Thread(
                name="dynamic-token-renew",
                target=self.worker,
                daemon=True,
                args=(self.dynamic_token_queue,),
            )  # noqa: F841
            kubernetes_ttl_renew = Thread(
                name="kubes-token-renew",
                target=self.worker,
                daemon=True,
                args=(self.kubes_token_queue,),
            )
            kubernetes_ttl_renew.start()
        self._is_connected = True

    def stop(self) -> None:
        self._run_worker = False

    def __del__(self) -> None:
        self.stop()

    def get(
        self, key: str, path: str, filter: str, sep: Optional[str] = "."
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
        print(f"CALLED VAULT GET")
        if not self._is_connected:
            self.connect()
        # if the key has been read before and is not a TTL secret
        if key in self._secret_values and key not in self._secret_expiry_times:
            return self._secret_values[key]

        # if the secret can expire but hasn't expired yet
        if key in self._secret_expiry_times and not self._is_secret_expired(key):
            return self._secret_values[key]

        try:
            response = retry_call(
                self.vault_client.read,
                fargs=[path],
                exceptions=(RuntimeError, Timeout),
                delay=self.delay,
                tries=self.tries,
            )
            if response is None:
                raise RuntimeError("Gestalt Error: No secrets found")
            if response["lease_id"]:
                dynamic_token = (
                    "dynamic",
                    response["lease_id"],
                    response["lease_duration"],
                )
                self.dynamic_token_queue.put_nowait(dynamic_token)
            requested_data = response["data"].get("data", response["data"])
        except hvac.exceptions.InvalidPath:
            raise RuntimeError(
                "Gestalt Error: The secret path or mount is set incorrectly"
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Gestalt Error: Gestalt couldn't connect to Vault")
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

    def _set_secrets_ttl(self, requested_data: Dict[str, Any], key: str) -> None:
        last_vault_rotation_str = requested_data["last_vault_rotation"].split(".")[
            0
        ]  # to the nearest second
        last_vault_rotation_dt = datetime.strptime(
            last_vault_rotation_str, "%Y-%m-%dT%H:%M:%S"
        )
        ttl = requested_data["ttl"]
        secret_expires_dt = last_vault_rotation_dt + timedelta(seconds=ttl)
        self._secret_expiry_times[key] = secret_expires_dt

    def worker(self, token_queue: Queue) -> None:  # type: ignore
        """
        Worker function to renew lease on expiry
        """

        try:
            while self._run_worker:
                if not token_queue.empty():
                    token_type, token_id, token_duration = token = token_queue.get()
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
                "Gestalt Error: The lease path or mount is set incorrectly"
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Gestalt Error: Gestalt couldn't connect to Vault")
        except Exception as err:
            raise RuntimeError(f"Gestalt Error: {err}")

    @property
    def scheme(self) -> str:
        return self._scheme
