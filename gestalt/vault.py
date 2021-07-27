from .helpers import parse_nested_dict_and_find_key
import requests
from typing import Optional
import hvac
import sys
import json

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

class Vault():
    def __init__(self,
                 url: Optional[str] = None,
                 token: Optional[str] = None,
                 cert: Optional[str] = None,
                 role: Optional[str] = None,
                 jwt: Optional[str] = None,
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
                "Gestalt Error: Incorrect VAULT_ADDR or VAULT_TOKEN provided")
        if role and jwt:
            try:
                self.vault_client.auth_kubernetes(\
                    role=role,
                    jwt=jwt
                )
            except hvac.exceptions.InvalidPath as err:
                raise RuntimeError(
                    "Gestalt Error: Kubernetes auth couldn't be performed")
            except requests.exceptions.ConnectionError as err:
                raise RuntimeError("Gestalt Error: Couldn't connect to Vault")


    def get(self, key: str, path: str, filter: str) -> str:
        print("Fetching secrets from VAULT")
        
        try:
            response = self.vault_client.read(path)
            if response is None:
                raise RuntimeError("Gestalt Error: No secrets found")
            requested_data = response['data']['data'] if filter is None else response
            return requested_data[key]
        except hvac.exceptions.InvalidPath as err:
            raise RuntimeError(
                "Gestalt Error: The secret path or mount is set incorrectly"
            )
        except requests.exceptions.ConnectionError as err:
            raise RuntimeError(
                "Gestalt Error: Gestalt couldn't connect to Vault")
        except Exception as err:
            raise RuntimeError(f"Gestalt Error: {err}")