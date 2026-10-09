# US-GW-002: `POST /api/chat` — validación y proxy al AI Engine

**Épica:** 04 — API Gateway
**Prioridad:** CRÍTICA
**Estimación:** 5 pts
**Dependencias:** US-GW-001

## Historia de usuario
**Como** frontend,
**quiero** un único endpoint público `POST /api/chat`,
**para** enviar el mensaje del usuario y recibir la recomendación sin conocer el ai-engine.

## Contexto técnico
- Patrón: `models/chatRequest.js` (zod) → `services/aiEngineClient.js` (fetch) → `routes/chat.js` → test.
- El gateway reenvía a `${AI_ENGINE_URL}/chat` con `Content-Type: application/json` y `AbortSignal.timeout(AI_ENGINE_TIMEOUT_MS)`.
- El cliente del ai-engine se inyecta en `createApp` para poder sustituirlo por un doble en los tests.

## Contrato
`POST /api/chat`
```json
// request (idéntico al del ai-engine)
{ "message": "Quiero algo de ciencia ficción tipo Interstellar",
  "history": [ { "role": "user|assistant", "content": "..." } ] }   // history opcional
// 200
{ "reply": "Te recomiendo ..." }
// error
{ "error": "invalid_request|upstream_unavailable|upstream_error|timeout|internal_error",
  "message": "Texto genérico apto para mostrar al usuario" }
```

## Criterios de aceptación
- [x] Validación con zod: `message` obligatorio, `string`, `trim()` no vacío, ≤ 2000 caracteres;
  `history` opcional (por defecto `[]`), ≤ 20 ítems, `role` ∈ {`user`,`assistant`}, `content` 1–2000 caracteres.
  Los límites viven en una única constante del gateway.
- [x] Body inválido (campo faltante, tipo erróneo, rol inválido, JSON malformado) → `400` con `error: "invalid_request"`
  y mensaje genérico (sin eco del payload).
- [x] `Content-Type` distinto de `application/json` → `415`.
- [x] Caso feliz: reenvía **solo** `{message, history}` ya validados/saneados y devuelve `200 {"reply": string}`.
  Cualquier campo extra del cliente se descarta (no se hace *passthrough* del body).
- [x] Respuesta del ai-engine con forma inesperada (sin `reply` string) → `502 upstream_error`.
- [x] Mapeo de errores aguas abajo: ai-engine inalcanzable / `503` → `503 upstream_unavailable`;
  `502`/`5xx` → `502 upstream_error`; timeout → `504 timeout`; `422` del ai-engine → `502` (el gateway ya validó,
  por lo que es un desajuste de contrato); error inesperado → `500 internal_error`.
- [x] Los mensajes de error **no** exponen trazas, URL internas (`ai-engine:8000`), cabeceras ni detalles del upstream.
- [x] No se reenvían cabeceras del cliente (`Cookie`, `Authorization`, etc.) al ai-engine.
- [x] Tests con cliente falso (Supertest): éxito, 400 (vacío, demasiado largo, history inválido, JSON roto),
  415, 502 (forma inesperada y 5xx), 503, 504, 500, y verificación de que no se filtran campos extra.
- [x] El `README`/docs del gateway documenta el contrato de `POST /api/chat`.

## Fuera de alcance
- Streaming SSE, autenticación, caché, reintentos automáticos (el LLM no es idempotente ni barato).
- Rate limiting y CORS (US-GW-003).

## Definition of Done
- Criterios marcados `[x]` y `npm test` en verde, incluyendo la ruta nueva (regla 3 de `CLAUDE.md`).
- Prueba manual con el stack levantado: `curl -X POST localhost:3000/api/chat -H 'content-type: application/json'
  -d '{"message":"hola"}'` devuelve `{"reply": ...}` real; con el `ai-engine` detenido devuelve `503`.
- Confirmado que `ai-engine` **no** es alcanzable desde el host (`curl localhost:8000` y `:8001` fallan).
- Revisado con el skill `code-review` (sin issues CRÍTICOS/ALTOS).
- Plan de implementación actualizado.
