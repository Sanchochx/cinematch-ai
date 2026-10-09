# US-GW-003: CORS restrictivo y endurecimiento HTTP del gateway

**Épica:** 04 — API Gateway
**Prioridad:** CRÍTICA
**Estimación:** 3 pts
**Dependencias:** US-GW-001

## Historia de usuario
**Como** responsable de seguridad,
**quiero** que el gateway solo acepte peticiones de navegador desde el origen del frontend y limite el abuso,
**para** proteger el ai-engine (y el gasto del LLM) de tráfico no autorizado.

## Contexto técnico
- `CORS_ORIGIN` (por defecto `http://localhost:5173`) define el origen permitido; admite lista separada por comas.
- Middlewares propuestos: `cors`, `helmet`, `express.json({limit})`, `express-rate-limit`.
- Orden: seguridad (helmet, CORS) → rate limit → parser JSON → rutas.
- Cada llamada a `/api/chat` consume tokens del LLM: el rate limit es una defensa de **coste**, no solo de disponibilidad.

## Criterios de aceptación
- [x] CORS usa una **allowlist exacta** tomada de `CORS_ORIGIN`; nunca `*` ni reflejo del `Origin` recibido.
  Si `CORS_ORIGIN` es `*` o vacío en `NODE_ENV=production`, el arranque falla.
- [x] Origen permitido → respuesta con `Access-Control-Allow-Origin` igual a ese origen y `Vary: Origin`.
- [x] Origen no permitido → sin cabeceras CORS (el navegador bloquea); la petición no se procesa como si fuera confiable.
- [x] Preflight `OPTIONS /api/chat` responde `204` con `Allow-Methods: POST, OPTIONS` y `Allow-Headers: Content-Type`,
  con `Max-Age` razonable; sin `Allow-Credentials` (no hay cookies).
- [x] Límite de body `express.json({ limit: '64kb' })`; excederlo → `413 {"error":"payload_too_large"}`.
- [x] Rate limit por IP en `/api/chat` (por defecto 20 req/min, configurable por `RATE_LIMIT_MAX`/`RATE_LIMIT_WINDOW_MS`);
  al excederlo → `429 {"error":"rate_limited"}` con cabecera `Retry-After`. `/health` queda excluido.
- [x] `helmet` activo con cabeceras por defecto (API JSON: `X-Content-Type-Options: nosniff`, etc.).
- [x] Solo `POST` (y `OPTIONS`) permitidos en `/api/chat`; otros métodos → `405` con `Allow`.
- [x] Tests (Supertest): origen permitido, origen no permitido, preflight, 413, 429 con `Retry-After`,
  405, y fallo de arranque con `CORS_ORIGIN=*` en producción.
- [x] Variables nuevas documentadas en `CLAUDE.md` (sección *Variables de entorno*).

## Fuera de alcance
- Autenticación/API keys, rate limiting distribuido (Redis), WAF, TLS (se asume terminación TLS fuera del compose).

## Definition of Done
- Criterios marcados `[x]` y `npm test` en verde.
- Prueba manual con `curl -i -H 'Origin: http://evil.example' ...` (sin cabeceras CORS) y con
  `Origin: http://localhost:5173` (con cabeceras); ráfaga de >20 peticiones devuelve `429`.
- Revisado con el skill `code-review` y sin hallazgos de seguridad abiertos.
- Plan de implementación actualizado.
