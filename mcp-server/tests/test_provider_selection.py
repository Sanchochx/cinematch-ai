import logging

import pytest

from config import load_settings
from providers import create_provider
from providers.mock import MockProvider
from providers.tmdb import TmdbProvider
from tests.conftest import FAKE_TMDB_API_KEY


async def test_api_key_present_uses_tmdb_provider(caplog):
    caplog.set_level(logging.INFO)

    provider = create_provider(load_settings({"TMDB_API_KEY": FAKE_TMDB_API_KEY}))
    try:
        assert isinstance(provider, TmdbProvider)
        assert provider.source == "tmdb"
        assert ("providers", logging.INFO, "TMDB provider enabled") in caplog.record_tuples
        assert FAKE_TMDB_API_KEY not in caplog.text
    finally:
        await provider.aclose()


@pytest.mark.parametrize("env", [{}, {"TMDB_API_KEY": ""}, {"TMDB_API_KEY": "   "}])
def test_missing_or_blank_api_key_uses_mock_provider(env, caplog):
    caplog.set_level(logging.INFO)

    provider = create_provider(load_settings(env))

    assert isinstance(provider, MockProvider)
    assert provider.source == "mock"
    assert (
        "providers",
        logging.WARNING,
        "TMDB_API_KEY not set — using mock data",
    ) in caplog.record_tuples
