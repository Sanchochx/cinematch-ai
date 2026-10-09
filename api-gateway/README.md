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
| Body inválido o JSON malformado | 400 | `invalid_request` |
| Body > 512 kb | 413 | `payload_too_large` |
| Más de `RATE_LIMIT_MAX` peticiones por ventana | 429 | `rate_limited` |
| Método distinto de POST/OPTIONS | 405 | `method_not_allowed` |
| `Content-Type` distinto de `application/json` | 415 | `invalid_request` |
| ai-engine inalcanzable o 503 | 503 | `upstream_unavailable` |
| ai-engine 5xx/4xx (incl. 422) o respuesta sin `reply` string | 502 | `upstream_error` |
| Timeout (`AI_ENGINE_TIMEOUT_MS`, 30000 por defecto) | 504 | `timeout` |
| Error inesperado | 500 | `internal_error` |

Los mensajes de error nunca incluyen trazas, URLs internas ni detalles del upstream, y no se reenvían cabeceras del cliente.

## Seguridad (US-GW-003)
Orden: `helmet` → CORS → rate limit → parser JSON → rutas.

- **CORS:** allowlist exacta de `CORS_ORIGIN` (lista separada por comas; `*` se rechaza al arrancar y la variable es obligatoria con `NODE_ENV=production`). Un navegador desde otro origen recibe `403 forbidden_origin` sin cabeceras CORS. Preflight `OPTIONS /api/chat` → `204` (`POST, OPTIONS`, `Content-Type`, `Max-Age` 600, sin credenciales).
- **Body:** máximo 512 kb (cubre el historial máximo: 20 × 10 000 caracteres + mensaje de 2000, con margen para UTF-8); superarlo → `413 payload_too_large`.
- **Rate limit** por IP en `/api/chat`: `RATE_LIMIT_MAX` (20) por `RATE_LIMIT_WINDOW_MS` (60000) → `429 rate_limited` con `Retry-After`. `/health` y los preflights quedan fuera.
- **Métodos:** en `/api/chat` solo `POST` y `OPTIONS`; el resto → `405` con `Allow`.
- **Helmet** con cabeceras por defecto.

## Desarrollo
`npm run dev` · `npm test` · `npm run lint`
