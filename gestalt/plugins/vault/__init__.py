from abc import abstractclassmethod
from gestalt.remote_provider import RemoteProvider
import hvac  # type: ignore
from gestalt import Gestalt
from typing import Dict, Any
from gestalt.configprovider.config_provider import ConfigProvider  # type: ignore
from gestalt.plugins.vault.client import VaultClient  # type: ignore

g: Gestalt = Gestalt()


class VaultConfigProvider(ConfigProvider):  # type: ignore
    """VaultConfigProvider that generates a config provider for Vault. 
        
       This class inherits from ConfigProvider
    """
    client: hvac.Client = hvac.Client()

    def __init__(self, config: Dict[str, str]):
        """Initializes the VaultConfigProvider

        Args:
            config (Dict[str])
        """
        self.client: hvac.Client = VaultClient(config)

    @abstractclassmethod
    def Get(self, rp: RemoteProvider) -> Any:
        """Gets the keys from the Vault Cluster.
        Currently only support kv.v2 secrets from the Vault Cluster 

        Args:
            rp (RemoteProvider): The vault remote provider

        Returns:
            Dict[str, any]: The key located at 'rp.path' 
        """
        secret: Dict[Any, Any] = self.client.secrets.kv.v2.read_secret_version(
            path=rp.path)
        return secret['data']['data']