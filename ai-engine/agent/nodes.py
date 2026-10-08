from collections.abc import Awaitable, Callable
from typing import Any

from langchain_core.messages import AIMessage, SystemMessage

from agent.errors import LlmError
from agent.prompts import SYSTEM_PROMPT
from agent.state import AgentState


def make_agent_node(llm: Any) -> Callable[[AgentState], Awaitable[dict[str, list[AIMessage]]]]:
    """Nodo `agent`: invoca el LLM (ya con tools enlazadas) con system prompt + historial."""

    async def agent(state: AgentState) -> dict[str, list[AIMessage]]:
        try:
            response = await llm.ainvoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])
        except Exception as exc:
            # Solo el tipo de excepción: el mensaje del SDK puede incluir fragmentos de la API key.
            raise LlmError(f"Fallo del LLM: {type(exc).__name__}") from None
        return {"messages": [response]}

    return agent


def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    return "tools" if isinstance(last, AIMessage) and last.tool_calls else "__end__"


