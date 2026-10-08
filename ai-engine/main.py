import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.graph.state import CompiledStateGraph

from agent import build_graph, create_llm
from api.errors import register_error_handlers
from api.routes import router
from api.service import ChatService
from config import Settings, load_settings
from mcp_client import McpClient, load_mcp_tools

logging.basicConfig(level=logging.INFO)


def _graph_factory(settings: Settings):
    async def build() -> CompiledStateGraph:
        client = McpClient(settings.mcp_server_url, settings.mcp_timeout_seconds)
        return build_graph(create_llm(settings), await load_mcp_tools(client))

    return build


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.chat_service = ChatService(_graph_factory(settings))
        yield

    # /docs solo con ENABLE_DOCS=true; el servicio no se expone al host en cualquier caso.
    docs = {} if settings.enable_docs else {"docs_url": None, "redoc_url": None, "openapi_url": None}
    app = FastAPI(title="CineMatch AI Engine", lifespan=lifespan, **docs)
    register_error_handlers(app)
    app.include_router(router)
    return app


app = create_app()
