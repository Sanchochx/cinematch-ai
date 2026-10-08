# US-MCP-001: Entorno Python y dependencias del MCP Server

**Épica:** 02 — MCP Server
**Prioridad:** CRÍTICA
**Estimación:** 2 pts
**Dependencias:** Ninguna

## Historia de usuario
**Como** desarrollador backend del mcp-server,
**quiero** un entorno Python 3.11 con sus dependencias declaradas y versionadas,
**para** construir el servidor MCP de forma reproducible en local y en Docker.

## Contexto técnico
- Servicio: `mcp-server/` (Python 3.11, imagen base `python:3.11-slim`).
- SDK oficial de Model Context Protocol: paquete PyPI `mcp` (incluye `FastMCP` y el transporte
  Streamable HTTP).
- Cliente HTTP elegido: `httpx`, porque es asíncrono y encaja con el modelo async del SDK.
- `CLAUDE.md` exige un test por cada tool MCP, así que se separan dependencias de runtime y de desarrollo.
- **Nota de implementación (2026-10-06):** la última estable de `mcp` es la 2.3.0, pero la 2.x
  renombró `FastMCP` a `MCPServer` (US-MCP-002 usa `FastMCP`). Se fija `mcp>=1.30,<2` (1.30.0 es la
  última 1.x). La verificación en 3.11 se hizo en un contenedor `python:3.11-slim`, porque el host
  no tiene 3.11.

## Criterios de aceptación
- [x] Existe `mcp-server/requirements.txt` solo con dependencias de runtime:
  - `mcp` con versión acotada (p. ej. `mcp>=1.x,<2`), usando la última estable al implementar.
  - `httpx` con versión acotada (p. ej. `httpx>=0.27,<1`).
- [x] Existe `mcp-server/requirements-dev.txt` que incluye `-r requirements.txt` y añade
  `pytest`, `pytest-asyncio` y `respx` (mock de `httpx`).
- [x] Existe `mcp-server/tests/` (con `__init__.py` o `conftest.py` mínimo) listo para las US siguientes.
- [x] En un venv limpio con Python 3.11, `pip install -r requirements-dev.txt` termina sin errores
  ni conflictos de versiones.
- [x] `python -c "import mcp, httpx"` funciona dentro del venv.
- [x] `.venv/`, `__pycache__/` y `.pytest_cache/` no se versionan (`.gitignore` del servicio o de la raíz).

## Fuera de alcance
- Escribir el servidor MCP o las tools (US-MCP-002 a 004).
- Modificar el `Dockerfile` (US-MCP-005).

## Definition of Done
- Criterios marcados `[x]`.
- Comando de verificación documentado:
  ```bash
  cd mcp-server && python3.11 -m venv .venv && source .venv/bin/activate
  pip install -r requirements-dev.txt && python -c "import mcp, httpx"
  ```
