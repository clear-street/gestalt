from abc import ABCMeta, abstractmethod
from typing import Tuple, Dict, Any, Optional, Union, List[Any]


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
    def get(self, key: str, path: str, filter: str, sep: Optional[str]) -> Union[str, int, float, bool, List[Any]]:
        """Abstract method to get a value from the provider
        """
        pass

    @property
    @abstractmethod
    def scheme(self) -> str:
        """Returns scheme of provider
        """
        pass
