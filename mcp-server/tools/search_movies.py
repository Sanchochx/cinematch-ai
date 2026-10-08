"""Tool `search_movies`: candidatas por género y/o palabra clave."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import Field
from typing_extensions import TypedDict

from providers.base import MovieProvider, MovieSummary, ProviderSource
from tools import READ_ONLY
from tools.errors import handle_provider_errors

MAX_KEYWORD_LENGTH = 100
DEFAULT_LIMIT = 10
MAX_LIMIT = 20


class SearchMoviesResult(TypedDict):
    source: ProviderSource
    results: list[MovieSummary]


def register_search_movies(mcp: FastMCP, provider: MovieProvider) -> None:
    @mcp.tool(annotations=READ_ONLY)
    @handle_provider_errors
    async def search_movies(
        genre: Annotated[
            str | None,
            Field(description="Nombre del género, en español o inglés (p. ej. 'ciencia ficción', 'Horror')."),
        ] = None,
        keyword: Annotated[
            str | None,
            Field(max_length=MAX_KEYWORD_LENGTH, description="Texto libre: título o palabra clave."),
        ] = None,
        limit: Annotated[
            int, Field(ge=1, le=MAX_LIMIT, description="Máximo de resultados (1-20).")
        ] = DEFAULT_LIMIT,
    ) -> SearchMoviesResult:
        """Busca películas por género y/o palabra clave para reunir candidatas a recomendar.

        Combinaciones: sin parámetros devuelve las populares; solo `genre` las más populares del
        género; solo `keyword` las que coinciden con el texto; ambos, las que coinciden con el
        texto y además son del género. Si el género no existe, el error lista los válidos.

        Devuelve `source` ('tmdb' o 'mock') y `results`: lista de películas con `id`, `title`,
        `release_year`, `overview`, `genres` (nombres), `vote_average` y `poster_path`.
        Una lista vacía significa que no hay coincidencias, no que haya un fallo.
        """
        if keyword is not None and not keyword.strip():
            raise ToolError("`keyword` no puede estar vacío; omítelo para buscar sin texto")
        if genre is not None and not genre.strip():
            raise ToolError("`genre` no puede estar vacío; omítelo para buscar sin filtrar por género")
        results = await provider.search_movies(
            genre=genre.strip() if genre else None,
            keyword=keyword.strip() if keyword else None,
            limit=limit,
        )
        return SearchMoviesResult(source=provider.source, results=results)
