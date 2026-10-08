# US-AI-004: API REST FastAPI — `POST /chat` y `GET /health`

**Épica:** 03 — AI Engine
**Prioridad:** CRÍTICA
**Estimación:** 5 pts
**Dependencias:** US-AI-003

## Historia de usuario
**Como** api-gateway,
**quiero** un endpoint HTTP interno en el ai-engine para enviar el mensaje del usuario,
**para** obtener la recomendación del agente sin conocer su implementación.

## Contexto técnico
- Aplicación FastAPI en `ai-engine/main.py` (reemplaza el stub), servida por uvicorn en `0.0.0.0:8000`.
- El ai-engine **no se expone al host**: solo es accesible desde `internal_network`
  (`http://ai-engine:8000`) por el api-gateway.
- Patrón del proyecto: modelos → servicio → ruta → test. Estructura propuesta: `ai-engine/api/`
  (`schemas.py`, `routes.py`) y servicio que envuelve `run_agent`.
- El grafo y las tools MCP se inicializan una vez en el `lifespan` de la app y se reutilizan.
- Registrar ADR: FastAPI + uvicorn como framework HTTP del ai-engine.

## Contrato
`POST /chat`
```json
// request
{ "message": "Quiero una película de ciencia ficción tipo Interstellar",
  "history": [ { "role": "user|assistant", "content": "..." } ] }   // history opcional
// 200
{ "reply": "Te recomiendo ..." }
```
`GET /health` → `200 {"status":"ok"}` (no depende del LLM ni de TMDB).

## Criterios de aceptación
- [x] `POST /chat` valida con Pydantic: `message` obligatorio, no vacío, longitud máxima (p. ej. 2000);
  `history` opcional con roles restringidos a `user`/`assistant` y tamaño máximo.
- [x] Entrada inválida devuelve `422` con el detalle estándar de FastAPI.
- [x] Caso feliz devuelve `200` con `{"reply": str}` producido por el agente (US-AI-003).
- [x] `McpConnectionError` → `503`; `LlmError` → `502`; excepción inesperada → `500`.
  Los cuerpos de error son genéricos (`{"detail": "..."}`) y **no** exponen trazas, URLs internas ni claves.
- [x] `GET /health` responde `200 {"status":"ok"}`.
- [x] El agente se construye en el `lifespan` y se inyecta como dependencia (`Depends`), de modo que
  los tests puedan sobrescribirlo con `app.dependency_overrides`.
- [x] Arranque con `uvicorn main:app --host 0.0.0.0 --port 8000` funciona; el puerto 8000 se
  respeta sin variables extra.
- [x] Rutas en `/kebab-case`; docs automáticas (`/docs`) activas solo si no es producción
  (flag por env) o documentado que quedan accesibles únicamente en la red interna.
- [x] Logging de request sin contenido sensible (no se loguea el mensaje completo del usuario ni
  credenciales).
- [x] Tests con `TestClient`/`httpx.AsyncClient` y agente falso: éxito, 422 (vacío, tipo erróneo,
  rol inválido), 502, 503, 500, `/health`.
- [x] ADR registrado en `docs/decisions/` (FastAPI + uvicorn).

## Fuera de alcance
- Streaming SSE, autenticación entre servicios, rate limiting (responsabilidad del gateway).
- Modificar `api-gateway` o `docker-compose.yml`.

## Definition of Done
- Criterios marcados `[x]` y `pytest tests/ -v` en verde.
- Prueba manual: `docker compose up --build ai-engine mcp-server` y `POST /chat` ejecutado desde
  el contenedor del gateway (o `docker compose exec`) devuelve una recomendación.
