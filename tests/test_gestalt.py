# type: ignore

import json
from gestalt.plugins import vault
import pytest
import hvac
import os
import gestalt
from unittest.mock import MagicMock
from unittest import TestCase
from gestalt import remote_provider
from gestalt.plugins.vault import VaultConfigProvider


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


# Testing Configuration Provider and Remote Provider
def test_register_config_provider():
    g = gestalt.Gestalt()
    vaultProvider = VaultConfigProvider({})
    g.register_config_provider('vault', vaultProvider)
    receivedProvider = g.config_provider_registry.config_providers['vault']
    assert receivedProvider == vaultProvider


def test_add_remote_provider():
    g = gestalt.Gestalt()
    rp = remote_provider.RemoteProvider("rp", "ep", "path")
    g.add_remote_provider("rp", "ep", "path")
    assert rp.__dict__ == g.get_remote_providers()[0].__dict__ 


def test_read_remote_config():
    g = gestalt.Gestalt()
    data = { 'user' : '123' }
    vault_provider = MagicMock()
    vault_provider.Get.return_value = data
    g.register_config_provider("vault", vault_provider)
    g.add_remote_provider("vault", "something", "service")
    g.read_remote_config()
    secret = g.dump()
    assert data == json.loads(secret)

def test_read_remote_config_not_found():
    g = gestalt.Gestalt()
    vault_provider = MagicMock()
    VaultError = hvac.exceptions.VaultError('', '', '')
    return_err = hvac.exceptions.InvalidRequest(VaultError)
    vault_provider.Get.side_effect = hvac.exceptions.InvalidRequest(VaultError)
    g.register_config_provider("vault", vault_provider)
    g.add_remote_provider("vault", "something", "service")
    try:
        g.read_remote_config()
    except Exception as err:
        assert str(err) == str(return_err)