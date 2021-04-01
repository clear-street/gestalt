from ConfigProvider import ConfigProvider
from typing import Dict

config_provider: Dict[str, ConfigProvider] = {}

def new_config_provider_registry() -> Dict[str, ConfigProvider]:
        config_provider: Dict[str, ConfigProvider] = {} 
        return config_provider