"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


class TestSettings:
    """Test the Settings class."""

    def test_settings_defaults(self):
        """Test default settings values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.app_name == "{{ cookiecutter.project_name }}"
            assert settings.app_version == "{{ cookiecutter.version }}"
            assert settings.debug is False
            assert settings.host == "0.0.0.0"
            assert settings.port == {{ cookiecutter.port }}
            assert settings.log_level == "INFO"

    def test_settings_from_env(self):
        """Test settings loading from environment variables."""
        env_vars = {
            "DEBUG": "true",
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "LOG_LEVEL": "DEBUG",
            "OPENAI_API_KEY": "test-key"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.debug is True
            assert settings.host == "127.0.0.1"
            assert settings.port == 9000
            assert settings.log_level == "DEBUG"
            assert settings.openai_api_key == "test-key"

    def test_has_llm_api_key_openai(self):
        """Test LLM API key detection for OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            settings = Settings()
            assert settings.has_llm_api_key() is True

    def test_has_llm_api_key_anthropic(self):
        """Test LLM API key detection for Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
            settings = Settings()
            assert settings.has_llm_api_key() is True

    def test_has_llm_api_key_none(self):
        """Test LLM API key detection when no key is set."""
        # Create a completely clean environment
        clean_env = {}
        with patch.dict(os.environ, clean_env, clear=True):
            # Use pydantic settings config to ignore .env file for this test
            from pydantic_settings import SettingsConfigDict
            
            class TestSettings(Settings):
                model_config = SettingsConfigDict(
                    env_file=None,  # Don't load from .env file
                    case_sensitive=False,
                    extra="ignore",
                )
            
            settings = TestSettings()
            assert settings.has_llm_api_key() is False

    def test_get_portia_storage_class_memory(self):
        """Test getting Portia storage class - memory."""
        with patch.dict(os.environ, {"PORTIA_STORAGE_CLASS": "MEMORY"}, clear=True):
            settings = Settings()
            from portia.config import StorageClass
            assert settings.get_portia_storage_class() == StorageClass.MEMORY

    def test_get_portia_storage_class_disk(self):
        """Test getting Portia storage class - disk."""
        with patch.dict(os.environ, {"PORTIA_STORAGE_CLASS": "DISK"}, clear=True):
            settings = Settings()
            from portia.config import StorageClass
            assert settings.get_portia_storage_class() == StorageClass.DISK

    def test_get_portia_storage_class_invalid(self):
        """Test getting Portia storage class with invalid value."""
        with patch.dict(os.environ, {"PORTIA_STORAGE_CLASS": "INVALID"}, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_portia_log_level_conversion(self):
        """Test Portia log level conversion."""
        with patch.dict(os.environ, {"PORTIA_LOG_LEVEL": "DEBUG"}, clear=True):
            settings = Settings()
            from portia.config import LogLevel
            assert settings.portia_log_level == LogLevel.DEBUG

    def test_settings_validation_invalid_port(self):
        """Test settings validation with invalid port."""
        with patch.dict(os.environ, {"PORT": "99999"}, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_validation_invalid_log_level(self):
        """Test settings validation with invalid log level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}, clear=True):
            with pytest.raises(ValidationError):
                Settings()


class TestGetSettings:
    """Test the get_settings function."""

    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_get_settings_with_env_change(self):
        """Test get_settings behavior when environment changes."""
        # Clear any cached settings
        get_settings.cache_clear()
        
        with patch.dict(os.environ, {"DEBUG": "false"}, clear=True):
            settings1 = get_settings()
            assert settings1.debug is False
        
        # Note: In practice, environment changes during runtime
        # don't affect cached settings unless cache is cleared
        # This is expected behavior for production applications