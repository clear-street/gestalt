import time
import hvac  # type: ignore
from typing import Optional, List, Tuple, Union
import requests
import threading
import os


class Vault():
    def __init__(self):
        self.__vault_paths: List[Tuple[Union[str, None], str]] = []
        self.secret_ttl_identifier: List[Tuple[str, int, float]] = []
        self.TTL_RENEW_INCREMENT: int = 300
        self.ttl_renew_thread = threading.Thread(name='ttl-renew', target=self.ttl_expire_check)


    def add_vault_config_provider(self,
                                  url: Optional[str] = None,
                                  token: Optional[str] = None,
                                  cert: Optional[str] = None,
                                  role: Optional[str] = None,
                                  jwt: Optional[str] = None,
                                  verify: Optional[bool] = True) -> None:
        """Initialized vault client and authenticates vault

        Args:
            client_config (HVAC_ClientConfig): initializes vault. URL can be set in VAULT_ADDR
                environment variable, token can be set to VAULT_TOKEN environment variable.
                These will be picked by default if not set to empty string
            auth_config (HVAC_ClientAuthentication): authenticates the initialized vault client
                with role and jwt string from kubernetes
        """

        self.vault_client = hvac.Client(url=url,
                                        token=token,
                                        cert=cert,
                                        verify=verify)
        try:
            self.vault_client.is_authenticated()
        except requests.exceptions.MissingSchema:
            raise RuntimeError(
                "Gestalt Error: Incorrect VAULT_ADDR or VAULT_TOKEN provided")
        if role and jwt:
            try:
                self.vault_client.auth_kubernetes(
                    role=role,
                    jwt=jwt
                )
            except hvac.exceptions.InvalidPath as err:
                raise RuntimeError(
                    "Gestalt Error: Kubernetes auth couldn't be performed")
            except requests.exceptions.ConnectionError as err:
                raise RuntimeError("Gestalt Error: Couldn't connect to Vault")

    def add_vault_secret_path(self,
                              path: str,
                              mount_path: Optional[str] = None) -> None:
        """Adds a vault secret with key and path to gestalt

        Args:
            path (str): The path to the secret in vault cluster
            mount_path ([type], optional): The mount_path for a non-default secret
                mount. Defaults to Optional[str].
        """
        mount_path = mount_path if mount_path != None else "secret"

        self.__vault_paths.append((mount_path, path))

    def fetch_vault_secrets(self) -> None:
        """Fetches client secrets from vault first checks the path provided 
        """
        if len(self.__vault_paths) <= 0:
            return
        print("Fetching secrets from VAULT")
        for vault_path in self.__vault_paths:
            secret_path = f"{vault_path[0]}/data/{vault_path[1]}""
            try:
                secret_token = self.vault_client.read(path=secret_path)
            except hvac.exceptions.InvalidPath as err:
                raise RuntimeError(
                    "Gestalt Error: The secret path or mount is set incorrectly"
                )
            except requests.exceptions.ConnectionError as err:
                raise RuntimeError(
                    "Gestalt Error: Gestalt couldn't connect to Vault")
            except Exception as err:
                raise RuntimeError(f"Gestalt Error: {err}")
            

            if secret_token['lease_id']: # dynamic secret from some secrets engine
                # needs to be stored and ttl renewed
                pass
            elif secret_token['data']['data']: # kv2 secrets engine
                self.__conf_data.update(secret_token['data']['data'])
                
            if secret_token['lease_id'] != '': 
                secret_lease = (secret_token['lease_id'],
                            secret_token['lease_duration'], time.time())
                self.secret_ttl_identifier.append(secret_lease)
                

    def ttl_expire_check(self) -> None:
        count = 0
        if os.environ.get("CI"):
            test_mode = True
        while (True):
            if test_mode and count == 5:   # For testing cases the thread will stop after 5 renewals
                break
            for lease in self.secret_ttl_identifier:    # Lease Renewal based 2/3 policy of vault
                if lease[2] - time.time() <= 0.667 * lease[1]:
                    print('Lease: ', lease[0])
                    renewed_lease = self.vault_client.sys.renew_lease(
                        lease_id=lease[0], increment=self.TTL_RENEW_INCREMENT)
                    lease[2] = renewed_lease["lease_duration"]
            if test_mode: count += 1
            time.sleep(1)
            