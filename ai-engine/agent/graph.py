from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from pydantic import SecretStr

from agent.errors import LlmError
from agent.nodes import make_agent_node, route_after_agent
from agent.prompts import FALLBACK_MESSAGE
from agent.state import AgentState
from config import Settings

MAX_TOOL_ITERATIONS = 6
# Cada iteración consume dos pasos del grafo (agent + tools); +1 para el agent final.
RECURSION_LIMIT = MAX_TOOL_ITERATIONS * 2 + 1


def create_llm(settings: Settings) -> ChatOpenAI:
    if not settings.openai_api_key:
        raise LlmError("OPENAI_API_KEY no está configurada")
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=SecretStr(settings.openai_api_key),
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
    )


def build_graph(llm: Any, tools: Sequence[BaseTool]) -> CompiledStateGraph:
    """Bucle ReAct: agent → (tools → agent)* → END. Dependencias inyectadas para testear sin red."""
    graph = StateGraph(AgentState)
    graph.add_node("agent", make_agent_node(llm.bind_tools(list(tools))))
    # handle_tool_errors=True: una excepción de tool llega al LLM como ToolMessage, no rompe el grafo.
    graph.add_node("tools", ToolNode(list(tools), handle_tool_errors=True))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", route_after_agent, {"tools": "tools", "__end__": END})
    graph.add_edge("tools", "agent")
    return graph.compile()


def _text(message: AnyMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block if isinstance(block, str) else block.get("text", "")
        for block in content
        if isinstance(block, (str, dict))
    )


async def run_agent(graph: CompiledStateGraph, messages: str | Sequence[AnyMessage]) -> str:
    """Ejecuta el agente y devuelve el texto final. Lanza `LlmError` si falla el LLM."""
    history = [HumanMessage(messages)] if isinstance(messages, str) else list(messages)
    try:
        result = await graph.ainvoke({"messages": history}, {"recursion_limit": RECURSION_LIMIT})
    except GraphRecursionError:
        return FALLBACK_MESSAGE
    last = result["messages"][-1]
    return _text(last) if isinstance(last, AIMessage) else FALLBACK_MESSAGE
