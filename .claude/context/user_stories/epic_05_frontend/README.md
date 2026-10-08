# Epic 05: Frontend — Ventana de chat y recomendaciones de películas

**Fase:** 4
**Prioridad:** CRÍTICA
**Prefijo de ID:** `US-FE`
**Carpeta:** `context/user_stories/epic_05_frontend/`

## Objetivo
Convertir el stub de `frontend/` en una SPA moderna y sencilla (React 19 + TypeScript + Vite) con una
ventana de chat donde el usuario describe sus gustos y ve las recomendaciones del agente. El frontend
habla **solo** con el api-gateway (`POST /api/chat`).

## Estado de partida
- `frontend/index.js` es un stub; `frontend/Dockerfile` multi-stage con `builder` vacío y `USER node`.
- No existe `package.json`, código fuente ni tests.
- `docker-compose.yml` publica `5173:3000` y conecta el frontend a `public_network`.
- El contrato del gateway (épica 04) es `POST /api/chat` `{message, history?}` → `{reply}`.

## Historias de usuario

| ID | Historia | Prioridad | Estimación | Dependencias |
|----|----------|-----------|------------|--------------|
| [US-FE-001](US-FE-001_vite_react_setup/US-FE-001_vite_react_setup.md) | Proyecto Vite + React 19 + TS strict, tokens y tooling | CRÍTICA | 2 pts | Ninguna |
| [US-FE-002](US-FE-002_chat_service_hook/US-FE-002_chat_service_hook.md) | Feature `chat`: modelos, servicio HTTP y hook `useChat` | CRÍTICA | 3 pts | US-FE-001, contrato de US-GW-002 |
| [US-FE-003](US-FE-003_chat_ui/US-FE-003_chat_ui.md) | UI de chat accesible con recomendaciones | CRÍTICA | 5 pts | US-FE-002 |
| [US-FE-004](US-FE-004_dockerfile_compose/US-FE-004_dockerfile_compose.md) | Dockerfile multi-stage (Vite → nginx sin privilegios) e integración en Compose | ALTA | 3 pts | US-FE-003, US-GW-004 |

**Total:** 4 US · 13 pts

Orden de ejecución sugerido: `001 → 002 → 003 → 004`. Las US-FE-001/002/003 pueden desarrollarse contra un
mock del gateway; la integración real ocurre en US-FE-004 (requiere US-GW-004).

## Decisiones propuestas (registrar como ADR en `docs/decisions/` al implementar)
- **Bundler: Vite + React 19 + TypeScript strict** (ya sugerido en `CLAUDE.md`). Descartado HTML/Vanilla JS:
  los estándares del proyecto exigen componentes tipados, hooks, CSS Modules y tests con Testing Library.
- **Servidor en producción: `nginxinc/nginx-unprivileged`** sirviendo el build estático en el puerto 3000
  (el compose ya mapea `5173:3000`). Alternativa descartada: `vite preview` (no apto para producción).
- **Estado local** (`useState`/`useReducer` dentro de `useChat`); sin Zustand porque el estado no cruza features.
- **Sin dependencias de UI pesadas**: CSS Modules + tokens; sin Framer Motion (solo transiciones CSS).
- **Tests: Vitest + Testing Library**; E2E con Playwright queda como tarea posterior (ver fuera de alcance).

## Puntos a validar en la revisión técnica
1. **El contrato solo devuelve texto (`reply: string`).** El ai-engine no entrega datos estructurados
   (título, póster, año), por lo que la v1 **renderiza el texto de la recomendación** (párrafos y listas,
   sin HTML crudo). Mostrar *fichas con póster* requiere ampliar el contrato `{reply, movies[]}` en
   ai-engine + gateway → se propone como historia futura, **no** se incluye aquí.
2. **URL del gateway en el navegador:** el navegador no resuelve `api-gateway`; debe llamar a
   `http://localhost:3000`. Vite inlinea `VITE_API_URL` en **build time** → se pasa como `build.args` en Compose.
3. **CORS:** el origen del frontend (`http://localhost:5173`) debe coincidir con `CORS_ORIGIN` del gateway.
4. **Historial:** el frontend es dueño del historial y lo reenvía en cada request (máx. 20 ítems; se recorta
   a los más recientes). No se persiste entre recargas en esta fase.
5. **Idioma:** textos de UI en español; identificadores/archivos en inglés (`CLAUDE.md`).

## Fuera de alcance de la épica
- Fichas con póster/metadatos (requiere cambio de contrato), streaming de tokens, autenticación,
  persistencia de conversaciones, modo oscuro, internacionalización, E2E con Playwright, PWA.
