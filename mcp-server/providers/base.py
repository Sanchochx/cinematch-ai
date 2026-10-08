"""Contrato común de los proveedores de películas (TMDB y mock).

Las tools dependen solo de estos tipos, nunca de una implementación concreta.
"""

from typing import Literal, Protocol, TypedDict

ProviderSource = Literal["tmdb", "mock"]


class MovieSummary(TypedDict):
    """Película en un listado (search_movies)."""

    id: int
    title: str
    release_year: int | None
    overview: str
    genres: list[str]
    vote_average: float
    poster_path: str | None  # ruta relativa de TMDB; el frontend elige el tamaño


class CastMember(TypedDict):
    name: str
    character: str


class MovieDetails(TypedDict):
    """Ficha completa de una película (get_movie_details)."""

    id: int
    title: str
    overview: str
    director: str | None
    cast: list[CastMember]
    runtime: int | None
    genres: list[str]
    release_date: str | None  # ISO 8601


class MovieProvider(Protocol):
    """Fuente de datos de películas.

    `source` se copia en cada respuesta de las tools para que el agente sepa si los datos
    son reales o mock. Las operaciones de consulta se añaden con cada tool.
    """

    async def search_movies(
        self, *, genre: str | None, keyword: str | None, limit: int
    ) -> list[MovieSummary]:
        """Películas que cumplen los filtros (todos opcionales), como máximo `limit`.

        Lanza `UnknownGenreError` si `genre` no existe. Sin filtros devuelve las populares.
        """
        ...

    async def get_movie_details(self, *, movie_id: int) -> MovieDetails:
        """Ficha completa de la película `movie_id` (id de TMDB).

        Lanza `MovieNotFoundError` si no existe.
        """
        ...

    @property
    def source(self) -> ProviderSource: ...

    async def aclose(self) -> None:
        """Libera los recursos del proveedor (conexiones HTTP)."""
        ...
