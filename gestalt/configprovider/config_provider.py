from abc import abstractclassmethod
from typing import Dict, Union
from gestalt.remote_provider import RemoteProvider

config_provider: Dict[str, any] = {}

class ConfigProviderRegistry:
    """The registry for Config Providers
    """
    config_providers: Dict[str, any] = config_provider

    def register_provider(self, name: str, provider: any) -> None:
        """Receives a provider and registers it in the config_providers

        Args:
            name (str): The name of the provider
            provider (ConfigProvider): The provider for the name
        """
        self.config_providers[name] = provider

    def get_config_provider(self, rp: RemoteProvider) -> Union[any, bool]:
        """Gets a config providers from the list of remote providers

        Args:
            rp (RemoteProvider): Remote Provider that needs to be found

        Returns:
            config_provider: If config_provider for remote_provider is found, else boolean
        """
        provider = rp.provider
        if self.config_providers[provider]:
            return self.config_providers[provider]
        return False

class ConfigProvider:
    """ConfigProvider is the interface defined by Gestalt for remote config providers
    """

    config_provider_registry: Dict = ConfigProviderRegistry()
 
    @abstractclassmethod
    def Get(rp: RemoteProvider) -> any:
        """Get Abstract Method which gets implemented by the sub class that inherits
        ConfigProvider

        Args:
            rp: RemoteProvider

        Returns:
            any: The base class adds the restriction
        """
        pass


def new_config_provider_registry() -> Dict[str, ConfigProvider]:
    """Generates a new ConfigProviderRegistry

    Returns:
        config_provider_registry: a new dictionary with fomat Dict[str, ConfigProvider]
    """
    config_provider_registry: Dict[str, ConfigProvider] = {} 
    return config_provider_registry