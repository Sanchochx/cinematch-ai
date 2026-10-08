import asyncio
import socket
from collections.abc import AsyncIterator

import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from starlette.routing import Route

from config import Settings
from providers.mock import MockProvider
from server import MCP_PATH, SERVER_NAME, create_server


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
async def running_server() -> AsyncIterator[str]:
    """Arranca el servidor real (Streamable HTTP) en un puerto libre de localhost."""
    settings = Settings(mcp_host="127.0.0.1", mcp_port=free_port())
    mcp = create_server(settings, MockProvider())
    config = uvicorn.Config(
        mcp.streamable_http_app(),
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.01)
    yield f"http://{settings.mcp_host}:{settings.mcp_port}{MCP_PATH}"
    server.should_exit = True
    await task


def test_server_uses_configured_name_host_and_port():
    mcp = create_server(Settings(mcp_host="0.0.0.0", mcp_port=8123), MockProvider())

    assert mcp.name == SERVER_NAME == "cinematch-mcp"
    assert mcp.settings.host == "0.0.0.0"
    assert mcp.settings.port == 8123
    assert mcp.settings.streamable_http_path == MCP_PATH == "/mcp"


def test_only_the_mcp_endpoint_is_exposed(settings):
    app = create_server(settings, MockProvider()).streamable_http_app()

    assert [route.path for route in app.routes if isinstance(route, Route)] == [MCP_PATH]
    assert len(app.routes) == 1


async def test_all_registered_tools_are_read_only(settings):
    mcp = create_server(settings, MockProvider())

    for tool in await mcp.list_tools():
        assert tool.annotations is not None and tool.annotations.readOnlyHint, tool.name


async def test_mcp_client_completes_initialize_handshake(running_server):
    async with streamable_http_client(running_server) as (read, write, _):
        async with ClientSession(read, write) as session:
            result = await session.initialize()

    assert result.serverInfo.name == SERVER_NAME
