from typing import Dict
from gestalt.configprovider.config_provider import ConfigProvider

config_provider: Dict[str, ConfigProvider] = {}

def new_config_provider_registry() -> Dict[str, ConfigProvider]:
        config_provider: Dict[str, ConfigProvider] = {} 
        return config_provider
