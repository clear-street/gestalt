# type: ignore

from unittest.mock import patch, Mock

from gestalt.vault import Vault
from gestalt import merge_into
import pytest
import os
import gestalt
import hvac
from queue import Queue


# Testing member function
def test_merge_into():
    combine1 = {}
    combine2 = {}
    combine3 = {"local": 1234, "pg": {"host": "dict1_pg", "pass": "dict1_pg"}}
    combine4 = {"local": 1234, "pg": {"host": "dict2_pg"}}

    merge_into(combine3, combine1)
    merge_into(combine4, combine1)

    merge_into(combine4, combine2)
    merge_into(combine3, combine2)

    assert combine1 == {
        "local": 1234,
        "pg": {
            "host": "dict2_pg",
            "pass": "dict1_pg"
        }
    }

    assert combine2 == {
        "local": 1234,
        "pg": {
            "host": "dict1_pg",
            "pass": "dict1_pg"
        }
    }


def test_combine_into_empty_dict():
    combine = {}
    merge_into({}, combine)
    assert combine == {}

    combine = {"local": 1234}
    merge_into({}, combine)
    assert combine == {"local": 1234}


# Testing JSON Loading
def test_loading_json():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    x = g.dump()
    assert len(x)


def test_loading_json_file():
    g = gestalt.Gestalt()
    g.add_config_file('./tests/testdata/testjson.json')
    g.build_config()
    x = g.dump()
    assert len(x)


def test_loading_file_dir():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_file('./tests/testdata')
        assert 'is not a file' in terr


def test_loading_file_nonexist():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_file('./tests/testdata/nothere.yaml')
        g.build_config()
        assert 'is not a file' in terr


def test_loading_file_bad_yaml():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_file('./tests/testdatabad/testyaml.yaml')
        g.build_config()
        assert terr.type is ValueError
        assert 'but cannot be read as such' in terr.value.args[0]


def test_loading_file_bad_json():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_file('./tests/testdatabad/testjson.json')
        g.build_config()
        assert terr.type is ValueError
        assert 'but cannot be read as such' in terr.value.args[0]


def test_loading_dir_bad_files():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_path('./tests/testdatabad')
        g.build_config()
        assert terr.type is ValueError
        assert 'but cannot be read as such' in terr.value.args[0]


def test_loading_dir_bad_files_yaml_only():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_path('./tests/testdatabadyaml')
        g.build_config()
        assert terr.type is ValueError
        assert 'but cannot be read as such' in terr.value.args[0]


def test_loading_yaml_file():
    g = gestalt.Gestalt()
    g.add_config_file('./tests/testdata/testyaml.yaml')
    g.build_config()
    x = g.dump()
    assert len(x)


def test_loading_json_nonexist_dir():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_path('./nonexistpath')
        assert 'does not exist' in terr


def test_loading_json_file_not_dir():
    g = gestalt.Gestalt()
    with pytest.raises(ValueError) as terr:
        g.add_config_path('./setup.py')
        assert 'is not a directory' in terr


def test_get_wrong_type():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    with pytest.raises(TypeError) as terr:
        g.get_string('numbers')
        assert 'is not of type' in terr


def test_get_non_exist_key():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    with pytest.raises(ValueError) as terr:
        g.get_string('non-exist')
        assert 'is not in any configuration and no default is provided' in terr


def test_get_key_wrong_type():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    with pytest.raises(TypeError) as terr:
        g.get_string(1234)
        assert 'is not of string type' in terr


def test_get_key_wrong_default_type():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    with pytest.raises(TypeError) as terr:
        g.get_string('nonexist', 1234)
        assert 'Provided default is of incorrect type' in terr


def test_get_json_string():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_string('yarn')
    assert testval == 'blue skies'


def test_get_json_default_string():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_string('nonexist', 'mydefval')
    assert testval == 'mydefval'


def test_get_json_set_default_string():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    g.set_default_string('nonexisttest', 'otherdefval')
    testval = g.get_string('nonexisttest')
    assert testval == 'otherdefval'


def test_get_json_int():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_int('numbers')
    assert testval == 12345678


def test_get_json_float():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_float('strangenumbers')
    assert testval == 123.456


def test_get_json_bool():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_bool('truthy')
    assert testval is True


def test_get_json_list():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_list('listing')
    assert testval
    assert 'dog' in testval
    assert 'cat' in testval


def test_get_json_nested():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_string('deep.nested1')
    assert testval == 'hello'


def test_get_yaml_nested():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_string('deep_yaml.nest1.nest2.foo')
    assert testval == 'hello'


# Test Set Overriding
def test_set_string():
    g = gestalt.Gestalt()
    g.set_string('mykey', 'myval')
    testval = g.get_string('mykey')
    assert testval == 'myval'


def test_set_int():
    g = gestalt.Gestalt()
    g.set_int('mykey', 1234)
    testval = g.get_int('mykey')
    assert testval == 1234


def test_set_float():
    g = gestalt.Gestalt()
    g.set_float('mykey', 45.23)
    testval = g.get_float('mykey')
    assert testval == 45.23


def test_set_bool():
    g = gestalt.Gestalt()
    g.set_bool('mykey', False)
    testval = g.get_bool('mykey')
    assert testval is False


def test_set_list():
    g = gestalt.Gestalt()
    g.set_list('mykey', ['hi', 'bye'])
    testval = g.get_list('mykey')
    assert testval
    assert 'hi' in testval
    assert 'bye' in testval


def test_set_int_get_bad():
    g = gestalt.Gestalt()
    g.set_int('mykey', 1234)
    with pytest.raises(TypeError) as terr:
        g.get_string('mykey')
        assert 'Given set key is not of type' in terr


def test_set_bad_key_type():
    g = gestalt.Gestalt()
    with pytest.raises(TypeError) as terr:
        g.set_string(1234, 'myval')
        assert 'is not of string type' in terr


def test_set_bad_type():
    g = gestalt.Gestalt()
    with pytest.raises(TypeError) as terr:
        g.set_string('mykey', 123)
        assert 'is not of type' in terr


def test_re_set_bad_type():
    g = gestalt.Gestalt()
    g.set_string('mykey', '123')
    with pytest.raises(TypeError) as terr:
        g.set_int('mykey', 123)
        assert 'Overriding key' in terr


def test_set_override():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    testval = g.get_int('numbers')
    assert testval == 12345678
    g.set_int('numbers', 6543)
    testval = g.get_int('numbers')
    assert testval == 6543


def test_set_bad_type_file_config():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    with pytest.raises(TypeError) as terr:
        g.set_string('numbers', 'notgood')
        assert 'File config has' in terr


def test_set_bad_type_default_config():
    g = gestalt.Gestalt()
    g.set_default_string('mykey', 'mystring')
    with pytest.raises(TypeError) as terr:
        g.set_int('mykey', 123)
        assert 'Default config has' in terr


# Test Env Variables
def test_get_env_string():
    g = gestalt.Gestalt()
    g.auto_env()
    os.environ['MYKEY'] = 'myval'
    testval = g.get_string('mykey')
    assert testval == 'myval'


def test_get_env_int():
    g = gestalt.Gestalt()
    g.auto_env()
    os.environ['MYKEY'] = '999'
    testval = g.get_int('mykey')
    assert testval == 999


def test_get_nested_env_string():
    g = gestalt.Gestalt()
    g.auto_env()
    os.environ['MY_KEY'] = 'myval'
    testval = g.get_string('my.key')
    assert testval == 'myval'


def test_get_env_bad_type():
    g = gestalt.Gestalt()
    g.auto_env()
    os.environ['MY_KEY'] = 'myval'
    with pytest.raises(TypeError) as terr:
        g.get_int('my.key')
        assert "could not be converted to type" in terr


# Test Default Values
def test_set_default_string():
    g = gestalt.Gestalt()
    g.set_default_string('mykey', 'myval')
    testval = g.get_string('mykey')
    assert testval == 'myval'


def test_set_default_int():
    g = gestalt.Gestalt()
    g.set_default_int('mykey', 1234)
    testval = g.get_int('mykey')
    assert testval == 1234


def test_set_default_float():
    g = gestalt.Gestalt()
    g.set_default_float('mykey', 1234.05)
    testval = g.get_float('mykey')
    assert testval == 1234.05


def test_set_default_bool():
    g = gestalt.Gestalt()
    g.set_default_bool('mykey', False)
    testval = g.get_bool('mykey')
    assert testval is False


def test_set_default_list():
    g = gestalt.Gestalt()
    g.set_default_list('mykey', ['bear', 'bull'])
    testval = g.get_list('mykey')
    assert testval
    assert 'bear' in testval
    assert 'bull' in testval


def test_set_default_int_get_bad():
    g = gestalt.Gestalt()
    g.set_default_int('mykey', 1234)
    with pytest.raises(TypeError) as terr:
        g.get_string('mykey')
        assert 'Given default set key is not of type' in terr


def test_set_default_string_bad_key():
    g = gestalt.Gestalt()
    with pytest.raises(TypeError) as terr:
        g.set_default_string(1234, 'myval')
        assert 'Given key is not of string type' in terr


def test_set_default_string_bad_val():
    g = gestalt.Gestalt()
    with pytest.raises(TypeError) as terr:
        g.set_default_string('mykey', 123)
        assert 'Input value when setting default' in terr


def test_set_default_string_bad_val_override():
    g = gestalt.Gestalt()
    with pytest.raises(TypeError) as terr:
        g.set_default_string('mykey', 'myval')
        g.set_default_int('mykey', 1234)
        assert 'Overriding default key' in terr


def test_override_nested_config():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testoverride/')
    g.build_config()
    assert g.get_int("local") == 123456
    assert g.get_string("nested1.nested2") == "final"
    assert g.get_string("pg.host") == "dev_host"
    assert g.get_string("pg.pass") == "def_pass"
    assert g.get_string("nested1.nested3.nested4.deeplevel") == "nested5"


def test_set_default_bad_type_file_config():
    g = gestalt.Gestalt()
    g.add_config_path('./tests/testdata')
    g.build_config()
    with pytest.raises(TypeError) as terr:
        g.set_default_string('numbers', 'notgood')
        assert 'File config has' in terr


def test_set_default_bad_type_set_config():
    g = gestalt.Gestalt()
    g.set_string('mykey', 'mystring')
    with pytest.raises(TypeError) as terr:
        g.set_default_int('mykey', 123)
        assert 'Set config has' in terr


def test_vault_setup():
    vault = Vault(role=None, jwt=None)
    assert vault.vault_client.is_authenticated() is True


def test_vault_interpolation(secret_setup):
    g = gestalt.Gestalt()
    g.add_config_file("./tests/testvault/testcorrect.json")
    vault = Vault(role=None, jwt=None)
    g.configure_provider("vault", vault)
    g.build_config()
    secret = g.get_string("test_secret.test_secret")
    assert secret == "test_secret_password"


def test_vault_mount_path(mount_setup):
    g = gestalt.Gestalt()
    g.add_config_file("./tests/testvault/testmount.json")
    g.configure_provider("vault", Vault(role=None, jwt=None))
    g.build_config()
    secret = g.get_string("test_mount.test_mount")
    assert secret == "test_mount_password"


def test_vault_incorrect_path(mount_setup):
    g = gestalt.Gestalt()
    g.add_config_file("./tests/testvault/testincorrectmount.json")
    g.configure_provider("vault", Vault(role=None, jwt=None))
    with pytest.raises(RuntimeError):
        g.build_config()
        g.get_string("test_mount")


def test_nest_key_for_vault(nested_setup, secret_setup):
    g = gestalt.Gestalt()
    g.add_config_file("./tests/testvault/testnested.json")
    g.configure_provider("vault", Vault(role=None, jwt=None))
    g.build_config()
    secret_db = g.get_string("remoteAPI.database.test_secret")
    secret_slack = g.get_string("remoteAPI.slack.token")
    assert secret_db == "test_secret_password"
    assert secret_slack == "random-token"


def test_read_no_nest_db_role(mock_db_role_request):
    g = gestalt.Gestalt()
    g.add_config_file("./tests/testvault/testsfdynamic.json")
    g.configure_provider("vault", Vault(role=None, jwt=None))
    g.build_config()
    secret_username = g.get_string("username")
    assert secret_username == "foo"


def test_set_vault_key(nested_setup):
    g = gestalt.Gestalt()
    g.configure_provider("vault", Vault(role=None, jwt=None))
    g.set_string(key="test",
                 value="ref+vault://secret/data/testnested#.slack.token")
    g.build_config()
    secret = g.get_string("test")
    assert secret == "ref+vault://secret/data/testnested#.slack.token"


def test_vault_worker_dynamic(mock_vault_workers, mock_vault_k8s_auth):
    mock_dynamic_renew, mock_k8s_renew = mock_vault_workers

    mock_sleep = None

    def except_once(self, **kwargs):
        # side effect used to exit the worker loop after one call
        if mock_sleep.call_count == 1:
            raise hvac.exceptions.VaultError("some error")

    with patch("gestalt.vault.sleep", side_effect=except_once,
               autospec=True) as mock_sleep:

        with patch("gestalt.vault.hvac.Client") as mock_client:
            v = Vault(role="test-role", jwt="test-jwt")

            mock_k8s_renew.start.assert_called()

            test_token_queue = Queue(maxsize=0)
            test_token_queue.put(("dynamic", 1, 100))

            with pytest.raises(RuntimeError):
                v.worker(test_token_queue)

            mock_sleep.assert_called()
            mock_client().sys.renew_lease.assert_called()
            mock_k8s_renew.start.assert_called_once()

            mock_dynamic_renew.stop()
            mock_k8s_renew.stop()


def test_vault_worker_k8s(mock_vault_workers):
    mock_dynamic_renew, mock_k8s_renew = mock_vault_workers

    mock_sleep = None

    def except_once(self, **kwargs):
        # side effect used to exit the worker loop after one call
        if mock_sleep.call_count == 1:
            raise hvac.exceptions.VaultError("some error")

    with patch("gestalt.vault.sleep", side_effect=except_once,
               autospec=True) as mock_sleep:
        with patch("gestalt.vault.hvac.Client") as mock_client:
            v = Vault(role="test-role", jwt="test-jwt")

            mock_k8s_renew.start.assert_called()

            test_token_queue = Queue(maxsize=0)
            test_token_queue.put(("kubernetes", 1, 100))

            with pytest.raises(RuntimeError):
                v.worker(test_token_queue)

            mock_sleep.assert_called()
            mock_client().auth.token.renew.assert_called()
            mock_k8s_renew.start.assert_called_once()

            mock_dynamic_renew.stop()
            mock_k8s_renew.stop()


def test_vault_start_dynamic_lease(mock_vault_workers):
    mock_response = {
        "lease_id": "1",
        "lease_duration": 5,
        "data": {
            "data": "mock_data"
        }
    }

    mock_vault_client_patch = patch("gestalt.vault.hvac.Client.read",
                                    return_value=mock_response)
    with mock_vault_client_patch as mock_vault_client_read:
        mock_dynamic_token_queue = Mock()
        mock_kube_token_queue = Mock()
        with patch(
                "gestalt.vault.queue.Queue",
                side_effect=[mock_dynamic_token_queue,
                             mock_kube_token_queue]) as mock_queues:

            v = Vault(role=None, jwt=None)
            g = gestalt.Gestalt()
            g.add_config_file("./tests/testvault/testmount.json")
            g.configure_provider("vault", v)
            g.build_config()
            g.get_string("test_mount")

            mock_vault_client_read.assert_called()
            mock_dynamic_token_queue.put_nowait.assert_called()

            mock_vault_client_read.stop()
            mock_dynamic_token_queue.stop()
            mock_kube_token_queue.stop()
            mock_queues.stop()
            mock_vault_client_read.stop()
