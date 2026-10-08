# US-AI-002: Cliente MCP HTTP con descubrimiento dinámico de tools

**Épica:** 03 — AI Engine
**Prioridad:** CRÍTICA
**Estimación:** 5 pts
**Dependencias:** US-AI-001

## Historia de usuario
**Como** agente del ai-engine,
**quiero** conectarme por HTTP al mcp-server y obtener sus tools en tiempo de ejecución,
**para** consultar TMDB sin acoplar el código del agente a tools concretas.

## Contexto técnico
- Transporte: Streamable HTTP en `/mcp` (ADR-001). URL por defecto
  `http://mcp-server:8000/mcp`, configurable con `MCP_SERVER_URL`.
- Cliente: `mcp.client.streamable_http.streamablehttp_client` + `mcp.ClientSession`.
- Módulo propuesto: `ai-engine/mcp_client/` (p. ej. `client.py`) y `ai-engine/config.py` con
  `Settings` (dataclass, como el mcp-server).
- Las tools MCP deben convertirse a tools de LangChain (`BaseTool`/`StructuredTool`) para que el
  grafo las pueda enlazar al LLM. Se implementó un adaptador propio sobre `list_tools`/`call_tool`
  (sin `langchain-mcp-adapters`, para no añadir dependencias).
- El ai-engine **nunca** habla con TMDB; solo con el mcp-server (red `ai_network`).

## Criterios de aceptación
- [x] `config.py` expone `Settings` con `mcp_server_url` (default `http://mcp-server:8000/mcp`,
  env `MCP_SERVER_URL`) y `mcp_timeout_seconds` (default razonable, p. ej. 10).
- [x] Existe una función/clase async que abre sesión MCP por HTTP, hace `initialize` y `list_tools`.
- [x] Las tools se obtienen **dinámicamente**: ningún nombre de tool (`search_movies`, etc.) aparece
  hardcodeado en el código de producción.
- [x] Cada tool MCP se convierte en una tool de LangChain conservando `name`, `description` y el
  esquema JSON de argumentos.
- [x] Al invocar una tool convertida se ejecuta `call_tool` en el servidor y se devuelve su
  contenido como texto/JSON usable por el LLM.
- [x] Si el resultado MCP trae `isError=True`, se devuelve al LLM como mensaje de error legible
  (no se propaga una excepción que rompa el grafo).
- [x] Si el servidor MCP no está disponible o excede el timeout, se lanza una excepción propia
  (`McpConnectionError`) con mensaje claro; no cuelga indefinidamente.
- [x] La URL no está hardcodeada fuera de `Settings` y se usa nombre de servicio de Compose, no IP.
- [x] Tests (con mock de la sesión MCP o servidor MCP en memoria): descubrimiento de tools,
  conversión de esquema, llamada exitosa, `isError`, servidor caído/timeout.
- [x] Verificación manual: con `docker compose up mcp-server`, un script o test de integración
  marcado (`@pytest.mark.integration`) lista las tools reales `search_movies` y `get_movie_details`.

**Notas de implementación (2026-10-08):** cada operación abre una sesión MCP corta (el servidor es
stateless). Se usa `streamable_http_client` (`streamablehttp_client` está deprecado en mcp 1.30). Los
fallos de transporte durante una llamada de tool se devuelven al LLM como texto. Test de integración
(`MCP_INTEGRATION_URL=http://<ip>:8000/mcp pytest -m integration`) verificado contra el mcp-server real.

## Fuera de alcance
- El grafo del agente y la decisión de cuándo llamar tools (US-AI-003).
- Caché de la lista de tools entre requests más allá de lo necesario (puede decidirse en US-AI-003).
- Autenticación hacia el mcp-server.

## Definition of Done
- Criterios marcados `[x]` y `pytest tests/ -v` en verde.
- Ningún secreto en el código; `TMDB_API_KEY` no se menciona en el ai-engine.
