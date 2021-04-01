from gestalt import Gestalt
from typing import Dict
from gestalt.configprovider.config_provider import ConfigProvider
from gestalt.plugins.vault.client import VaultClient

g: Gestalt = Gestalt()
class VaultConfigProvider(ConfigProvider):
    """
    """

    def __init__(self, config: Dict[str, str]):
        """
        """
        self.client: VaultClient = VaultClient(g.read_config(config))

    def Get(self, path) -> Dict[str, any]:
        """

        Args:


        Raises:


        Return:
        """
        secret = self.client

        returns me a json

        wrap it in a dict
    
    def Watch():
        """
        """
        pass

    def WatchChannel():
        """

        Args:

        Return:

        Raises:
        """
        pass