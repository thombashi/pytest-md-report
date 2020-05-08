import pytest


@pytest.mark.xfail()
def test_xfailed():
    assert False


class Test:
    @pytest.mark.xfail()
    def test_pass(self):
        assert False
