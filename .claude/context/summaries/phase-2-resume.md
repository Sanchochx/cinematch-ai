# Resumen de Fase 2 — DATOS: MCP Server sobre TMDB

**Fecha de cierre:** 2026-10-07
**Épica:** 02 MCP Server · **US completadas:** 5/5 (15 pts) · **Tests:** 138 pasan (Python 3.11 y 3.14)

## 📝 Changes Made

El stub de `mcp-server/` (`print` + bucle `sleep`) es ahora un servidor MCP real:

- **Servidor MCP con `FastMCP`** (SDK oficial `mcp`), transporte **Streamable HTTP** en `/mcp`, puerto 8000
  ([ADR-001](../../docs/decisions/ADR-001-transporte-mcp-streamable-http.md)). Se arranca con
  `run_streamable_http_async()` dentro de `asyncio.run`, y el proveedor se cierra en un `finally`.
- **Cliente TMDB asíncrono con `httpx.AsyncClient`**, coherente con el SDK `mcp`, que es async. Un único cliente
  con `base_url`, timeout configurable y `api_key` como query param por defecto. Se cierra con `aclose()`.
- **Patrón proveedor** (`MovieProvider`, un `Protocol`): las tools dependen solo del contrato, nunca de la implementación.
  - `TmdbProvider`: datos reales.
  - `MockProvider`: catálogo en memoria con los mismos ids que TMDB. Se usa cuando `TMDB_API_KEY` está vacía o ausente.
  - `create_provider(settings)` elige entre ambos al arrancar y registra un `WARNING` en modo mock.
- **Dos tools de solo lectura** (anotadas `READ_ONLY`):
  - `search_movies(genre?, keyword?, limit=10)`: máx. 20 resultados, género en español o inglés.
  - `get_movie_details(movie_id)`: id estricto (`strict=True`, `> 0`), director, hasta 5 actores, duración y fecha.
  - Ambas devuelven `source` (`'tmdb'` o `'mock'`) para que el agente sepa el origen de los datos.
- **Manejo de errores**: el decorador `handle_provider_errors` convierte los errores de dominio (`MovieNotFoundError`,
  `UnknownGenreError`, auth/rate limit/indisponibilidad de TMDB) en `ToolError` con mensaje seguro. Cualquier otra
  excepción se registra en el servidor y el agente recibe un mensaje genérico, sin stack trace.
- **Seguridad de la key**: `Settings.tmdb_api_key` con `repr=False`, y un `logging.Filter` que redacta la key en los
  logs de `httpx`/`httpcore`, que registran la URL completa.
- **Imagen Docker**: la etapa `builder` instala las dependencias en un venv (`/opt/venv`) que se copia a la etapa final.
  La imagen no lleva herramientas de build ni `requirements-dev.txt`.

## 📂 Files Modified/Created

| Ruta (en `mcp-server/`) | Propósito |
|---|---|
| `requirements.txt` / `requirements-dev.txt` | Dependencias de runtime (`mcp`, `httpx`, `typing-extensions`) y de test (`pytest`, `pytest-asyncio`, `respx`) |
| `pytest.ini`, `tests/` | Configuración y 69 funciones de test, 138 casos con parametrización (config, selección de proveedor, mock, TMDB con `respx`, tools, errores, servidor) |
| `config.py` | `Settings` inmutable y `load_settings()`: lee y valida `TMDB_API_KEY`, `MCP_HOST`, `MCP_PORT`, `TMDB_TIMEOUT_SECONDS`, `TMDB_LANGUAGE` |
| `main.py` | Entrypoint: logging, proveedor, servidor y cierre ordenado |
| `server.py` | `create_server()`: instancia `FastMCP` y registra las tools |
| `providers/base.py` | Contrato `MovieProvider` y tipos (`MovieSummary`, `MovieDetails`, `CastMember`) |
| `providers/tmdb.py` | Cliente TMDB async: mapeo de respuestas, errores HTTP y redacción de la key |
| `providers/mock.py`, `providers/genres.py`, `providers/errors.py`, `providers/__init__.py` | Catálogo mock, resolución de géneros es/en, excepciones de dominio, `create_provider` |
| `tools/search_movies.py`, `tools/get_movie_details.py` | Las dos tools MCP |
| `tools/errors.py`, `tools/__init__.py` | Decorador de errores y anotaciones `READ_ONLY` |
| `Dockerfile` | Instalación de dependencias en venv (US-MCP-005); las líneas de `appuser` no cambian |
| `.dockerignore` | Excluye `.venv/`, `__pycache__/`, `.pytest_cache/`, `tests/`, `.env` |
| `../.claude/docs/decisions/ADR-001-…` | Decisión del transporte MCP |

## 🎯 Rationale

- **Por qué FastMCP + Streamable HTTP:** ai-engine y mcp-server viven en contenedores distintos, así que no sirve stdio.
  FastMCP deriva el esquema de cada tool de las anotaciones de tipo (`Annotated` + `Field`), por lo que los
  descriptores que ve el agente salen del mismo código que los valida.
- **Por qué `httpx` asíncrono:** el servidor MCP corre sobre asyncio. Una llamada bloqueante a TMDB frenaría las demás peticiones.
- **Por qué el patrón proveedor + mock:** permite desarrollar el ai-engine sin API key y probar sin red.
  Los tests nunca llaman a TMDB: usan `respx`.
- **Encaje en la arquitectura:** el mcp-server es el único servicio que habla con TMDB. El ai-engine llega a él por
  `http://mcp-server:8000/mcp` (`MCP_SERVER_URL`) y accede a películas solo mediante estas tools.
- **Errores pensados para un LLM:** los mensajes son accionables (p. ej. el error de género lista los válidos),
  y "sin resultados" es una lista vacía, no un fallo.

## 🧱 Obstáculos superados

- **`PydanticUserError` solo dentro del contenedor.** Al cerrar US-MCP-005, `docker compose up mcp-server` fallaba al
  registrar `search_movies`: `Please use typing_extensions.TypedDict instead of typing.TypedDict on Python < 3.12`.
  - **Causa:** los `TypedDict` de las US-MCP-002/003/004 se importaban de `typing`, y pydantic (que usa FastMCP para
    generar el esquema de salida) los rechaza en Python < 3.12. La imagen usa `python:3.11-slim`, pero el `.venv` local
    era Python 3.14, así que los tests locales pasaban y el fallo solo aparecía en el contenedor.
  - **Solución:** importar `TypedDict` desde `typing_extensions` en `providers/base.py`, `providers/mock.py`,
    `tools/search_movies.py` y `tools/get_movie_details.py`, y declarar `typing-extensions>=4.12,<5` en `requirements.txt`.
  - **Verificación:** el servidor arranca en modo mock y se mantiene vivo en Docker, y los 138 tests pasan en 3.11 (contenedor) y 3.14 (local).
  - **Lección:** validar siempre en la versión de Python de la imagen, no solo en el venv local.

## ⚠️ Riesgos conocidos (fuera de alcance de la fase)

- `docker-compose.yml` no pasa `TMDB_API_KEY` al `mcp-server`: en Docker arranca en **modo mock** hasta añadir `env_file`/`environment`.
- `docs/architecture.md` dice que el mcp-server solo está en `ai_network` (sin internet), pero el compose también lo conecta
  a `internal_network` (con egress). Falta un ADR que lo resuelva; sin egress, `TmdbProvider` no podría alcanzar TMDB.
- El `.venv` local (Python 3.14) no coincide con la imagen (3.11); conviene alinearlo.

## 🚀 Next Steps

- **Fase 3 — AI Engine (`US-AI`):** agente LangGraph que consume `search_movies` y `get_movie_details` vía `MCP_SERVER_URL`.
  - **Decisiones previas, cada una con su ADR:** framework HTTP (FastAPI sugerido), proveedor de LLM y persistencia/checkpointer.
  - **Dependencia:** el cliente MCP del ai-engine debe usar Streamable HTTP en `/mcp` (ADR-001).
- Antes de integrar con TMDB real: pasar `TMDB_API_KEY` al `mcp-server` en el compose y resolver la inconsistencia de redes.
- Fases 4 (API Gateway, `US-GW`) y 5 (Frontend, `US-FE`) siguen sin historias de usuario.
