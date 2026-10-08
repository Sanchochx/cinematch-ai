# Agente con LLM y tools falsos: ninguna llamada de red.
from typing import Any

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import StructuredTool

from agent import LlmError, build_graph, create_llm, run_agent
from agent.prompts import FALLBACK_MESSAGE, SYSTEM_PROMPT
from config import Settings


class ScriptedLLM(BaseChatModel):
    """Devuelve las respuestas de `script` en orden (la última se repite) y registra las entradas."""

    script: list[AIMessage]
    seen: list[list[BaseMessage]] = []
    error: Exception | None = None

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedLLM":
        return self

    def _generate(self, messages: list[BaseMessage], stop: Any = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        if self.error:
            raise self.error
        self.seen.append(list(messages))
        index = min(len(self.seen) - 1, len(self.script) - 1)
        return ChatResult(generations=[ChatGeneration(message=self.script[index])])


def tool_call(name: str = "search_movies", call_id: str = "c1", **args: Any) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args or {"query": "x"}, "id": call_id}])


def make_tool(result: str = "Matrix (1999)", fail: bool = False) -> StructuredTool:
    calls: list[dict] = []

    async def search_movies(query: str) -> str:
        calls.append({"query": query})
        if fail:
            raise RuntimeError("TMDB caído")
        return result

    tool = StructuredTool.from_function(coroutine=search_movies, name="search_movies", description="Busca películas")
    tool.metadata = {"calls": calls}
    return tool


def llm_with(*script: AIMessage) -> ScriptedLLM:
    return ScriptedLLM(script=list(script), seen=[])


async def test_sin_tools_para_un_saludo():
    llm, tool = llm_with(AIMessage("¡Hola! ¿Qué te apetece ver?")), make_tool()
    answer = await run_agent(build_graph(llm, [tool]), "hola")
    assert answer == "¡Hola! ¿Qué te apetece ver?"
    assert tool.metadata["calls"] == []
    assert len(llm.seen) == 1


async def test_una_tool_y_su_resultado_vuelve_al_llm():
    llm, tool = llm_with(tool_call(query="ciencia ficción"), AIMessage("Te recomiendo Matrix.")), make_tool()
    answer = await run_agent(build_graph(llm, [tool]), "recomiéndame sci-fi")
    assert answer == "Te recomiendo Matrix."
    assert tool.metadata["calls"] == [{"query": "ciencia ficción"}]
    tool_messages = [m for m in llm.seen[1] if isinstance(m, ToolMessage)]
    assert [m.content for m in tool_messages] == ["Matrix (1999)"]


async def test_dos_iteraciones_de_tools():
    llm = llm_with(tool_call(call_id="a"), tool_call(call_id="b", query="y"), AIMessage("Listo."))
    tool = make_tool()
    assert await run_agent(build_graph(llm, [tool]), "busca") == "Listo."
    assert len(tool.metadata["calls"]) == 2


async def test_limite_de_iteraciones_devuelve_degradacion():
    llm = llm_with(tool_call())  # pide tool para siempre
    answer = await run_agent(build_graph(llm, [make_tool()]), "busca")
    assert answer == FALLBACK_MESSAGE


async def test_error_de_tool_llega_al_llm_sin_romper_el_grafo():
    llm = llm_with(tool_call(), AIMessage("Lo siento, falló la búsqueda."))
    answer = await run_agent(build_graph(llm, [make_tool(fail=True)]), "busca")
    assert answer == "Lo siento, falló la búsqueda."
    tool_message = next(m for m in llm.seen[1] if isinstance(m, ToolMessage))
    assert tool_message.status == "error"
    assert "TMDB caído" in tool_message.content


async def test_error_del_llm_se_traduce_a_llm_error_sin_filtrar_la_clave():
    llm = llm_with(AIMessage("x"))
    llm.error = RuntimeError("Incorrect API key provided: sk-secret-123")
    with pytest.raises(LlmError) as info:
        await run_agent(build_graph(llm, []), "hola")
    assert "sk-secret-123" not in str(info.value)
    assert info.value.__cause__ is None and info.value.__suppress_context__


async def test_system_prompt_y_historial_se_envian_al_llm():
    llm = llm_with(AIMessage("ok"))
    history = [HumanMessage("hola"), AIMessage("hola"), HumanMessage("algo de terror")]
    await run_agent(build_graph(llm, []), history)
    assert llm.seen[0][0].content == SYSTEM_PROMPT
    assert llm.seen[0][1:] == history


def test_system_prompt_cubre_las_reglas():
    for fragment in ("mismo idioma", "SOLO", "No inventes"):
        assert fragment in SYSTEM_PROMPT


def test_create_llm_sin_clave_lanza_llm_error():
    with pytest.raises(LlmError):
        create_llm(Settings())


def test_settings_no_expone_la_clave_en_repr():
    assert "sk-secret" not in repr(Settings(openai_api_key="sk-secret"))
