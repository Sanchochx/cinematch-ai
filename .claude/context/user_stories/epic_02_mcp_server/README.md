# Epic 02: MCP Server — Tools MCP sobre la API de TMDB

**Fase:** 2
**Prioridad:** CRÍTICA
**Prefijo de ID:** `US-MCP`
**Carpeta:** `context/user_stories/epic_02_mcp_server/`

## Objetivo
Convertir el stub actual de `mcp-server/` en un servidor MCP real que exponga al agente del
`ai-engine` herramientas de solo lectura sobre TMDB, con un modo mock que permita desarrollar sin
API key.

## Estado de partida
- `mcp-server/main.py` es un stub (`print('MCP Server OK')` + bucle `sleep`).
- `mcp-server/Dockerfile` es multi-stage, pero la etapa `builder` está vacía y la final corre como `appuser`.
- No existe `requirements.txt` ni `tests/`.

## Historias de usuario

| ID | Historia | Prioridad | Estimación | Dependencias |
|----|----------|-----------|------------|--------------|
| [US-MCP-001](US-MCP-001_python_environment/US-MCP-001_python_environment.md) | Entorno Python y dependencias | CRÍTICA | 2 pts | Ninguna |
| [US-MCP-002](US-MCP-002_mcp_server_tmdb_client/US-MCP-002_mcp_server_tmdb_client.md) | Servidor MCP, cliente TMDB y fallback mock | CRÍTICA | 5 pts | US-MCP-001 |
| [US-MCP-003](US-MCP-003_search_movies_tool/US-MCP-003_search_movies_tool.md) | Tool `search_movies` | CRÍTICA | 3 pts | US-MCP-002 |
| [US-MCP-004](US-MCP-004_get_movie_details_tool/US-MCP-004_get_movie_details_tool.md) | Tool `get_movie_details` | CRÍTICA | 3 pts | US-MCP-002 |
| [US-MCP-005](US-MCP-005_dockerfile_dependencies/US-MCP-005_dockerfile_dependencies.md) | Instalación de dependencias en el Dockerfile | ALTA | 2 pts | US-MCP-001 |

**Total:** 5 US · 15 pts

Orden de ejecución sugerido: `001 → 002 → 003 → 004 → 005`. La 005 solo depende de la 001, pero
conviene cerrarla al final para validar la imagen con el servidor ya funcional.

## Decisiones tomadas para esta épica
- **Nombres de tools en inglés** (`search_movies`, `get_movie_details`), siguiendo la convención de
  `CLAUDE.md` (snake_case con verbo) y `docs/architecture.md`.
- **Transporte MCP: Streamable HTTP** en el puerto 8000, porque ai-engine y mcp-server están en
  contenedores distintos. Se registra como ADR en `docs/decisions/` dentro de US-MCP-002.
- **Cliente HTTP: `httpx`** (async), coherente con el SDK oficial `mcp`, que es asíncrono.

## Notas y riesgos fuera de alcance
- `docker-compose.yml` **no** pasa hoy `TMDB_API_KEY` al servicio `mcp-server`. Como esta épica no
  modifica el compose, dentro del contenedor el servidor arrancará en **modo mock**. Pasar la
  variable (`env_file` o `environment`) queda como tarea posterior.
- `docs/architecture.md` indica que el mcp-server no tiene salida a internet (solo `ai_network`),
  pero el compose actual ya lo conecta también a `internal_network` (bridge con egress).
  Inconsistencia a resolver en un ADR aparte; no se corrige en esta épica.
