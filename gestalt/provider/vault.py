from .provider import Provider, ProviderConfig
import requests
from typing import Optional, Tuple
from dataclasses import dataclass
import hvac  # type: ignore
import os

@dataclass
class VaultConfig(ProviderConfig):
    """Configuration for Vault Instance
    
    Args:
        role: Kubernetes role. Default: None
        jwt: Kubernetes token. Default: None
        url: URL to vault instance. Default: VAULT_ADDR ENV VAR 
        token: Token to vault instance. Default: VAULT_TOKEN ENV VAR
        cert: Cerificate for vault instance. Default None
        verify: Verification for vault instance. Default True
    """
    role: Optional[str] = None
    jwt: Optional[str] = None
    url: Optional[str] = os.environ.get("VAULT_ADDR")
    token: Optional[str] = os.environ.get("VAULT_TOKEN")
    cert: Optional[Tuple(str, str)] = None
    verify: Optional[bool] = True

class Vault():
    def __init__(self,
                 config: VaultConfig) -> None:
        """Initialized vault client and authenticates vault

        Args:
            client_config (HVAC_ClientConfig): initializes vault. URL can be set in VAULT_ADDR
                environment variable, token can be set to VAULT_TOKEN environment variable.
                These will be picked by default if not set to empty string
            auth_config (HVAC_ClientAuthentication): authenticates the initialized vault client
                with role and jwt string from kubernetes
        """

        self.vault_client = hvac.Client(url=config.url,
                                        token=config.token,
                                        cert=config.cert,
                                        verify=config.verify)
        try:
            self.vault_client.is_authenticated()
        except requests.exceptions.MissingSchema:
            raise RuntimeError(
                "Gestalt Error: Incorrect VAULT_ADDR or VAULT_TOKEN provided")
        if config.role and config.jwt:
            try:
                self.vault_client.auth_kubernetes(
                    role=config.role,
                    jwt=config.jwt
                )
            except hvac.exceptions.InvalidPath:
                raise RuntimeError(
                    "Gestalt Error: Kubernetes auth couldn't be performed")
            except requests.exceptions.ConnectionError:
                raise RuntimeError("Gestalt Error: Couldn't connect to Vault")

    def get(self, key: str, path: str, filter: str) -> str:
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
            requested_data = response['data']['data'] if filter is None else response
            return requested_data[key]
        except hvac.exceptions.InvalidPath:
            raise RuntimeError(
                "Gestalt Error: The secret path or mount is set incorrectly"
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Gestalt Error: Gestalt couldn't connect to Vault")
        except Exception as err:
            raise RuntimeError(f"Gestalt Error: {err}")

    def clear(self, key, value):
        self.key = key
        [self.__provider_name, self.path] = value.split("+")[1].split("://")     # split the url
        try:
            self.__filter = self.path[1].split("#")[1]   # get the filter
        except IndexError:
            self.filter = None
            self.provider = self.initialize_provider(self.__provider_name)
            self.value = self.provider.get(self.key, self.path, self.filter)


Provider.register(Vault)