import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from agent import LlmError
from mcp_client import McpConnectionError

logger = logging.getLogger("ai_engine.api")


def _handler(status: int, detail: str):
    async def handle(request: Request, exc: Exception) -> JSONResponse:
        # Solo el tipo: el mensaje puede contener URLs internas o fragmentos de credenciales.
        logger.error("%s en %s %s", type(exc).__name__, request.method, request.url.path)
        return JSONResponse({"detail": detail}, status_code=status)

    return handle


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(McpConnectionError, _handler(503, "Servicio de películas no disponible"))
    app.add_exception_handler(LlmError, _handler(502, "El modelo de lenguaje no está disponible"))
    app.add_exception_handler(Exception, _handler(500, "Error interno"))
