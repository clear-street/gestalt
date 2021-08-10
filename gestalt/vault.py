from .provider import Provider
import requests
from jsonpath_ng import parse  # type: ignore
from typing import Optional, Tuple, Any
import hvac  # type: ignore
import os


class Vault(Provider):
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
                self.vault_client.auth_kubernetes(role=role, jwt=jwt)
            except hvac.exceptions.InvalidPath:
                raise RuntimeError(
                    "Gestalt Error: Kubernetes auth couldn't be performed")
            except requests.exceptions.ConnectionError:
                raise RuntimeError("Gestalt Error: Couldn't connect to Vault")

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
            requested_data = response['data']['data']
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
