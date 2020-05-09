import pytest


def test_skipped():
    pytest.skip()


class Test:
    def test_skipped(self):
        pytest.skip()
