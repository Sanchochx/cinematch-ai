"""Entrypoint del mcp-server: `python main.py`."""

import asyncio
import logging

from config import load_settings
from providers import create_provider
from server import create_server

LOG_FORMAT = "%(levelname)-7s %(name)s: %(message)s"


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    # Una línea de log por petición a TMDB es ruido; TmdbProvider además redacta la API key.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


async def serve() -> None:
    settings = load_settings()
    provider = create_provider(settings)
    mcp = create_server(settings, provider)
    try:
        await mcp.run_streamable_http_async()
    finally:
        await provider.aclose()


def main() -> None:
    configure_logging()
    asyncio.run(serve())


if __name__ == "__main__":
    main()
