from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session

from providers.errors import (
    MovieNotFoundError,
    TmdbAuthError,
    TmdbRateLimitError,
    TmdbUnavailableError,
)
from tools.errors import UNEXPECTED_ERROR_MESSAGE, handle_provider_errors


def build_server_raising(error: Exception) -> FastMCP:
    mcp = FastMCP("test")

    @mcp.tool()
    @handle_provider_errors
    async def failing_tool(movie_id: int) -> dict:
        raise error

    return mcp


async def call_failing_tool(error: Exception):
    async with create_connected_server_and_client_session(build_server_raising(error)) as client:
        return await client.call_tool("failing_tool", {"movie_id": 1})


async def test_wrapped_tool_keeps_its_parameters_schema():
    async with create_connected_server_and_client_session(build_server_raising(ValueError())) as client:
        tools = (await client.list_tools()).tools

    assert tools[0].inputSchema["required"] == ["movie_id"]


async def test_domain_errors_reach_the_agent_with_their_message():
    for error, expected in [
        (TmdbAuthError(), "credenciales de TMDB inválidas"),
        (MovieNotFoundError("No se encontró la película con id 1"), "No se encontró la película con id 1"),
        (TmdbRateLimitError(5), "reintenta en 5 s"),
        (TmdbUnavailableError(), "TMDB no está disponible"),
    ]:
        result = await call_failing_tool(error)

        assert result.isError
        text = result.content[0].text
        assert expected in text
        assert "Traceback" not in text


async def test_unexpected_errors_are_replaced_by_a_generic_message():
    secret_detail = "https://api.themoviedb.org/3/movie/1?api_key=secret"

    result = await call_failing_tool(RuntimeError(secret_detail))

    assert result.isError
    text = result.content[0].text
    assert UNEXPECTED_ERROR_MESSAGE in text
    assert secret_detail not in text
    assert "Traceback" not in text
