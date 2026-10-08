import pytest

from config import (
    DEFAULT_MCP_HOST,
    DEFAULT_MCP_PORT,
    DEFAULT_TMDB_LANGUAGE,
    DEFAULT_TMDB_TIMEOUT_SECONDS,
    load_settings,
)
from tests.conftest import FAKE_TMDB_API_KEY


def test_defaults_when_env_is_empty():
    settings = load_settings({})

    assert settings.tmdb_api_key is None
    assert settings.mcp_host == DEFAULT_MCP_HOST == "0.0.0.0"
    assert settings.mcp_port == DEFAULT_MCP_PORT == 8000
    assert settings.tmdb_timeout_seconds == DEFAULT_TMDB_TIMEOUT_SECONDS == 10
    assert settings.tmdb_language == DEFAULT_TMDB_LANGUAGE == "es-ES"


def test_reads_api_key_and_strips_spaces():
    settings = load_settings({"TMDB_API_KEY": f"  {FAKE_TMDB_API_KEY}\n"})

    assert settings.tmdb_api_key == FAKE_TMDB_API_KEY


@pytest.mark.parametrize("raw", ["", "   ", "\t\n"])
def test_blank_api_key_is_treated_as_missing(raw):
    assert load_settings({"TMDB_API_KEY": raw}).tmdb_api_key is None


def test_reads_overrides():
    settings = load_settings(
        {
            "MCP_HOST": "127.0.0.1",
            "MCP_PORT": "9001",
            "TMDB_TIMEOUT_SECONDS": "2.5",
            "TMDB_LANGUAGE": "en-US",
        }
    )

    assert settings.mcp_host == "127.0.0.1"
    assert settings.mcp_port == 9001
    assert settings.tmdb_timeout_seconds == 2.5
    assert settings.tmdb_language == "en-US"


@pytest.mark.parametrize("raw", ["abc", "0", "70000"])
def test_invalid_port_raises(raw):
    with pytest.raises(ValueError, match="MCP_PORT"):
        load_settings({"MCP_PORT": raw})


@pytest.mark.parametrize("raw", ["abc", "0", "-1"])
def test_invalid_timeout_raises(raw):
    with pytest.raises(ValueError, match="TMDB_TIMEOUT_SECONDS"):
        load_settings({"TMDB_TIMEOUT_SECONDS": raw})


def test_repr_does_not_leak_api_key():
    settings = load_settings({"TMDB_API_KEY": FAKE_TMDB_API_KEY})

    assert FAKE_TMDB_API_KEY not in repr(settings)
