"""Conversión de excepciones en errores MCP legibles para el agente."""

import functools
import logging
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from mcp.server.fastmcp.exceptions import ToolError

from providers.errors import MovieProviderError

logger = logging.getLogger(__name__)

UNEXPECTED_ERROR_MESSAGE = "Error interno del servidor de películas; inténtalo de nuevo más tarde"

P = ParamSpec("P")
R = TypeVar("R")


def handle_provider_errors(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Decora una tool para que sus errores lleguen al agente como ToolError sin stack trace.

    Los errores de dominio ya traen un mensaje seguro. Cualquier otro se registra en el log
    del servidor y se sustituye por un mensaje genérico, porque su texto podría filtrar
    detalles internos.
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except ToolError:
            raise
        except MovieProviderError as exc:
            raise ToolError(str(exc)) from None
        except Exception:
            logger.exception("Unexpected error in tool %s", func.__name__)
            raise ToolError(UNEXPECTED_ERROR_MESSAGE) from None

    return wrapper
