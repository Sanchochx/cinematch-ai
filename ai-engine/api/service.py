import asyncio
from collections.abc import Awaitable, Callable

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from agent import run_agent
from api.schemas import ChatRequest

GraphFactory = Callable[[], Awaitable[CompiledStateGraph]]


def to_messages(request: ChatRequest) -> list[AnyMessage]:
    history: list[AnyMessage] = [
        HumanMessage(item.content) if item.role == "user" else AIMessage(item.content)
        for item in request.history
    ]
    return [*history, HumanMessage(request.message)]


class ChatService:
    """Envuelve `run_agent`. El grafo se construye en la primera petición y se reutiliza.

    La construcción es perezosa porque descubrir las tools exige al mcp-server: si estuviera
    caído al arrancar, el ai-engine seguiría vivo (`/health` ok) y respondería 503 hasta que vuelva.
    """

    def __init__(self, graph_factory: GraphFactory) -> None:
        self._factory = graph_factory
        self._graph: CompiledStateGraph | None = None
        self._lock = asyncio.Lock()

    async def _get_graph(self) -> CompiledStateGraph:
        async with self._lock:
            if self._graph is None:
                self._graph = await self._factory()
            return self._graph

    async def chat(self, request: ChatRequest) -> str:
        return await run_agent(await self._get_graph(), to_messages(request))
