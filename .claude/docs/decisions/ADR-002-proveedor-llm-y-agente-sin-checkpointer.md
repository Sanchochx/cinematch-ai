# ADR-002: Proveedor de LLM (OpenAI) y agente LangGraph sin checkpointer

**Fecha:** 2026-10-08
**Estado:** Aceptada
**Historia:** US-AI-003

## Contexto
El agente del `ai-engine` necesita un LLM con soporte de tool calling y decidir si conserva el
estado de la conversación entre requests.

## Decisión
- **Proveedor:** OpenAI a través de `langchain-openai` (`ChatOpenAI`).
- **Modelo por defecto:** `gpt-4o-mini` (coste bajo, tool calling fiable). Configurable con
  `LLM_MODEL`; temperatura 0.2 y timeout de 30 s.
- **Credencial:** solo `OPENAI_API_KEY` desde el entorno, guardada con `repr=False` y pasada como
  `SecretStr`. Los errores del proveedor se traducen a `LlmError` con solo el nombre de la
  excepción, porque el mensaje del SDK puede contener fragmentos de la clave.
- **Grafo:** `agent → (tools → agent)* → END`, compilado **sin checkpointer**. El cliente envía el
  historial completo en cada request (stateless).
- **Límite del bucle:** 6 iteraciones de tools (`recursion_limit` = 13). Al excederlo se devuelve un
  mensaje de degradación en lugar de un error.

## Consecuencias
- Cambiar de proveedor implica sustituir `create_llm`; el grafo recibe el LLM por inyección.
- Sin persistencia: la memoria vive en el cliente y cada request reenvía el historial (más tokens).
  La decisión de BD/checkpointer sigue pendiente.
- Un fallo de tool no rompe el grafo: el LLM recibe el error como `ToolMessage`.
