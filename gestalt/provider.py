from abc import ABCMeta, abstractmethod
from typing import Tuple, Dict, Any


class Provider(metaclass=ABCMeta):
    """Abstract provider class
    """
    @abstractmethod
    def __init__(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]):
        """Abstract initializer for the Provider class with ProviderConfig

        Args:
            config (ProviderConfig): config for the provider
        """
        pass

    @abstractmethod
    def get(self, key: str, path: str, filter: str) -> Any:
        """Abstract method to get a value from the provider
        """
        pass
