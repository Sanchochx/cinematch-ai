# US-AI-001: Entorno Python y dependencias del AI Engine

**Épica:** 03 — AI Engine
**Prioridad:** CRÍTICA
**Estimación:** 2 pts
**Dependencias:** Ninguna

## Historia de usuario
**Como** desarrollador del ai-engine,
**quiero** un entorno Python 3.11 con dependencias de runtime y de desarrollo separadas y versionadas,
**para** construir el agente de forma reproducible en local y en Docker.

## Contexto técnico
- Servicio: `ai-engine/` (Python 3.11, imagen base `python:3.11-slim`).
- Se replica el patrón de `mcp-server/` (`requirements.txt` + `requirements-dev.txt` + `tests/`).
- Las versiones de LangGraph/LangChain cambian rápido: acotar con rangos (`>=X,<Y_mayor`) usando la
  última estable al implementar y verificar la compatibilidad entre `langgraph`, `langchain-core` y
  `langchain-openai`.
- El cliente MCP del `ai-engine` usa el mismo SDK oficial `mcp` que el servidor (rango compatible
  con `mcp>=1.30,<2` del mcp-server).

## Criterios de aceptación
- [x] Existe `ai-engine/requirements.txt` solo con dependencias de runtime:
  - `langgraph`
  - `langchain` (y `langchain-core` si se importa directamente)
  - `langchain-openai` (integración del LLM)
  - `mcp` (cliente MCP)
  - `fastapi`
  - `uvicorn[standard]`
  - Todas con versión acotada.
- [x] Existe `ai-engine/requirements-dev.txt` que incluye `-r requirements.txt` y añade `pytest`,
  `pytest-asyncio`, `httpx` (necesario para `TestClient`/`ASGITransport` de FastAPI) y `respx`.
- [x] Existe `ai-engine/pytest.ini` con `asyncio_mode = auto` y `testpaths = tests`.
- [x] Existe `ai-engine/tests/` con `__init__.py` o `conftest.py` mínimo.
- [x] En un venv limpio con Python 3.11, `pip install -r requirements-dev.txt` termina sin errores
  ni conflictos de versiones.
- [x] `python -c "import langgraph, langchain, langchain_openai, mcp, fastapi, uvicorn"` funciona.
- [x] `.venv/`, `__pycache__/` y `.pytest_cache/` no se versionan.
- [x] Ninguna dependencia de desarrollo aparece en `requirements.txt`.

**Nota de implementación (2026-10-08):** se descartó `pydantic-settings`; la configuración usa un
`dataclass` + `os.environ`, igual que `mcp-server/config.py`. Verificado en `python:3.11-slim`
(mcp 1.30.0, langgraph 1.2.14, langchain 1.4.3, langchain-openai 1.7.0, fastapi 0.143.0). El
`.venv` local del host usa Python 3.14 (no hay 3.11 en el host).

## Fuera de alcance
- Escribir cliente, grafo o API (US-AI-002 a 004).
- Modificar el `Dockerfile` (US-AI-005).

## Definition of Done
- Criterios marcados `[x]`.
- Comando de verificación documentado:
  ```bash
  cd ai-engine && python3.11 -m venv .venv && source .venv/bin/activate
  pip install -r requirements-dev.txt && python -c "import langgraph, langchain, langchain_openai, mcp, fastapi, uvicorn"
  ```
