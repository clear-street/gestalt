from gestalt.remote_provider import RemoteProvider
from typing import Dict, Union
from . import config_provider

class ConfigProviderRegistry:
    """
    """
    config_providers: Dict[str, config_provider.ConfigProvider] = config_provider

    def register_provider(self, name: str, provider: RemoteProvider) -> None:
        """
        """
        if not self.get_config_provider(provider):
            self.config_providers.update({name, provider})

    def get_config_provider(self, rp: RemoteProvider) -> Union[RemoteProvider, bool]:
        """
        """
        provider = rp.provider()
        if self.rp.config_providers[provider]:
            return self.rp.config_providers[provider];
        return False