"""Tool `get_movie_details`: sinopsis, director y reparto de una película."""

from typing import Annotated, TypedDict

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from providers.base import MovieDetails, MovieProvider, ProviderSource
from tools import READ_ONLY
from tools.errors import handle_provider_errors


class GetMovieDetailsResult(TypedDict):
    source: ProviderSource
    movie: MovieDetails


def register_get_movie_details(mcp: FastMCP, provider: MovieProvider) -> None:
    @mcp.tool(annotations=READ_ONLY)
    @handle_provider_errors
    async def get_movie_details(
        # strict: "157336" o 157336.0 se rechazan en vez de coercionarse en silencio.
        movie_id: Annotated[
            int,
            Field(strict=True, gt=0, description="ID de TMDB de la película, el `id` que devuelve `search_movies`."),
        ],
    ) -> GetMovieDetailsResult:
        """Obtiene la ficha de una película para justificar una recomendación con datos concretos.

        Devuelve `source` ('tmdb' o 'mock') y `movie`: `id`, `title`, `overview` (sinopsis, vacía si
        no hay), `director` (varios separados por ', '; null si no consta), `cast` (hasta 5
        actores con `name` y `character`), `runtime` (minutos), `genres` (nombres) y
        `release_date` (ISO 8601). Si el id no existe, el error lo indica.
        """
        movie = await provider.get_movie_details(movie_id=movie_id)
        return GetMovieDetailsResult(source=provider.source, movie=movie)
