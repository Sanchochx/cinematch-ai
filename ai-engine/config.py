"""Configuración del ai-engine leída de variables de entorno."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_MCP_SERVER_URL = "http://mcp-server:8000/mcp"
DEFAULT_MCP_TIMEOUT_SECONDS = 10.0


@dataclass(frozen=True)
class Settings:
    mcp_server_url: str = DEFAULT_MCP_SERVER_URL
    mcp_timeout_seconds: float = DEFAULT_MCP_TIMEOUT_SECONDS


def _parse_timeout(raw: str | None) -> float:
    if raw is None or not raw.strip():
        return DEFAULT_MCP_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"MCP_TIMEOUT_SECONDS debe ser un número, no {raw!r}") from None
    if value <= 0:
        raise ValueError("MCP_TIMEOUT_SECONDS debe ser mayor que 0")
    return value


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env
    url = (env.get("MCP_SERVER_URL") or "").strip() or DEFAULT_MCP_SERVER_URL
    return Settings(
        mcp_server_url=url,
        mcp_timeout_seconds=_parse_timeout(env.get("MCP_TIMEOUT_SECONDS")),
    )
