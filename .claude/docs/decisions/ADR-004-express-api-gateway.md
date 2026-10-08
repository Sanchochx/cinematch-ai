# ADR-004: Node.js 20 + Express como framework HTTP del api-gateway

**Fecha:** 2026-10-08
**Estado:** Aceptada
**Historia:** US-GW-001

## Contexto
El api-gateway es el único punto de entrada público del backend: valida input, aplica CORS/límites y
reenvía `POST /api/chat` al ai-engine. Es I/O-bound (espera al LLM), por lo que el rendimiento bruto
del framework no es el factor limitante.

## Decisión
- **Express 4** (ES modules) sobre Node 20+. Ecosistema maduro para lo que necesitamos
  (`cors`, `helmet`, `express-rate-limit`) y mínima superficie.
- Cliente HTTP al ai-engine con `fetch` nativo + `AbortSignal.timeout` (sin dependencias extra).
- Validación con `zod` (en el modelo); tests con Vitest + Supertest; lint con ESLint.
- `createApp(config, {logger, routers})` es una fábrica sin efectos: permite testear sin abrir puertos.
- Configuración solo por variables de entorno, validada al arrancar (falla rápido).

## Alternativas descartadas
- **Fastify:** más rápido, pero la ganancia no compensa otra curva de aprendizaje en un servicio I/O-bound.
- **Python/FastAPI:** `CLAUDE.md` define Node para la capa pública.

## Consecuencias
- Express 4 no captura rechazos de handlers `async`: las rutas async deben envolver errores (`next(err)`).
- Gateway stateless; rate limiting en memoria (válido con una réplica).
