# Epic 03: AI Engine — Agente LangGraph que consume las tools MCP

**Fase:** 3
**Prioridad:** CRÍTICA
**Prefijo de ID:** `US-AI`
**Carpeta:** `context/user_stories/epic_03_ai_engine/`

## Objetivo
Convertir el stub de `ai-engine/` en el motor cognitivo de CineMatch: un agente LangGraph que recibe
un mensaje del usuario, razona con un LLM, descubre y llama dinámicamente a las tools del
`mcp-server` (TMDB) y devuelve una recomendación fundamentada, expuesto como API REST con FastAPI.

## Estado de partida
- `ai-engine/main.py` es un stub (`print('AI Engine OK')` + bucle `sleep`).
- `ai-engine/Dockerfile` es multi-stage, pero la etapa `builder` está vacía; la final corre como `appuser`.
- No existe `requirements.txt` ni `tests/`.
- El `mcp-server` ya expone `search_movies` y `get_movie_details` por Streamable HTTP en `/mcp` (Fase 2).

## Historias de usuario

| ID | Historia | Prioridad | Estimación | Dependencias |
|----|----------|-----------|------------|--------------|
| [US-AI-001](US-AI-001_python_environment/US-AI-001_python_environment.md) | Entorno Python y dependencias | CRÍTICA | 2 pts | Ninguna |
| [US-AI-002](US-AI-002_mcp_http_client/US-AI-002_mcp_http_client.md) | Cliente MCP HTTP con descubrimiento dinámico de tools | CRÍTICA | 5 pts | US-AI-001 |
| [US-AI-003](US-AI-003_langgraph_agent/US-AI-003_langgraph_agent.md) | Agente LangGraph (razonar → tools → responder) | CRÍTICA | 8 pts | US-AI-002 |
| [US-AI-004](US-AI-004_fastapi_chat_endpoint/US-AI-004_fastapi_chat_endpoint.md) | API REST FastAPI: `POST /chat` y `GET /health` | CRÍTICA | 5 pts | US-AI-003 |
| [US-AI-005](US-AI-005_dockerfile_dependencies/US-AI-005_dockerfile_dependencies.md) | Dockerfile con venv y arranque de uvicorn | ALTA | 3 pts | US-AI-001, US-AI-004 |

**Total:** 5 US · 23 pts

Orden de ejecución sugerido: `001 → 002 → 003 → 004 → 005`.

## Decisiones tomadas para esta épica (registrar como ADR en `docs/decisions/`)
- **Framework HTTP: FastAPI + uvicorn** (ADR dentro de US-AI-004).
- **Proveedor de LLM: OpenAI vía `langchain-openai`** (ADR dentro de US-AI-003). El modelo es
  configurable por env (`LLM_MODEL`), no hardcodeado.
- **Agente sin persistencia** en esta fase: el cliente envía el historial en cada request
  (stateless). El checkpointer/BD sigue pendiente de decisión.
- **Tools descubiertas dinámicamente** vía `list_tools` de MCP; el agente no conoce `search_movies`
  ni `get_movie_details` por nombre en el código.

## Puntos a validar en la revisión técnica
1. **URL del MCP:** el brief indica `http://mcp-server:8000`, pero el transporte (ADR-001) sirve en
   **`/mcp`**. Las US usan `MCP_SERVER_URL=http://mcp-server:8000/mcp`, igual que `CLAUDE.md`.
2. **Variable del LLM:** `docker-compose.yml` pasa hoy `OPENAI_API_KEY` al ai-engine, mientras que
   `CLAUDE.md` documenta `LLM_API_KEY`. Se propone que el código lea `OPENAI_API_KEY` (la que usa
   `langchain-openai` por defecto) y actualizar `CLAUDE.md`; alternativa: cambiar el compose.
3. **`CMD` del Dockerfile:** pasar a `uvicorn` obliga a modificar `CMD ["python","main.py"]`
   (a diferencia de la épica 02). Las líneas de `appuser` siguen intactas.
4. **`docker-compose.yml` no se modifica** en esta épica: `MCP_SERVER_URL` y `LLM_MODEL` tienen
   valores por defecto en código; pasarlas por compose queda como tarea posterior.
5. **Orden de `ai_network`:** `internal: true` no afecta al LLM porque el ai-engine también está en
   `internal_network` (con egress); si se aislara, habría que revisar el acceso a la API del LLM.

## Fuera de alcance de la épica
- Streaming (SSE) de respuestas, persistencia de conversaciones, autenticación.
- Cambios en api-gateway, frontend o mcp-server.
