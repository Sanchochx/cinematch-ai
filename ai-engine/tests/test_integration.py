import os

import pytest

from mcp_client import McpClient, load_mcp_tools

URL = os.environ.get("MCP_INTEGRATION_URL")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not URL, reason="MCP_INTEGRATION_URL no definida"),
]


async def test_lists_real_tools():
    tools = await load_mcp_tools(McpClient(URL, timeout_seconds=10))
    assert {"search_movies", "get_movie_details"} <= {t.name for t in tools}
