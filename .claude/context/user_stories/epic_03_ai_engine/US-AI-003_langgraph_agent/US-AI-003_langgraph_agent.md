# US-AI-003: Agente LangGraph (razonar → tools → responder)

**Épica:** 03 — AI Engine
**Prioridad:** CRÍTICA
**Estimación:** 8 pts
**Dependencias:** US-AI-002

## Historia de usuario
**Como** usuario de CineMatch,
**quiero** que el agente entienda mi mensaje, consulte datos reales de películas cuando haga falta y
me devuelva una recomendación,
**para** recibir sugerencias fundamentadas y no inventadas.

## Contexto técnico
- Grafo: `langgraph.graph.StateGraph` con estado tipado (`TypedDict`) cuyo campo `messages` usa el
  reductor `add_messages`.
- Nodos mínimos:
  - `agent`: invoca el LLM (`ChatOpenAI(...).bind_tools(tools)`) con el system prompt + historial.
  - `tools`: ejecuta las tool calls pedidas por el LLM (`ToolNode` o equivalente).
  - Arista condicional tras `agent`: si el último mensaje trae `tool_calls` → `tools`; si no → `END`.
  - Arista `tools` → `agent` (bucle ReAct).
- Estructura propuesta: `ai-engine/agent/` (`state.py`, `nodes.py`, `graph.py`, `prompts.py`) con
  una factoría `build_graph(llm, tools)` para inyectar dependencias y poder testear sin red.
- Configuración: `OPENAI_API_KEY` (ver "Puntos a validar" del README), `LLM_MODEL` (default a
  definir en el ADR), temperatura baja.
- Registrar ADR en `docs/decisions/` con la elección de proveedor/modelo y de LangGraph sin
  checkpointer.

## Criterios de aceptación
- [x] El grafo compila y expone un punto de entrada async (p. ej. `run_agent(messages) -> str`)
  que recibe el historial/prompt del usuario y devuelve el texto final de la recomendación.
- [x] Con una pregunta que no requiere datos (p. ej. saludo), el grafo termina sin llamar a tools.
- [x] Con una petición de recomendación, el LLM emite tool calls, se ejecutan vía el cliente MCP
  (US-AI-002) y sus resultados vuelven al LLM antes de la respuesta final.
- [x] El system prompt (en `prompts.py`) instruye: responder en el idioma del usuario, basar las
  recomendaciones **solo** en resultados de las tools, y no inventar títulos/datos si las tools no
  devuelven nada.
- [x] Límite de iteraciones del bucle agente↔tools (`recursion_limit` o contador, p. ej. 6) para
  evitar bucles infinitos; al excederlo se devuelve una respuesta de degradación controlada.
- [x] Error de una tool no rompe el grafo: el LLM recibe el error y puede reintentar o disculparse.
- [x] Error del LLM (auth, rate limit, timeout) se traduce a una excepción propia
  (`LlmError`) sin filtrar la API key en el mensaje ni en logs.
- [x] La API key se lee solo del entorno; no existe en código, tests ni logs.
- [x] Tests con LLM falso (`GenericFakeChatModel` o similar) y tools falsas, sin red: camino sin
  tools, camino con una tool, camino con dos iteraciones, límite de iteraciones, error de tool.
- [x] ADR registrado en `docs/decisions/` (proveedor de LLM, modelo por defecto, sin checkpointer).

## Fuera de alcance
- Persistencia de conversaciones / checkpointer (decisión pendiente).
- Streaming de tokens.
- Extracción estructurada de preferencias como nodo separado (posible mejora futura).
- Evaluación de calidad de las recomendaciones (evals).

## Definition of Done
- Criterios marcados `[x]` y `pytest tests/ -v` en verde sin llamadas reales al LLM.
- Prueba manual documentada con `OPENAI_API_KEY` real y mcp-server en modo mock levantado.
