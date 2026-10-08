import httpx
import pytest
import respx

from config import load_settings
from mcp_client import McpClient, McpConnectionError, load_mcp_tools
from tests.conftest import MCP_URL, FakeMcpServer


@pytest.fixture
def client() -> McpClient:
    return McpClient(MCP_URL, timeout_seconds=2)


async def test_discovers_tools_dynamically(fake_server, client):
    tools = await load_mcp_tools(client)
    assert [t.name for t in tools] == ["search_movies"]
    assert tools[0].description == "Busca películas por texto."
    assert tools[0].args_schema["required"] == ["query"]


async def test_tool_call_returns_text(fake_server, client):
    fake_server.call_result = {"content": [{"type": "text", "text": "Interstellar"}]}
    (tool,) = await load_mcp_tools(client)
    assert await tool.ainvoke({"query": "space"}) == "Interstellar"
    assert fake_server.calls == [("search_movies", {"query": "space"})]


async def test_is_error_becomes_readable_text(fake_server, client):
    fake_server.call_result = {"content": [{"type": "text", "text": "TMDB caído"}], "isError": True}
    (tool,) = await load_mcp_tools(client)
    assert await tool.ainvoke({"query": "x"}) == "Error de la tool: TMDB caído"


async def test_structured_content_fallback(fake_server, client):
    fake_server.call_result = {"content": [], "structuredContent": {"results": [1]}}
    (tool,) = await load_mcp_tools(client)
    assert await tool.ainvoke({"query": "x"}) == '{"results": [1]}'


async def test_server_down_raises_connection_error(mcp_router, client):
    mcp_router.post(MCP_URL).mock(side_effect=httpx.ConnectError("refused"))
    with pytest.raises(McpConnectionError):
        await client.list_tools()


async def test_http_500_raises_connection_error(mcp_router, client):
    mcp_router.post(MCP_URL).respond(500)
    with pytest.raises(McpConnectionError):
        await client.list_tools()


async def test_timeout_raises_connection_error(mcp_router):
    import asyncio

    async def slow(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(5)
        return httpx.Response(200)

    mcp_router.post(MCP_URL).mock(side_effect=slow)
    with pytest.raises(McpConnectionError, match="Timeout"):
        await McpClient(MCP_URL, timeout_seconds=0.2).list_tools()


async def test_transport_failure_during_call_is_returned_to_llm(mcp_router, client):
    server = FakeMcpServer([{"name": "t", "inputSchema": {"type": "object"}}])
    mcp_router.post(MCP_URL).mock(side_effect=server)
    (tool,) = await load_mcp_tools(client)
    mcp_router.post(MCP_URL).mock(side_effect=httpx.ConnectError("down"))
    assert (await tool.ainvoke({})).startswith("Error de la tool:")


def test_default_url_comes_from_settings():
    assert load_settings({}).mcp_server_url == "http://mcp-server:8000/mcp"
