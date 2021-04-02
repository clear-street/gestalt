from typing import List, Union

SupportedRemoteProviders: List[str] = ["etcd", "consul", "firestore"]

class RemoteProvider:
    """RemoteProvider class that generates a Remote Provider
    """

    def __init__(self, provider: str, endpoint: str, path: str, secret_keystring: Union[str, None]=None):
        """ Initializes the remote provider class

        Args:
            provider (str): The name of the provider
            endpoint (str): The endpoint of the provider
            path (str): The path to the provider 
            secret_keystring (str | None): The secret_keystring
        """
        self.provider = provider
        self.endpoint = endpoint
        self.path = path
        self.secret_keystring = secret_keystring