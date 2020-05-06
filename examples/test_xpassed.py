import pytest


@pytest.mark.xfail()
def test_xpassed():
    assert True
