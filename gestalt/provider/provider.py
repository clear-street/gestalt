from abc import ABCMeta, abstractmethod

class Provider(metaclass=ABCMeta):
    """Abstract provider class
    """
    
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Abstract initializer for the Provider class with ProviderConfig 

        Args:
            config (ProviderConfig): config for the provider
        """
        pass
    
    @abstractmethod
    def get(self, path: str):
        """Abstract get method to fetch the information available at the path

        Args:
            path (str): the path for the provider information fetching
        """
        pass