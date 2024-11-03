# src/sarinfer/api/auth.py

import os
from functools import lru_cache

from sarinfer.utils.errors import ERROR_INVALID_API_KEY


@lru_cache()
def get_valid_api_keys():
    """
    Fetch the valid API keys from environment variables only once.
    Use caching to avoid reading the environment multiple times.
    """
    return os.getenv("VALID_API_KEYS", "your_default_key").split(",")

def validate_api_key(api_key: str):
    """
    Validate the API key against the cached list of valid API keys.
    """
    valid_keys = get_valid_api_keys()
    if api_key in valid_keys:
        return True
    else:
        raise PermissionError(ERROR_INVALID_API_KEY)

def check_auth(api_key: str):
    """
    Wrapper function to validate the API key.
    """
    validate_api_key(api_key)
