import os
from datetime import datetime, timedelta, timezone
from queue import Queue
from typing import Any, Dict, List, Optional, Tuple, Union

import hvac  # type: ignore
import requests
from jsonpath_ng import parse  # type: ignore
from requests.exceptions import Timeout
from retry.api import retry_call

from gestalt.provider import Provider
from dateutil.parser import isoparse

EXPIRATION_THRESHOLD_HOURS = 1


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
        self.kubes_token: Optional[Tuple[str, str, str, datetime]] = None

        self._vault_client: Optional[hvac.Client] = None
        self._secret_expiry_times: Dict[str, datetime] = dict()
        self._secret_values: Dict[str, Union[str, int, float, bool,
                                             List[Any]]] = dict()
        self._is_connected: bool = False
        self._role: Optional[str] = role
        self._jwt: Optional[str] = jwt
        self._url: Optional[str] = url
        self._token: Optional[str] = token
        self._cert: Optional[Tuple[str, str]] = cert
        self._verify: Optional[bool] = verify

        self.delay = delay
        self.tries = tries

    @property
    def vault_client(self) -> hvac.Client:
        if self._vault_client is None:
            self._vault_client = hvac.Client(url=self._url,
                                             token=self._token,
                                             cert=self._cert,
                                             verify=self._verify)
        return self._vault_client

    def connect(self) -> None:
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
                hvac.api.auth_methods.Kubernetes(
                    self.vault_client.adapter).login(role=self._role,
                                                     jwt=self._jwt)
                token = retry_call(
                    self.vault_client.auth.token.lookup_self,
                    exceptions=(RuntimeError, Timeout),
                    delay=self.delay,
                    tries=self.tries,
                )

                if token is not None:
                    print("Kubernetes login successful")
                    kubes_token = (
                        "kubernetes",
                        token["data"]["id"],
                        token["data"]["ttl"],
                        token["data"]['expire_time'],
                    )
                    self.kubes_token = kubes_token
            except hvac.exceptions.InvalidPath:
                raise RuntimeError(
                    "Gestalt Error: Kubernetes auth couldn't be performed")
            except requests.exceptions.ConnectionError:
                raise RuntimeError("Gestalt Error: Couldn't connect to Vault")

        self._is_connected = True

    def stop(self) -> None:
        self._run_worker = False

    def __del__(self) -> None:
        self.stop()

    def get(self,
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
        if not self._is_connected:
            self.connect()
        # if the key has been read before and is not a TTL secret
        if key in self._secret_values and key not in self._secret_expiry_times:
            return self._secret_values[key]

        # if the secret can expire but hasn't expired yet
        if key in self._secret_expiry_times and not self._is_secret_expired(
                key):
            return self._secret_values[key]

        # verify if the token still valid, in case not, call connect()
        self._validate_token_expiration()

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

        returned_value_from_secret: Union[str, int, float,
                                          List[Any]] = match[0].value
        if returned_value_from_secret == "":
            raise RuntimeError("Gestalt Error: Empty secret!")

        self._secret_values[key] = returned_value_from_secret
        if "ttl" in requested_data:
            self._set_secrets_ttl(requested_data, key)

        # TODO: unclear what this note means, was left my a previous dev along time ago.
        # should figure out what this does and why it's here.
        #
        # repr is converting the string to RAW string since \\$ was returning $\
        # Then we are removing single quotes (first and last char)
        if isinstance(returned_value_from_secret, str):
            return str(repr(returned_value_from_secret))[1:-1]
        return returned_value_from_secret

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
                                                   "%Y-%m-%dT%H:%M:%S")
        ttl = requested_data["ttl"]
        secret_expires_dt = last_vault_rotation_dt + timedelta(seconds=ttl)
        self._secret_expiry_times[key] = secret_expires_dt

    @property
    def scheme(self) -> str:
        return self._scheme

    def _validate_token_expiration(self) -> None:
        if self.kubes_token is not None:
            expire_time = self.kubes_token[3]
            # Use isoparse to correctly parse the datetime string
            expire_time = isoparse(expire_time)

            # Ensure the parsed time is in UTC
            if expire_time.tzinfo is None:
                expire_time = expire_time.replace(tzinfo=timezone.utc)
            else:
                expire_time = expire_time.astimezone(timezone.utc)

            current_time = datetime.now(timezone.utc)
            # in hours
            delta_time = (expire_time - current_time).total_seconds() / 3600

            if delta_time < EXPIRATION_THRESHOLD_HOURS:
                print(f"Re-authenticating with vault")
                self.connect()
            else:
                print(f"Token still valid for: {delta_time} hours")
        else:
            print(
                f"Can't reconnect, token information: {self.kubes_token}, not valid"
            )
