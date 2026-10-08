"""Cliente MCP por Streamable HTTP contra el mcp-server (ADR-001)."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client

from mcp_client.errors import McpConnectionError


class McpClient:
    """Abre una sesión MCP corta por operación.

    Sin sesión persistente: el servidor es stateless y así un reinicio del mcp-server
    no deja al agente con una conexión rota.
    """

    def __init__(self, url: str, timeout_seconds: float) -> None:
        self._url = url
        self._timeout = timeout_seconds

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[ClientSession]:
        # Las respuestas SSE son de larga duración: el límite de lectura lo impone _run con asyncio.timeout.
        async with httpx.AsyncClient(timeout=httpx.Timeout(self._timeout, read=None)) as http:
            async with streamable_http_client(self._url, http_client=http) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session

    async def _run(self, operation: Any) -> Any:
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session() as session:
                    return await operation(session)
        except McpConnectionError:
            raise
        except TimeoutError:
            raise McpConnectionError(
                f"Timeout de {self._timeout}s al contactar el servidor MCP"
            ) from None
        except Exception as exc:  # incluye ExceptionGroup de anyio y errores de httpx
            raise McpConnectionError(
                f"No se pudo contactar el servidor MCP: {type(exc).__name__}"
            ) from exc

    async def list_tools(self) -> list[types.Tool]:
        result = await self._run(lambda session: session.list_tools())
        return list(result.tools)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        return await self._run(lambda session: session.call_tool(name, arguments))
