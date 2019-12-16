import pytest
from gestalt import gestalt

def test_loading_json():
    g = gestalt.Gestalt()
    g.add_config_path('./testdata')
    g.build_config()
    x = g.dump()
    assert len(x)

