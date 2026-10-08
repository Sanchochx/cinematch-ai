"""Construcción del servidor MCP de CineMatch."""

from mcp.server.fastmcp import FastMCP

from config import Settings
from providers.base import MovieProvider
from tools.search_movies import register_search_movies

SERVER_NAME = "cinematch-mcp"
MCP_PATH = "/mcp"

SERVER_INSTRUCTIONS = (
    "Herramientas de solo lectura para consultar películas de TMDB. "
    "Cada respuesta incluye `source` ('tmdb' o 'mock') para indicar el origen de los datos."
)


def create_server(settings: Settings, provider: MovieProvider) -> FastMCP:
    """Crea la instancia FastMCP con transporte Streamable HTTP en MCP_PATH.

    Las tools reciben `provider` al registrarse; el servidor no expone rutas HTTP propias
    fuera del endpoint MCP.
    """
    mcp = FastMCP(
        SERVER_NAME,
        instructions=SERVER_INSTRUCTIONS,
        host=settings.mcp_host,
        port=settings.mcp_port,
        streamable_http_path=MCP_PATH,
    )
    register_search_movies(mcp, provider)
    return mcp
