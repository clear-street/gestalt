from .vault import Vault


SUPPORTED_PROVIDERS = [
    "vault"
]


class Provider():
    """Abstract class for all providers"""
    def __init__(self, key: str, value: str):
        self.key = key
        [self.__provider_name, self.path] = value.split("+")[1].split("://")     # split the url
        try:
            self.__filter = self.path[1].split("#")[1]   # get the filter
        except IndexError:
            self.filter = None
        self.provider = self.initialize_provider(self.__provider_name)
        self.value = self.provider.get(self.key, self.path, self.filter)

    def get(self, key: str, path: str, filter: str):
        """Abstract method for getting data from the provider"""
        pass

    def initialize_provider(self, provider: str):
        """Initialize the provider"""
        if provider == "vault":
            return Vault()
