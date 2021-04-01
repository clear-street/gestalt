from abc import abstractclassmethod
from gestalt.configprovider.config_provider_registry import ConfigProviderRegistry
from typing import Dict, Type
from . import config_provider
from gestalt.remote_provider import RemoteProvider

class ConfigProvider:
    """
    ConfigProvider is the interface defined by Gestalt for remote config providers
    """
    config_provider_registry = ConfigProviderRegistry()

    def register(self, name, provider):
        self.config_provider_registry

    # The type of client is key: string, value: hvac.client 
    @abstractclassmethod
    def Get(rp: RemoteProvider):
        """
        Args:
            rp: RemoteProvider
        """
        pass

    @abstractclassmethod
    def Watch():
        """
        Args:
            rp: RemoteProvider
        """
        pass

    @abstractclassmethod
    def WatchChannel():
        """
        Args:
            rp: RemoteProvider
        """
        pass



