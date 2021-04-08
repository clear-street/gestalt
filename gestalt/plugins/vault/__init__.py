from abc import abstractclassmethod
from gestalt.remote_provider import RemoteProvider
import hvac
from gestalt import Gestalt
from typing import Dict
from gestalt.configprovider.config_provider import ConfigProvider
from gestalt.plugins.vault.client import VaultClient

g: Gestalt = Gestalt()
class VaultConfigProvider(ConfigProvider):
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
    def Get(self, rp: RemoteProvider) -> Dict[str, any]:
        """Gets the keys from the Vault Cluster.
        Currently only support kv.v2 secrets from the Vault Cluster 

        Args:
            rp (RemoteProvider): The vault remote provider

        Returns:
            Dict[str, any]: The key located at 'rp.path' 
        """
        # print(self.client.client.secrets)
       
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=rp.path
        )
        print(secret['data']['data'])
        return secret['data']['data']