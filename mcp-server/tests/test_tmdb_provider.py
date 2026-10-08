import logging

import httpx
import pytest

from providers.errors import (
    MovieNotFoundError,
    TmdbAuthError,
    TmdbRateLimitError,
    TmdbUnavailableError,
)
from tests.conftest import FAKE_TMDB_API_KEY


async def test_success_returns_json_and_sends_key_and_language(tmdb_mock, tmdb_provider):
    route = tmdb_mock.get("/movie/157336").respond(200, json={"id": 157336})

    data = await tmdb_provider.get_json("/movie/157336", {"append_to_response": "credits"})

    assert data == {"id": 157336}
    params = route.calls.last.request.url.params
    assert params["api_key"] == FAKE_TMDB_API_KEY
    assert params["language"] == "es-ES"
    assert params["append_to_response"] == "credits"


async def test_reuses_a_single_client(tmdb_mock, tmdb_provider):
    tmdb_mock.get("/movie/popular").respond(200, json={})
    client = tmdb_provider._client

    await tmdb_provider.get_json("/movie/popular")
    await tmdb_provider.get_json("/movie/popular")

    assert tmdb_provider._client is client
    assert not client.is_closed


async def test_401_raises_auth_error(tmdb_mock, tmdb_provider):
    tmdb_mock.get("/movie/popular").respond(401, json={"status_message": "Invalid API key"})

    with pytest.raises(TmdbAuthError, match="credenciales de TMDB inválidas"):
        await tmdb_provider.get_json("/movie/popular")


async def test_404_raises_not_found(tmdb_mock, tmdb_provider):
    tmdb_mock.get("/movie/999999999").respond(404)

    with pytest.raises(MovieNotFoundError):
        await tmdb_provider.get_json("/movie/999999999")


async def test_429_includes_retry_after(tmdb_mock, tmdb_provider):
    tmdb_mock.get("/movie/popular").respond(429, headers={"Retry-After": "7"})

    with pytest.raises(TmdbRateLimitError, match="7 s") as exc_info:
        await tmdb_provider.get_json("/movie/popular")

    assert exc_info.value.retry_after == 7


@pytest.mark.parametrize("headers", [{}, {"Retry-After": "not-a-number"}])
async def test_429_without_usable_retry_after(tmdb_mock, tmdb_provider, headers):
    tmdb_mock.get("/movie/popular").respond(429, headers=headers)

    with pytest.raises(TmdbRateLimitError) as exc_info:
        await tmdb_provider.get_json("/movie/popular")

    assert exc_info.value.retry_after is None


@pytest.mark.parametrize("status", [500, 502, 503, 400])
async def test_server_and_unexpected_errors_raise_unavailable(tmdb_mock, tmdb_provider, status):
    tmdb_mock.get("/movie/popular").respond(status)

    with pytest.raises(TmdbUnavailableError):
        await tmdb_provider.get_json("/movie/popular")


@pytest.mark.parametrize(
    "error",
    [httpx.ReadTimeout("timed out"), httpx.ConnectError("connection refused")],
)
async def test_network_errors_raise_unavailable(tmdb_mock, tmdb_provider, error):
    tmdb_mock.get("/movie/popular").mock(side_effect=error)

    with pytest.raises(TmdbUnavailableError) as exc_info:
        await tmdb_provider.get_json("/movie/popular")

    # La excepción de httpx lleva la URL con la key: no debe quedar encadenada.
    assert exc_info.value.__cause__ is None
    assert exc_info.value.__suppress_context__


async def test_invalid_json_raises_unavailable(tmdb_mock, tmdb_provider):
    tmdb_mock.get("/movie/popular").respond(200, content=b"<html>oops</html>")

    with pytest.raises(TmdbUnavailableError):
        await tmdb_provider.get_json("/movie/popular")


@pytest.mark.parametrize(
    ("status", "headers"),
    [(401, {}), (404, {}), (429, {"Retry-After": "3"}), (500, {})],
)
async def test_api_key_never_leaks_in_errors_or_logs(tmdb_mock, tmdb_provider, caplog, status, headers):
    caplog.set_level(logging.DEBUG)
    tmdb_mock.get("/movie/popular").respond(status, headers=headers)

    with pytest.raises(Exception) as exc_info:
        await tmdb_provider.get_json("/movie/popular")

    assert FAKE_TMDB_API_KEY not in str(exc_info.value)
    assert FAKE_TMDB_API_KEY not in caplog.text


async def test_closing_the_provider_closes_the_client(tmdb_provider):
    await tmdb_provider.aclose()

    assert tmdb_provider._client.is_closed
