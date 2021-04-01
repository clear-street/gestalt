from abc import abstractclassmethod
from typing import Dict

from gestalt.remote_provider import RemoteProvider
import string
from utility import new_config_provider_registry, config_provider
import remote_provider
import hvac

config_provider: Dict[str, ConfigProvider] = {}

def new_config_provider_registry() -> Dict[str, ConfigProvider]:
        config_provider: Dict[str, ConfigProvider] = {} 
        return config_provider

class UnsupportedProviderType(Exception):
    pass

# Make this abstract class
@abstractclassmethod
class ConfigProvider:
    """
    ConfigProvider is the interface defined by Gestalt for remote config providers
    """
    # The type of client is key: string, value: hvac.client
    clients: Dict[str, hvac.Client] = {} 

    @abstractclassmethod
    def Get(rp: RemoteProvider):
        pass


class ConfigProviderRegistry:
    configProviders: Dict[str, ConfigProvider] = {}

    def get_config_provider(self, rp: RemoteProvider):      
        provider = rp.provider()
        try:
            self.config_provider = self.r.configProviders[provider]
        except UnsupportedProviderType as err:
            print(err) 
        return self.config_provider.get()
    
