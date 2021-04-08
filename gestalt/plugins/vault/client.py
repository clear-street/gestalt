import os
import hvac  # type: ignore
from typing import AnyStr, Dict, Any, Union


class VaultClient(hvac.Client):  # type: ignore
    """VaultClient is a wrapper library that builds on top of hvac
    """
    url: str = ""
    token: str = ""
    cert: str = ""
    verify: str = ""

    def __init__(self,
                 url: str = os.environ['VAULT_ADDR'],
                 token: str = os.environ['VAULT_TOKEN']) -> None:
        """Initializes a hvac client

        Args:
            url (str): URL for the VAULT Address
            token (str): token for the VAULT cluster
        """
        self.client = hvac.Client(url=url, token=token)

    def auth(self, method_type: str, app_id: str, user_id: str,
             auth_params: Dict[Any, Any]) -> None:
        """Authentication for the vault client, also logins the client into the Vault cluster

        Args:
            method_type (str): authentication type  
            app_id (str): app_id for the app
            user_id (str): user_id for the 
            auth_params (Dict[Any, Any]): authentication params specific to the method type
        """
        self.client.auth_app_id(app_id=app_id, user_id=user_id)
        if method_type == "approle":
            self.client.auth_approle(auth_params)
        elif method_type == "aws":
            self.client.auth_aws_iam(auth_params)
        elif method_type == "azure":
            self.client.enable_auth_backend(auth_params)
        elif method_type == "gcp":
            self.client.auth_gcp(auth_params)
        elif method_type == "github":
            self.client.auth_github(auth_params)
        elif method_type == "jwt":
            self.client.enable_auth_backend(method_type == "jwt")
        elif method_type == "oidc":
            self.client.enable_auth_backend(method_type == "oidc")
        elif method_type == "kubernetes" or method_type == "k8s":
            self.client.auth_kubernetes(auth_params)
        elif method_type == "ldap":
            self.client.auth_ldap(auth_params)
        elif method_type == "okta":
            if not auth_params.description or not auth_params.mount_point:  # type: ignore
                raise BaseException(
                    "auth params are incorrect for okta. missing description or secret_path"
                )
            self.client.enable_secret_backend(
                backend_type='okta',
                description=auth_params.description,  # type: ignore
                mount_point=auth_params.okta_secret_path  # type: ignore
            )
        else:
            raise BaseException(f"Unknown auth method {method_type}")

        self.client.login()