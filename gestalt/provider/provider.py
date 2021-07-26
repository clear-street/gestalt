
from gestalt.provider.vault import Vault


SUPPORTED_PROVIDERS = [
    "vault"
]

class Provider():
    """Abstract class for all providers"""
    def __init__(self, value):
        self.__provider_name = value.split("+")[1]    # get the provider name
        self.__path = self.__provider_name.split("://")[1]     # split the url
        self.__filter = self.__path[1].split("#")[1]   # get the filter
        self.provider = self.initialize_provider(self.__provider_name)
        self.provider.get(self.__path, self.__filter)

    def get(self, path: str, filter: str):
        """Abstract method for getting data from the provider"""
        pass


    def initialize_provider(self, provider: str):
        """Initialize the provider"""
        if provider == "vault":
            return Vault()