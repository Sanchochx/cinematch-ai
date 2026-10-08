"""Proveedor real: cliente async de la API v3 de TMDB."""

import logging
from typing import Any

import httpx

from providers.base import MovieSummary, ProviderSource
from providers.errors import (
    MovieNotFoundError,
    TmdbAuthError,
    TmdbRateLimitError,
    TmdbUnavailableError,
    UnknownGenreError,
)
from providers.genres import resolve_genre_id

logger = logging.getLogger(__name__)

HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_TOO_MANY_REQUESTS = 429

REDACTED = "***"
# Loggers que registran la URL completa de cada petición (incluido el parámetro api_key).
HTTP_LIBRARY_LOGGERS = ("httpx", "httpcore")


class _RedactSecretFilter(logging.Filter):
    """Sustituye un secreto por REDACTED en los mensajes de log."""

    def __init__(self, secret: str) -> None:
        super().__init__()
        self._secret = secret

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if self._secret in message:
            record.msg = message.replace(self._secret, REDACTED)
            record.args = None
        return True


def _release_year(release_date: str | None) -> int | None:
    # TMDB devuelve "" cuando no hay fecha de estreno.
    if release_date and release_date[:4].isdigit():
        return int(release_date[:4])
    return None


def _parse_retry_after(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return max(0, int(value))
    except ValueError:
        return None


class TmdbProvider:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str,
        timeout_seconds: float,
        language: str,
    ) -> None:
        self._language = language
        # id → nombre en `language`; se carga una vez y vive lo que el proceso.
        self._genres: dict[int, str] | None = None
        self._redact_filter = _RedactSecretFilter(api_key)
        for name in HTTP_LIBRARY_LOGGERS:
            logging.getLogger(name).addFilter(self._redact_filter)
        # Un único cliente para reutilizar conexiones durante toda la vida del proceso.
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout_seconds,
            params={"api_key": api_key},
        )

    @property
    def source(self) -> ProviderSource:
        return "tmdb"

    async def aclose(self) -> None:
        await self._client.aclose()
        for name in HTTP_LIBRARY_LOGGERS:
            logging.getLogger(name).removeFilter(self._redact_filter)

    async def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET a TMDB devolviendo el JSON o una excepción de dominio.

        Los errores se relanzan con `from None`: la excepción original de httpx contiene la
        URL de la petición, que incluye la API key, y no debe acabar en logs ni respuestas.
        """
        query = {"language": self._language, **(params or {})}
        try:
            response = await self._client.get(path, params=query)
        except httpx.TimeoutException:
            logger.warning("TMDB timeout on %s", path)
            raise TmdbUnavailableError() from None
        except httpx.HTTPError as exc:
            logger.warning("TMDB network error on %s: %s", path, type(exc).__name__)
            raise TmdbUnavailableError() from None

        status = response.status_code
        if status == HTTP_UNAUTHORIZED:
            raise TmdbAuthError()
        if status == HTTP_NOT_FOUND:
            raise MovieNotFoundError()
        if status == HTTP_TOO_MANY_REQUESTS:
            raise TmdbRateLimitError(_parse_retry_after(response.headers.get("Retry-After")))
        if status >= 400:
            # 5xx y cualquier otro 4xx inesperado: el agente solo necesita saber que falló.
            logger.warning("TMDB returned %s on %s", status, path)
            raise TmdbUnavailableError()

        try:
            return response.json()
        except ValueError:
            logger.warning("TMDB returned a non-JSON body on %s", path)
            raise TmdbUnavailableError() from None

    async def _genre_names(self) -> dict[int, str]:
        if self._genres is None:
            data = await self.get_json("/genre/movie/list")
            self._genres = {genre["id"]: genre["name"] for genre in data.get("genres", [])}
        return self._genres

    def _to_summary(self, item: dict[str, Any], genre_names: dict[int, str]) -> MovieSummary:
        return MovieSummary(
            id=item["id"],
            title=item.get("title", ""),
            release_year=_release_year(item.get("release_date")),
            overview=item.get("overview", ""),
            genres=[genre_names[gid] for gid in item.get("genre_ids", []) if gid in genre_names],
            vote_average=item.get("vote_average", 0.0),
            poster_path=item.get("poster_path"),
        )

    async def search_movies(
        self, *, genre: str | None, keyword: str | None, limit: int
    ) -> list[MovieSummary]:
        genre_names = await self._genre_names()
        genre_id: int | None = None
        if genre is not None:
            genre_id = resolve_genre_id(genre, genre_names)
            if genre_id is None:
                # Se falla antes de buscar nada: no se gasta una petición con un género inválido.
                raise UnknownGenreError(genre, sorted(genre_names.values()))

        if keyword is not None:
            data = await self.get_json("/search/movie", {"query": keyword})
        elif genre_id is not None:
            data = await self.get_json(
                "/discover/movie", {"with_genres": genre_id, "sort_by": "popularity.desc"}
            )
        else:
            data = await self.get_json("/movie/popular")

        items = data.get("results", [])
        if keyword is not None and genre_id is not None:
            # /search/movie no filtra por género, así que se hace aquí.
            items = [item for item in items if genre_id in item.get("genre_ids", [])]
        return [self._to_summary(item, genre_names) for item in items[:limit]]
