# api-gateway

Único punto de entrada público del backend. El frontend solo habla con este servicio; el `ai-engine` no es alcanzable desde el host.

## `GET /health`
`200 {"status":"ok"}`

## `POST /api/chat`
Valida el mensaje y lo reenvía a `${AI_ENGINE_URL}/chat`.

```json
// request (Content-Type: application/json)
{ "message": "Quiero algo de ciencia ficción tipo Interstellar",
  "history": [ { "role": "user|assistant", "content": "..." } ] }   // history opcional (por defecto [])
// 200
{ "reply": "Te recomiendo ..." }
// error
{ "error": "invalid_request|upstream_unavailable|upstream_error|timeout|internal_error",
  "message": "Texto genérico apto para mostrar al usuario" }
```

Límites (`src/models/chatRequest.js`, `CHAT_LIMITS`): `message` 1–2000 caracteres tras `trim()`; `history` ≤ 20 ítems con `role` ∈ {`user`,`assistant`} y `content` 1–2000. Los campos extra se descartan.

| Situación | Status | `error` |
|---|---|---|
| Body inválido, JSON malformado o > 64 kb | 400 | `invalid_request` |
| `Content-Type` distinto de `application/json` | 415 | `invalid_request` |
| ai-engine inalcanzable o 503 | 503 | `upstream_unavailable` |
| ai-engine 5xx/4xx (incl. 422) o respuesta sin `reply` string | 502 | `upstream_error` |
| Timeout (`AI_ENGINE_TIMEOUT_MS`, 30000 por defecto) | 504 | `timeout` |
| Error inesperado | 500 | `internal_error` |

Los mensajes de error nunca incluyen trazas, URLs internas ni detalles del upstream, y no se reenvían cabeceras del cliente.

## Desarrollo
`npm run dev` · `npm test` · `npm run lint`
