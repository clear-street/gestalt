import hvac

class VaultClient(hvac.Client):
    url: str = ""
    token: str = ""
    cert: tuple(str, str) = ("", "")
    verify: str = ""
    
    def __init__(self, vault_config):
        self.client = hvac.Client(vault_config)


    def __init__(self, url, token, cert, verify):
        self.client = hvac.Client(url, token, cert, verify)


    def auth(self, method_type, app_id, user_id, auth_params):
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
        elif method_type == "jwt" or method_type == "oidc":
            self.client.enable_auth_backend(
                method_type == method_type
            )
        elif method_type == "kubernetes" or method_type == "k8s":
            self.client.auth_kubernetes(auth_params)
        elif method_type == "ldap":
            self.client.auth_ldap(auth_params)
        elif method_type == "okta":
            if not auth_params.description or not auth_params.mount_point:
                raise """auth params are incorrect for okta. missing description or secret_path"""
            self.client.enable_secret_backend(
                backend_type='okta',
                description=auth_params.description,
                mount_point=auth_params.okta_secret_path
            )
        else:
            raise f"Unknown auth method {method_type}"

        self.client.login()