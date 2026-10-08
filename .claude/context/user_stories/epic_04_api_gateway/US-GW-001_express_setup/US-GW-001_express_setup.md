# US-GW-001: Proyecto Node/Express base y `GET /health`

**Épica:** 04 — API Gateway
**Prioridad:** CRÍTICA
**Estimación:** 2 pts
**Dependencias:** Ninguna

## Historia de usuario
**Como** desarrollador del equipo,
**quiero** un proyecto Node.js 20 con Express, configuración por entorno y un endpoint de salud,
**para** tener una base testeable sobre la que construir las rutas del gateway.

## Contexto técnico
- Reemplaza el stub `api-gateway/index.js`. Estructura propuesta (patrón modelo → servicio → ruta → test):
  ```
  api-gateway/
  ├── package.json            ← "type": "module", scripts: dev, start, test
  ├── src/
  │   ├── app.js              ← createApp(config): fábrica de Express (testeable sin abrir puerto)
  │   ├── server.js           ← lee config, arranca el listener y maneja SIGTERM
  │   ├── config.js           ← lectura/validación de variables de entorno
  │   ├── models/             ← esquemas zod
  │   ├── services/           ← cliente del ai-engine
  │   └── routes/             ← health.js, chat.js
  └── tests/
  ```
- Variables (de `CLAUDE.md`): `PORT=3000`, `AI_ENGINE_URL=http://ai-engine:8000`,
  `CORS_ORIGIN=http://localhost:5173`. Ninguna es secreto.
- Archivos en `camelCase.js`, rutas en `/kebab-case`.
- `package-lock.json` versionado (necesario para `npm ci` en el Dockerfile).

## Criterios de aceptación
- [x] `api-gateway/package.json` con `engines.node >= 20`, `"type": "module"` y scripts `dev`, `start`, `test`.
- [x] `createApp(config)` devuelve la app Express sin escuchar en ningún puerto (permite tests con Supertest).
- [x] `config.js` lee `PORT`, `AI_ENGINE_URL`, `CORS_ORIGIN` (y `AI_ENGINE_TIMEOUT_MS`, opcional, por defecto 30000)
  con valores por defecto sensatos; un valor inválido (p. ej. `PORT=abc`, URL malformada) hace fallar el arranque con un mensaje claro.
- [x] `GET /health` responde `200 {"status":"ok"}` sin llamar al ai-engine.
- [x] Rutas desconocidas responden `404 {"error":"not_found"}` en JSON (no HTML de Express).
- [x] Manejador global de errores: devuelve JSON genérico y **nunca** expone trazas, URLs internas ni cabeceras.
- [x] `server.js` cierra el servidor limpiamente ante `SIGTERM`/`SIGINT` (necesario para `docker compose down` rápido).
- [x] Se desactiva la cabecera `X-Powered-By`.
- [x] Logs sin contenido sensible: se registra método, ruta, status y duración; **no** el cuerpo del mensaje del usuario.
- [x] Tests (Vitest/Supertest): `/health` 200, 404 JSON, configuración inválida lanza error.
- [x] `npm test` en verde y `npm run dev` arranca con recarga (`node --watch`).

## Fuera de alcance
- Ruta `/api/chat`, CORS, Dockerfile y `docker-compose.yml` (US-GW-002 a US-GW-004).

## Definition of Done
- Todos los criterios marcados `[x]` y `npm test` en verde.
- ESLint sin warnings (si se añade; si no, documentar en el ADR).
- `node src/server.js` + `curl localhost:3000/health` devuelve `{"status":"ok"}`.
- ADR registrado en `docs/decisions/` (Express como framework HTTP del gateway).
- `.gitignore` cubre `node_modules/`; no hay secretos en el repo.
- Plan de implementación actualizado (checkbox, dashboard, barra de fase).
