

class RemoteProvider:
    def __init__(self):
        self.provider = str()
        self.endpoint = str()
        self.path = str()
        self.secret_keyring = str()

    def provider(self) -> str:
        return self.provider

    def endpoint(self) -> str:
        return self.endpoint

    def path(self) -> str:
        return self.path

    def secret_keyring(self) -> str:
        return self.secretKeyring

    def add_remote_provider(self, provider: str, endpoint: str, path: str) -> None:
        if provider:
            self.provider = provider 
        if endpoint:
            self.endpoint = endpoint
        if path:
            self.path = self.path

    def addRemoteProvider(self, provider: str, endpoint: str, path: str, secret_keyring: str) -> None:
        if provider: 
            self.provider = provider
        if endpoint:
            self.endpoint = endpoint
        if path:
            self.path = path
        if secret_keyring:
            self.secret_keyring = secret_keyring