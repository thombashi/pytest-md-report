import pytest


@pytest.mark.xfail()
def test_xfailed():
    assert False
