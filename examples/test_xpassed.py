import pytest


@pytest.mark.xfail()
def test_xpassed():
    assert True


class Test:
    @pytest.mark.xfail()
    def test_xpassed(self):
        assert True
