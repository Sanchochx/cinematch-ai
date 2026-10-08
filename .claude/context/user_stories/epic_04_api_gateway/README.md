# Epic 04: API Gateway — Punto de entrada público hacia el AI Engine

**Fase:** 4
**Prioridad:** CRÍTICA
**Prefijo de ID:** `US-GW`
**Carpeta:** `context/user_stories/epic_04_api_gateway/`

## Objetivo
Convertir el stub de `api-gateway/` en un servicio ligero (Node.js 20 + Express) que es el **único**
punto de entrada público del backend: valida el input, aplica CORS y límites de seguridad, y reenvía
`POST /api/chat` al `ai-engine` interno (`http://ai-engine:8000/chat`).

## Estado de partida
- `api-gateway/index.js` es un stub (`console.log('Gateway OK')` + `setInterval`).
- `api-gateway/Dockerfile` es multi-stage pero la etapa `builder` está vacía; la final corre como `node`.
- No existe `package.json` ni `tests/`.
- El `ai-engine` ya expone `POST /chat` (`{message, history?}` → `{reply}`) y `GET /health` (Fase 3),
  **sin puerto publicado al host** (solo `internal_network`).
- `docker-compose.yml` publica `3000:3000` en el gateway pero no le pasa variables de entorno.

## Historias de usuario

| ID | Historia | Prioridad | Estimación | Dependencias |
|----|----------|-----------|------------|--------------|
| [US-GW-001](US-GW-001_express_setup/US-GW-001_express_setup.md) | Proyecto Node/Express base y `GET /health` | CRÍTICA | 2 pts | Ninguna |
| [US-GW-002](US-GW-002_chat_proxy/US-GW-002_chat_proxy.md) | `POST /api/chat`: validación y proxy al ai-engine | CRÍTICA | 5 pts | US-GW-001 |
| [US-GW-003](US-GW-003_cors_security/US-GW-003_cors_security.md) | CORS restrictivo y endurecimiento HTTP | CRÍTICA | 3 pts | US-GW-001 |
| [US-GW-004](US-GW-004_dockerfile_compose/US-GW-004_dockerfile_compose.md) | Dockerfile multi-stage e integración en Compose | ALTA | 3 pts | US-GW-002, US-GW-003 |

**Total:** 4 US · 13 pts

Orden de ejecución sugerido: `001 → 002 → 003 → 004`.

## Decisiones propuestas (registrar como ADR en `docs/decisions/` al implementar)
- **Framework HTTP: Express 4/5** (JavaScript ES modules). Motivo: ecosistema maduro (`cors`, `helmet`,
  `express-rate-limit`), mínima superficie, equipo familiarizado. Alternativa descartada: Fastify (más
  rápido, pero el gateway es I/O-bound y la ganancia no justifica otra curva de aprendizaje). Python/FastAPI
  descartado para mantener Node en la capa pública, como define `CLAUDE.md`.
- **Cliente HTTP al ai-engine: `fetch` nativo de Node 20** (con `AbortSignal.timeout`); sin dependencias extra.
- **Validación: `zod`**, en el modelo (patrón modelo → servicio → ruta → test).
- **Tests: Vitest + Supertest** (o `node:test`; decidir en US-GW-001).
- **Gateway stateless:** el cliente reenvía `history` en cada request, igual que el ai-engine (ADR-002).

## Puntos a validar en la revisión técnica
1. **Límites del gateway = límites del ai-engine.** `message` ≤ 2000 caracteres e `history` ≤ 20 ítems
   (`ai-engine/api/schemas.py`). El gateway los replica para rechazar antes de gastar una llamada interna;
   si cambian en el ai-engine hay que sincronizarlos (constantes en un único módulo del gateway).
2. **Streaming (SSE):** `docs/architecture.md` lo menciona como ideal, pero el ai-engine hoy responde en
   una sola respuesta JSON. Queda **fuera de alcance**; el contrato `{reply}` es lo que se proxea.
3. **Rate limiting en memoria** (por IP): suficiente con una réplica. Con varias réplicas requeriría un
   store compartido (Redis) → fuera de alcance.
4. **`trust proxy`:** hoy no hay proxy delante del gateway, así que la IP del cliente es la del socket.
5. **Autenticación de usuarios:** pendiente de decidir en el proyecto; fuera de alcance.

## Fuera de alcance de la épica
- Streaming/SSE, autenticación, persistencia de conversaciones, caché de respuestas.
- Cambios en el `ai-engine`, `mcp-server` o `frontend` (salvo el bloque del gateway en `docker-compose.yml`).
