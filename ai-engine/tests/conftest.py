# Fixtures compartidas. El mcp-server se simula a nivel HTTP con respx; nunca se usa la red real.
import json

import httpx
import pytest
import respx

MCP_URL = "http://mcp-server:8000/mcp"

SEARCH_TOOL = {
    "name": "search_movies",
    "description": "Busca películas por texto.",
    "inputSchema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}


def _rpc(request_id: object, result: dict) -> httpx.Response:
    return httpx.Response(200, json={"jsonrpc": "2.0", "id": request_id, "result": result})


class FakeMcpServer:
    """Responde JSON-RPC de MCP sobre Streamable HTTP (modo JSON, sin SSE)."""

    def __init__(self, tools: list[dict], call_result: dict | None = None) -> None:
        self.tools = tools
        self.call_result = call_result or {"content": [{"type": "text", "text": "ok"}]}
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        method, params = body.get("method"), body.get("params") or {}
        if "id" not in body:  # notificación (initialized)
            return httpx.Response(202)
        if method == "initialize":
            return _rpc(body["id"], {
                "protocolVersion": params.get("protocolVersion"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fake", "version": "0"},
            })
        if method == "tools/list":
            return _rpc(body["id"], {"tools": self.tools})
        if method == "tools/call":
            self.calls.append((params["name"], params.get("arguments", {})))
            return _rpc(body["id"], self.call_result)
        return httpx.Response(400)


@pytest.fixture
def mcp_router() -> respx.MockRouter:
    with respx.mock(assert_all_called=False) as router:
        router.get(MCP_URL).respond(405)
        router.delete(MCP_URL).respond(405)
        yield router


@pytest.fixture
def fake_server(mcp_router: respx.MockRouter) -> FakeMcpServer:
    server = FakeMcpServer([SEARCH_TOOL])
    mcp_router.post(MCP_URL).mock(side_effect=server)
    return server
