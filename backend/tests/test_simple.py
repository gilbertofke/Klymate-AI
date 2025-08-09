import pytest

def test_simple():
    """A simple test to verify pytest is working."""
    assert True

@pytest.mark.skip(reason="Basic API structure implementation in progress")
def test_another():
    """Another test that we'll implement later."""
    assert True
