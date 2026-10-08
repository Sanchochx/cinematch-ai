"""Configuración del mcp-server leída de variables de entorno."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

TMDB_BASE_URL = "https://api.themoviedb.org/3"

DEFAULT_MCP_HOST = "0.0.0.0"
DEFAULT_MCP_PORT = 8000
DEFAULT_TMDB_TIMEOUT_SECONDS = 10.0
DEFAULT_TMDB_LANGUAGE = "es-ES"


@dataclass(frozen=True)
class Settings:
    # repr=False evita que la key aparezca si alguien loguea el objeto Settings.
    tmdb_api_key: str | None = field(default=None, repr=False)
    mcp_host: str = DEFAULT_MCP_HOST
    mcp_port: int = DEFAULT_MCP_PORT
    tmdb_timeout_seconds: float = DEFAULT_TMDB_TIMEOUT_SECONDS
    tmdb_language: str = DEFAULT_TMDB_LANGUAGE
    tmdb_base_url: str = TMDB_BASE_URL


def _clean(value: str | None) -> str | None:
    """Trata los valores vacíos o solo con espacios como ausentes."""
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_port(raw: str | None) -> int:
    if raw is None:
        return DEFAULT_MCP_PORT
    try:
        port = int(raw)
    except ValueError:
        raise ValueError(f"MCP_PORT debe ser un entero, no {raw!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"MCP_PORT fuera de rango (1-65535): {port}")
    return port


def _parse_timeout(raw: str | None) -> float:
    if raw is None:
        return DEFAULT_TMDB_TIMEOUT_SECONDS
    try:
        timeout = float(raw)
    except ValueError:
        raise ValueError(f"TMDB_TIMEOUT_SECONDS debe ser un número, no {raw!r}") from None
    if timeout <= 0:
        raise ValueError(f"TMDB_TIMEOUT_SECONDS debe ser mayor que 0: {timeout}")
    return timeout


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Construye Settings a partir del entorno (por defecto, os.environ)."""
    env = os.environ if env is None else env
    return Settings(
        tmdb_api_key=_clean(env.get("TMDB_API_KEY")),
        mcp_host=_clean(env.get("MCP_HOST")) or DEFAULT_MCP_HOST,
        mcp_port=_parse_port(_clean(env.get("MCP_PORT"))),
        tmdb_timeout_seconds=_parse_timeout(_clean(env.get("TMDB_TIMEOUT_SECONDS"))),
        tmdb_language=_clean(env.get("TMDB_LANGUAGE")) or DEFAULT_TMDB_LANGUAGE,
    )
