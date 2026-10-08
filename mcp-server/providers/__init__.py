"""Proveedores de datos de películas y selección según la configuración."""

import logging

from config import Settings
from providers.base import MovieProvider
from providers.mock import MockProvider
from providers.tmdb import TmdbProvider

logger = logging.getLogger(__name__)


def create_provider(settings: Settings) -> MovieProvider:
    """TmdbProvider si hay TMDB_API_KEY; si no, MockProvider para no bloquear el desarrollo."""
    if settings.tmdb_api_key:
        logger.info("TMDB provider enabled")
        return TmdbProvider(
            settings.tmdb_api_key,
            base_url=settings.tmdb_base_url,
            timeout_seconds=settings.tmdb_timeout_seconds,
            language=settings.tmdb_language,
        )
    logger.warning("TMDB_API_KEY not set — using mock data")
    return MockProvider()
