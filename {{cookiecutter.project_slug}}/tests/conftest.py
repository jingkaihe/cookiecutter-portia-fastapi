"""Shared test configuration and fixtures."""

import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables for consistent testing."""
    # Store original environment
    original_env = dict(os.environ)
    
    # Set up test environment with minimal required variables
    test_env = {
        "OPENAI_API_KEY": "sk-test-dummy-key-for-testing",
        "DEBUG": "false",
        "LOG_LEVEL": "INFO",
        "PORTIA_LOG_LEVEL": "INFO",
        "PORTIA_STORAGE_CLASS": "MEMORY"
    }
    
    # Clear environment and set test values
    os.environ.clear()
    os.environ.update(test_env)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_no_api_key():
    """Mock environment with no API keys."""
    with patch.dict(os.environ, {}, clear=True):
        yield


@pytest.fixture
def mock_valid_api_key():
    """Mock environment with valid API key."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-valid-key"}, clear=True):
        yield


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require real API keys)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take longer to run)"
    )