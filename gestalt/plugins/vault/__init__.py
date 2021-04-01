import sys
from typing import Dict
from vaultx import VaultClient
from gestalt import gestalt

vaultProvider = Vaultx.VaultConfigProvider({"token": "something"})
gestalt.remote.RegisterConfigProvider("vault", vault_provider)
gestalt.AddRemoteProvider("vault", "/secret/blah/balh")
getstalt.ReadRemoteConfig()

g: gestalt.Gestalt = gestalt.Gestalt()
class VaultConfigProvider(gestalt.ConfigProvider):
    def __init__(self, config: Dict[str, str]):
        self.client: VaultClient = VaultClient(g.read_config(config))

    def Get(self, path) -> Dict[str, any]:
        secret = self.client

        returns me a json

        wrap it in a dict
    
    def Watch():
        pass

    def WatchChannel():
        pass


def read_config(config_path):
    g = gestalt.Gestalt()
    g.add_config_path(config_path)
    g.build_config()