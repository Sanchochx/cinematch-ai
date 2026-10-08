# Resumen de Fase 3 — MOTOR COGNITIVO: AI Engine (LangGraph)

**Fecha de cierre:** 2026-10-08
**Épica:** 03 AI Engine · **US completadas:** 5/5 (23 pts) · **Validación:** prueba de integración con Docker Compose y la API real de TMDB superada

## 📝 Changes Made

El stub de `ai-engine/` es ahora un agente LangGraph que razona con un LLM, descubre las tools del mcp-server y se expone por HTTP:

- **Cliente MCP** (`mcp_client/`): se conecta por Streamable HTTP a `MCP_SERVER_URL` (`/mcp`, [ADR-001](../../docs/decisions/ADR-001-transporte-mcp-streamable-http.md)).
  `load_mcp_tools` descubre las tools en tiempo de ejecución y las convierte en tools de LangChain, así que el agente
  no tiene `search_movies` ni `get_movie_details` escritos a mano. Los fallos de conexión salen como `McpConnectionError`.
- **Agente ReAct** (`agent/`): `agent → (tools → agent)* → END`, compilado **sin checkpointer**
  ([ADR-002](../../docs/decisions/ADR-002-proveedor-llm-y-agente-sin-checkpointer.md)).
  - LLM de OpenAI vía `langchain-openai` (`gpt-4o-mini` por defecto, configurable con `LLM_MODEL`).
  - Límite de 6 iteraciones de tools (`recursion_limit` = 13). Al excederlo devuelve un mensaje de degradación en vez de un error.
  - `ToolNode(handle_tool_errors=True)`: si una tool falla, el LLM recibe el error como `ToolMessage` y el grafo sigue.
  - LLM y tools se inyectan en `build_graph`, de modo que los tests no necesitan red.
- **API FastAPI** (`api/`, `main.py`) servida por uvicorn ([ADR-003](../../docs/decisions/ADR-003-fastapi-uvicorn-ai-engine.md)):
  - `POST /chat` (`{message, history?}` → `{reply}`) y `GET /health` (`{"status":"ok"}`, sin tocar LLM ni TMDB).
  - Errores genéricos: `McpConnectionError` → 503, `LlmError` → 502, cualquier otra → 500.
  - `/docs`, `/redoc` y `/openapi.json` solo con `ENABLE_DOCS=true`. Los logs registran longitudes, nunca el contenido.
- **Dockerfile multi-stage** (US-AI-005): dependencias en un venv de la etapa `builder`, copiado a la imagen final.

## 🧠 Decisión clave: grafo perezoso (ADR-003)

El grafo **no se construye al arrancar**. `ChatService` recibe una *fábrica* (`GraphFactory`) y la ejecuta en la primera
petición a `/chat`; después reutiliza la instancia.

```python
async def _get_graph(self):
    async with self._lock:          # una sola construcción aunque lleguen peticiones concurrentes
        if self._graph is None:
            self._graph = await self._factory()
        return self._graph
```

- **Por qué:** construir el grafo exige descubrir las tools en el mcp-server. Si se hiciera en el `lifespan` y el
  mcp-server estuviera caído o aún arrancando, el ai-engine moriría o quedaría en bucle de reinicios.
- **Qué se gana:**
  - El ai-engine arranca siempre y `/health` responde `ok` sin depender de nada externo.
  - Mientras el mcp-server no esté disponible, `/chat` responde **503**. Cuando vuelve, la siguiente petición construye el grafo y todo funciona, sin reiniciar nada.
  - No hay orden de arranque estricto entre `ai-engine` y `mcp-server` en Compose.
- **Por qué es seguro:** el `asyncio.Lock` evita construcciones duplicadas, y si la fábrica falla `_graph` queda en `None`,
  así que el siguiente intento reintenta (no se cachean errores).
- **Trade-off:** la primera petición paga el coste de descubrir las tools, y un mcp-server mal configurado se detecta en
  la primera llamada y no al desplegar. Se mitiga con `/health` y con el test de integración.
- **Inyección:** el agente entra por `Depends` (`dependency_overrides` en tests), así `test_api.py` no construye ningún grafo real.

## 🐳 Orquestación del Dockerfile

```
builder (python:3.11-slim)           final (python:3.11-slim)
  python -m venv /opt/venv    ──►      COPY --from=builder /opt/venv
  pip install -r requirements.txt      usuario de sistema appuser (sin home)
                                       COPY --chown=appuser:appgroup . .
                                       USER appuser · EXPOSE 8000
                                       CMD uvicorn main:app --host 0.0.0.0 --port 8000
```

- **Multi-stage con venv:** la imagen final solo lleva el entorno ya instalado, sin caché de pip ni herramientas de build.
  Mismo patrón que el mcp-server.
- **`CMD` con uvicorn** en lugar del bucle `sleep` del stub; `main:app` expone la aplicación creada por `create_app()`.
- **Usuario sin privilegios** (`appuser`), como exige la regla 7 de `CLAUDE.md`.
- **`PYTHONUNBUFFERED=1`** para que los logs lleguen a `docker compose logs`, y `PYTHONDONTWRITEBYTECODE=1`.
- **`.dockerignore`** excluye `.venv/`, `__pycache__/`, `.pytest_cache/`, `tests/` y `.env`.
- **Compose:** `ai-engine` está en `internal_network` + `ai_network`, recibe solo `OPENAI_API_KEY` (nunca la de TMDB),
  tiene límite de 0.5 CPU / 512 MB y publica `8001:8000` para pruebas locales.
- **Dependencias** (`requirements.txt`): `langgraph`, `langchain`, `langchain-openai`, `mcp`, `fastapi`, `uvicorn[standard]`.

## 📂 Files Modified/Created

| Ruta (en `ai-engine/`) | Propósito |
|---|---|
| `requirements.txt` / `requirements-dev.txt`, `pytest.ini` | Dependencias de runtime y de test, configuración de pytest |
| `config.py` | `Settings` y `load_settings()`: `OPENAI_API_KEY` (`repr=False`), `LLM_MODEL`, `MCP_SERVER_URL`, `MCP_TIMEOUT_SECONDS`, `ENABLE_DOCS` |
| `mcp_client/client.py`, `tools.py`, `errors.py` | Cliente Streamable HTTP, descubrimiento de tools y `McpConnectionError` |
| `agent/graph.py`, `nodes.py`, `state.py`, `prompts.py`, `errors.py` | Grafo ReAct, nodos, estado, prompt del sistema y `LlmError` |
| `api/routes.py`, `schemas.py`, `service.py`, `errors.py` | Endpoints, validación Pydantic, `ChatService` (grafo perezoso) y manejadores de error |
| `main.py` | `create_app()` con `lifespan` y la fábrica del grafo |
| `Dockerfile`, `.dockerignore` | Imagen multi-stage con venv, uvicorn y `appuser` |
| `tests/` | `test_config`, `test_mcp_client`, `test_agent`, `test_api` y `test_integration` (contra un MCP real, solo con `MCP_INTEGRATION_URL`) |
| `../.claude/docs/decisions/ADR-002-…`, `ADR-003-…` | Proveedor de LLM y agente sin checkpointer; FastAPI + uvicorn y grafo perezoso |

## 🎯 Rationale

- **Descubrimiento dinámico de tools:** añadir una tool al mcp-server la expone al agente sin tocar el ai-engine.
- **Agente stateless:** el historial viaja en cada request (máx. 20 mensajes de 2000 caracteres). Es simple y escala, a costa de más tokens.
- **Encaje en la arquitectura:** el ai-engine no se expone a la red pública, solo habla con el gateway (`internal_network`) y con el mcp-server (`ai_network`). Nunca contacta con TMDB directamente.
- **Credenciales:** los errores del proveedor se traducen a `LlmError` con solo el nombre de la excepción, porque el mensaje del SDK puede contener fragmentos de la clave.

## ✅ Validación

La prueba de integración con Docker Compose y la API real de TMDB fue exitosa: el endpoint FastAPI responde y el grafo
de LangGraph gestiona las llamadas al MCP correctamente.

## ⚠️ Riesgos conocidos (fuera de alcance de la fase)

- **Sin autenticación ni rate limiting** en el ai-engine: dependen del aislamiento de red y del gateway.
- **Sin persistencia:** la decisión de BD/checkpointer sigue pendiente; cada request reenvía el historial.
- **Redes:** `docs/architecture.md` sigue diciendo que el mcp-server solo está en `ai_network`, pero el compose también lo conecta a `internal_network`. Sigue pendiente un ADR.
- `ports: "8001:8000"` publica el ai-engine al host, contrario a la regla "el ai-engine NO se expone al host". Conviene retirarlo antes de producción.

## 🚀 Next Steps

- **Fase 4 — API Gateway (`US-GW`):** `POST /api/chat` con validación, CORS y streaming. Antes, decidir el framework HTTP (Express/Fastify) y registrarlo en un ADR. El gateway reenviará el historial a `http://ai-engine:8000/chat`.
- **Fase 5 — Frontend (`US-FE`):** UI de conversación y fichas de películas; decidir el bundler (Vite sugerido).
- Resolver la inconsistencia de redes y retirar la publicación del puerto del ai-engine.
