"""Conversión de tools MCP a tools de LangChain."""

import json
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from mcp import types

from mcp_client.client import McpClient
from mcp_client.errors import McpConnectionError


def _result_to_text(result: types.CallToolResult) -> str:
    parts = [block.text for block in result.content if isinstance(block, types.TextContent)]
    if not parts and result.structuredContent is not None:
        parts.append(json.dumps(result.structuredContent, ensure_ascii=False))
    text = "\n".join(parts) or "(sin contenido)"
    return f"Error de la tool: {text}" if result.isError else text


def _to_langchain_tool(client: McpClient, tool: types.Tool) -> BaseTool:
    async def invoke(**kwargs: Any) -> str:
        # Un fallo de transporte se devuelve al LLM como texto para que el grafo no se rompa.
        try:
            result = await client.call_tool(tool.name, kwargs)
        except McpConnectionError as exc:
            return f"Error de la tool: {exc}"
        return _result_to_text(result)

    return StructuredTool(
        name=tool.name,
        description=tool.description or tool.name,
        args_schema=tool.inputSchema,
        coroutine=invoke,
    )


async def load_mcp_tools(client: McpClient) -> list[BaseTool]:
    """Descubre las tools del mcp-server en tiempo de ejecución."""
    return [_to_langchain_tool(client, tool) for tool in await client.list_tools()]
