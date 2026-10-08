# Fixtures compartidas de los tests del mcp-server.
# Las llamadas a TMDB se mockean siempre con respx; nunca se usa la API real.
from collections.abc import AsyncIterator

import pytest
import respx

from config import TMDB_BASE_URL, Settings
from providers.tmdb import TmdbProvider

FAKE_TMDB_API_KEY = "test-secret-key-0123456789"


@pytest.fixture
def settings() -> Settings:
    return Settings(tmdb_api_key=None, mcp_host="127.0.0.1", mcp_port=8000)


@pytest.fixture
def tmdb_mock() -> respx.MockRouter:
    with respx.mock(base_url=TMDB_BASE_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
async def tmdb_provider(tmdb_mock: respx.MockRouter) -> AsyncIterator[TmdbProvider]:
    provider = TmdbProvider(
        FAKE_TMDB_API_KEY,
        base_url=TMDB_BASE_URL,
        timeout_seconds=1,
        language="es-ES",
    )
    yield provider
    await provider.aclose()
