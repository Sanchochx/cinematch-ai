# ADR-003: FastAPI + uvicorn como framework HTTP del ai-engine

**Fecha:** 2026-10-08
**Estado:** Aceptada
**Historia:** US-AI-004

## Contexto
El api-gateway necesita un endpoint interno para enviar mensajes al agente. El ai-engine solo es
accesible desde `internal_network` (`http://ai-engine:8000`).

## Decisión
- **FastAPI** servido por **uvicorn** en `0.0.0.0:8000`: nativo async (el agente lo es) y con
  validación Pydantic integrada.
- Contrato: `POST /chat` (`{message, history?}` → `{reply}`) y `GET /health` (`{"status":"ok"}`,
  sin tocar LLM ni TMDB).
- Errores genéricos `{"detail": ...}`: `McpConnectionError` → 503, `LlmError` → 502, cualquier otra → 500.
- El agente se inyecta con `Depends` (`dependency_overrides` en tests). El grafo se construye en la
  primera petición y se reutiliza, no en el arranque: así el ai-engine arranca aunque el mcp-server
  esté caído y responde 503 hasta que vuelva.
- `/docs`, `/redoc` y `/openapi.json` desactivados salvo `ENABLE_DOCS=true`.
- Los logs registran solo longitudes, nunca el contenido del mensaje.

## Consecuencias
- Stateless: el gateway reenvía el historial en cada request (máx. 20 mensajes de 2000 caracteres).
- Sin autenticación ni rate limiting en el ai-engine: dependen del aislamiento de red y del gateway.
- El `CMD` del Dockerfile debe pasar a uvicorn (US-AI-005).
