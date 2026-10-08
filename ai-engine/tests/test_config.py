import pytest

from config import DEFAULT_MCP_SERVER_URL, DEFAULT_MCP_TIMEOUT_SECONDS, load_settings


def test_defaults():
    s = load_settings({})
    assert s.mcp_server_url == DEFAULT_MCP_SERVER_URL == "http://mcp-server:8000/mcp"
    assert s.mcp_timeout_seconds == DEFAULT_MCP_TIMEOUT_SECONDS


def test_env_overrides_and_blank_is_ignored():
    s = load_settings({"MCP_SERVER_URL": "http://x:1/mcp", "MCP_TIMEOUT_SECONDS": "2.5"})
    assert (s.mcp_server_url, s.mcp_timeout_seconds) == ("http://x:1/mcp", 2.5)
    assert load_settings({"MCP_SERVER_URL": "  "}).mcp_server_url == DEFAULT_MCP_SERVER_URL


@pytest.mark.parametrize("raw", ["abc", "0", "-1"])
def test_invalid_timeout(raw):
    with pytest.raises(ValueError):
        load_settings({"MCP_TIMEOUT_SECONDS": raw})


def test_llm_defaults_y_overrides():
    from config import DEFAULT_LLM_MODEL, load_settings

    assert load_settings({}).llm_model == DEFAULT_LLM_MODEL
    assert load_settings({}).openai_api_key == ""
    settings = load_settings({"OPENAI_API_KEY": " k ", "LLM_MODEL": "gpt-x"})
    assert (settings.openai_api_key, settings.llm_model) == ("k", "gpt-x")
