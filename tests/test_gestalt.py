# type: ignore

import pytest
import os
import gestalt
import hvac
import requests


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
    g = gestalt.Gestalt()
    client_config = gestalt.HVAC_ClientConfig()
    client_config['url'] = ""
    client_config['token'] = "myroot"
    client_config['cert'] = None
    client_config['verify'] = True
    g.add_vault_config_provider(client_config, auth_config=None)
    assert g.vault_client.is_authenticated()


def test_vault_fail_setup():
    g = gestalt.Gestalt()
    client_config = gestalt.HVAC_ClientConfig()
    client_config['url'] = "failed_url"
    client_config['token'] = "random_token"
    client_config['cert'] = None
    client_config['verify'] = True
    g.add_vault_config_provider(client_config, auth_config=None)
    with pytest.raises(requests.exceptions.MissingSchema):
        g.vault_client.is_authenticated()


def test_vault_fail_kubernetes_auth():
    g = gestalt.Gestalt()
    client_config = gestalt.HVAC_ClientConfig()
    client_config = gestalt.HVAC_ClientConfig()
    client_config['url'] = ""
    client_config['token'] = ""
    client_config['cert'] = None
    client_config['verify'] = True
    auth_config = gestalt.HVAC_ClientAuthentication()
    auth_config['role'] = "random_role"
    auth_config['jwt'] = "random_jwt"
    with pytest.raises(hvac.exceptions.InvalidRequest):
        g.add_vault_config_provider(client_config, auth_config)


def test_vault_get():
    g = gestalt.Gestalt()
    g.build_config()
    client_config = gestalt.HVAC_ClientConfig()
    client_config['url'] = ""
    client_config['token'] = "myroot"
    client_config['cert'] = None
    client_config['verify'] = True
    g.add_vault_config_provider(client_config, auth_config=None)
    print("Requires the user to set a token in the client")
    CLIENT_ID = "test_client"
    g.add_vault_secret_path("test")
    g.fetch_vault_secrets()
    secret = g.get_string(CLIENT_ID)
    assert secret == 'test_client_password'
