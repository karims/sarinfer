# src/sarinfer/tests/test_auth.py

import pytest
from sarinfer.api.auth import validate_api_key, check_auth
from sarinfer.utils.errors import ERROR_INVALID_API_KEY

# Sample valid and invalid API keys for testing
VALID_API_KEYS = ["valid_key_1", "valid_key_2"]
INVALID_API_KEY = "invalid_key"

# Mock environment variable for valid API keys (this would normally be loaded from env)
@pytest.fixture(autouse=True)
def mock_valid_api_keys(monkeypatch):
    """
    This fixture automatically sets a mock environment variable for valid API keys
    using the monkeypatch feature of pytest.
    """
    monkeypatch.setenv("VALID_API_KEYS", ",".join(VALID_API_KEYS))

# Test valid API key
def test_validate_api_key_valid():
    for valid_key in VALID_API_KEYS:
        assert validate_api_key(valid_key) == True

# Test invalid API key
def test_validate_api_key_invalid():
    with pytest.raises(PermissionError) as exc_info:
        validate_api_key(INVALID_API_KEY)
    assert str(exc_info.value) == ERROR_INVALID_API_KEY

# Test check_auth with valid API key
def test_check_auth_valid():
    for valid_key in VALID_API_KEYS:
        # Ensure no exceptions are raised with valid keys
        assert check_auth(valid_key) is None

# Test check_auth with invalid API key
def test_check_auth_invalid():
    with pytest.raises(PermissionError) as exc_info:
        check_auth(INVALID_API_KEY)
    assert str(exc_info.value) == ERROR_INVALID_API_KEY

# Test when no API key is provided
def test_validate_api_key_missing(monkeypatch):
    # Simulate no API key provided
    monkeypatch.setenv("VALID_API_KEYS", "")  # Empty env variable
    with pytest.raises(PermissionError) as exc_info:
        validate_api_key("some_key")
    assert str(exc_info.value) == ERROR_INVALID_API_KEY
