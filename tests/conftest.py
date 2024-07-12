from unittest.mock import patch, Mock
import pytest
import hvac
import os
import requests


class MockSession(requests.Session):
    def request(self, *_, **__):
        resp = {
            "request_id": "230f5e67-e55d-bdae-bd24-c7bc13c1a3e9",
            "lease_id": "",
            "renewable": False,
            "lease_duration": 0,
            "data": {
                "last_vault_rotation": "2023-05-31T14:24:41.724285249Z",
                "password": "foo",
                "rotation_period": 60,
                "ttl": 0,
                "username": "foo",
            },
            "wrap_info": None,
            "warnings": None,
            "auth": None,
        }
        return MockResponse(resp, 200)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = True

    def json(self):
        return self.json_data


@pytest.fixture
def mock_db_role_request(mocker):
    mocker.patch("requests.Session", MockSession)


@pytest.fixture(scope="function")
def secret_setup():
    client = hvac.Client()
    client.secrets.kv.v2.create_or_update_secret(
        path="test", secret=dict(test_secret="test_secret_password"))


@pytest.fixture(scope="function")
def incorrect_env_setup():
    os.environ["VAULT_ADDR"] = ""


@pytest.fixture(scope="function")
def mount_setup():
    client = hvac.Client()
    secret_engines_list = client.sys.list_mounted_secrets_engines(
    )["data"].keys()
    if "test-mount/" in secret_engines_list:
        client.sys.disable_secrets_engine(path="test-mount")
    client.sys.enable_secrets_engine(backend_type="kv", path="test-mount")
    client.secrets.kv.v2.create_or_update_secret(
        mount_point="test-mount",
        path="test",
        secret=dict(test_mount="test_mount_password\\$"),
    )


@pytest.fixture(scope="function")
def nested_setup():
    client = hvac.Client()
    client.secrets.kv.v2.create_or_update_secret(
        path="testnested", secret=dict(slack={"token": "random-token"}))


@pytest.fixture
def mock_vault_workers():
    mock_dynamic_renew = Mock()
    mock_k8s_renew = Mock()
    with patch("gestalt.vault.Thread",
               side_effect=[mock_dynamic_renew, mock_k8s_renew]):
        yield (mock_dynamic_renew, mock_k8s_renew)


@pytest.fixture
def mock_vault_k8s_auth(mocker):
    mocker.patch("gestalt.vault.hvac.api.auth_methods.Kubernetes")
