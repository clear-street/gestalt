# type: ignore

from gestalt.vault import Vault
import datetime


def test_get(mount_setup):
    mount_setup_path = "test-mount/data/test"
    key = "test_mount"
    filter_ = f".{key}"
    expected = "test_mount_password"
    vault = Vault()
    result = vault.get(key=key, path=mount_setup_path, filter=filter_)
    assert result == expected


def test_get_cache_hit(mock_db_role_request):
    mount_setup_path = "test-mount/data/test"
    key = "password"
    filter_ = f".{key}"
    expected = "foo"
    expected_expiry_time = datetime.datetime(2023, 5, 31, 14, 24, 41)
    vault = Vault()
    result_one = vault.get(key=key, path=mount_setup_path, filter=filter_)
    result_two = vault.get(key=key, path=mount_setup_path, filter=filter_)
    assert result_one == expected and result_two == expected
    assert vault._secret_expiry_times[key] == expected_expiry_time
    assert vault._secret_values[key] == expected

