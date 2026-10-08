"""Excepciones de dominio de los proveedores de películas.

Sus mensajes se muestran tal cual al agente, así que nunca deben incluir la API key,
URLs de petición ni detalles internos.
"""


class MovieProviderError(Exception):
    """Base de todos los errores esperables de un proveedor."""

    default_message = "Error al consultar el proveedor de películas"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class TmdbAuthError(MovieProviderError):
    default_message = "credenciales de TMDB inválidas"


class MovieNotFoundError(MovieProviderError):
    default_message = "No se encontró la película solicitada"

    def __init__(self, movie_id: int | None = None) -> None:
        super().__init__(
            f"No se encontró la película con id {movie_id}" if movie_id is not None else None
        )


class TmdbRateLimitError(MovieProviderError):
    def __init__(self, retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        message = "Límite de peticiones de TMDB alcanzado"
        if retry_after is not None:
            message += f"; reintenta en {retry_after} s"
        super().__init__(message)


class TmdbUnavailableError(MovieProviderError):
    default_message = "TMDB no está disponible en este momento; inténtalo más tarde"


class UnknownGenreError(MovieProviderError):
    def __init__(self, genre: str, valid_genres: list[str]) -> None:
        self.valid_genres = valid_genres
        super().__init__(f"Género desconocido: {genre!r}. Géneros válidos: {', '.join(valid_genres)}")
