# 🚀 CineMatch AI - Plan de Implementación

<!--
  Estados de US (el checkbox del título es la ÚNICA fuente de verdad):
    [ ]  Pendiente
    [~]  En progreso (solo UNA a la vez)
    [x]  Completada

  El workflow (TASK_EXECUTION.md) actualiza este archivo al cerrar cada US.
  Rutas relativas a `.claude/`.
-->

**Última actualización:** 2026-10-08
**Versión:** 1.6

---

## 📊 Dashboard General

```
┌─────────────────────────────────────────────────────────────┐
│  PROGRESO GLOBAL DEL PROYECTO                               │
├─────────────────────────────────────────────────────────────┤
│  Total Historias de Usuario:     18                         │
│  ✅ Completadas:                 16                         │
│  ⏳ En Progreso:                 0                          │
│  ⏸️  Pendientes:                 2                          │
│                                                             │
│  Progreso: [█████████░] 89% (16/18)                         │
└─────────────────────────────────────────────────────────────┘
```

<!--
  Barra de progreso de referencia (10 caracteres):
  0%   → [░░░░░░░░░░]    50%  → [█████░░░░░]
  10%  → [█░░░░░░░░░]    60%  → [██████░░░░]
  20%  → [██░░░░░░░░]    70%  → [███████░░░]
  30%  → [███░░░░░░░]    80%  → [████████░░]
  40%  → [████░░░░░░]    90%  → [█████████░]
                          100% → [██████████]
-->

---

## 🎯 Progreso por Épica

<!--
  Prefijos de ID del proyecto:
    INFRA → Infraestructura (Docker Compose, redes, Dockerfiles)
    MCP   → mcp-server (tools MCP sobre TMDB)
    AI    → ai-engine (agente LangGraph)
    GW    → api-gateway
    FE    → frontend
  Ejemplo: US-MCP-001, US-AI-003
-->

| Epic | Nombre | Total US | Completadas | En Progreso | Pendientes | Progreso |
|------|--------|----------|-------------|-------------|------------|----------|
| 01 | Infraestructura base | — | — | — | — | Desplegada fuera del plan (sin US) |
| 02 | MCP Server | 5 | 5 | 0 | 0 | [██████████] 100% |
| 03 | AI Engine | 5 | 5 | 0 | 0 | [██████████] 100% |
| 04 | API Gateway | 4 | 3 | 0 | 1 | [███████░░░] 75% |
| 05 | Frontend | 4 | 3 | 0 | 1 | [███████░░░] 75% |

---

## 📅 Plan de Implementación por Fases

---

# 🎯 FASE 1: FUNDACIÓN — Infraestructura base ✅

**Objetivo:** Contenedores y redes aisladas de Docker Compose levantados con servicios stub.
**Épicas:** 01 Infraestructura base
**Estado:** Completada antes de adoptar este plan; no tiene historias de usuario registradas.

Entregado:
- `docker-compose.yml` con los 4 servicios y las redes `public_network`, `internal_network` y `ai_network` (`internal: true`).
- Dockerfiles multi-stage con usuario sin privilegios (`appuser`) en cada servicio.
- Servicios stub: `frontend/index.js`, `api-gateway/index.js`, `ai-engine/main.py`, `mcp-server/main.py`.

---

# 🎯 FASE 2: DATOS — MCP Server sobre TMDB

**Objetivo:** Convertir el stub de `mcp-server/` en un servidor MCP real (Streamable HTTP) con tools de solo lectura sobre TMDB y fallback mock sin API key.
**Épicas:** 02 MCP Server
**Total US:** 5 (15 pts)
**Progreso:** [██████████] 100% (5/5)

---

## Epic 02: MCP Server - Tools MCP sobre la API de TMDB

**Prioridad:** CRÍTICA
**Carpeta:** `context/user_stories/epic_02_mcp_server/`
**Resumen de la épica:** `context/user_stories/epic_02_mcp_server/README.md`

Orden de ejecución: `001 → 002 → 003 → 004 → 005`. La 005 solo depende de la 001, pero se cierra al
final para validar la imagen con el servidor ya funcional.

### Historias de Usuario

#### [x] US-MCP-001: Entorno Python y dependencias del MCP Server
- **Archivo:** `context/user_stories/epic_02_mcp_server/US-MCP-001_python_environment/US-MCP-001_python_environment.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 2 pts
- **Dependencias:** Ninguna
- **Criterios de Aceptación:** 6

#### [x] US-MCP-002: Servidor MCP, cliente TMDB y fallback mock
- **Archivo:** `context/user_stories/epic_02_mcp_server/US-MCP-002_mcp_server_tmdb_client/US-MCP-002_mcp_server_tmdb_client.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 5 pts
- **Dependencias:** US-MCP-001
- **Criterios de Aceptación:** 16

#### [x] US-MCP-003: Tool `search_movies`
- **Archivo:** `context/user_stories/epic_02_mcp_server/US-MCP-003_search_movies_tool/US-MCP-003_search_movies_tool.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 3 pts
- **Dependencias:** US-MCP-002
- **Criterios de Aceptación:** 12

#### [x] US-MCP-004: Tool `get_movie_details`
- **Archivo:** `context/user_stories/epic_02_mcp_server/US-MCP-004_get_movie_details_tool/US-MCP-004_get_movie_details_tool.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 3 pts
- **Dependencias:** US-MCP-002
- **Criterios de Aceptación:** 10

#### [x] US-MCP-005: Instalación de dependencias en el Dockerfile del MCP Server
- **Archivo:** `context/user_stories/epic_02_mcp_server/US-MCP-005_dockerfile_dependencies/US-MCP-005_dockerfile_dependencies.md`
- **Prioridad:** ALTA
- **Estimación:** 2 pts
- **Dependencias:** US-MCP-001
- **Criterios de Aceptación:** 10

---

# 🎯 FASE 3: MOTOR COGNITIVO — AI Engine ✅

**Objetivo:** Convertir el stub de `ai-engine/` en un agente LangGraph que razona con un LLM, consume dinámicamente las tools del mcp-server y se expone como API FastAPI (`POST /chat`).
**Épicas:** 03 AI Engine
**Total US:** 5 (23 pts)
**Progreso:** [██████████] 100% (5/5)
**Resumen:** `context/summaries/phase-3-resume.md`

---

## Epic 03: AI Engine - Agente LangGraph que consume las tools MCP

**Prioridad:** CRÍTICA
**Carpeta:** `context/user_stories/epic_03_ai_engine/`
**Resumen de la épica:** `context/user_stories/epic_03_ai_engine/README.md`

Orden de ejecución: `001 → 002 → 003 → 004 → 005`.

### Historias de Usuario

#### [x] US-AI-001: Entorno Python y dependencias del AI Engine
- **Archivo:** `context/user_stories/epic_03_ai_engine/US-AI-001_python_environment/US-AI-001_python_environment.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 2 pts
- **Dependencias:** Ninguna
- **Criterios de Aceptación:** 8

#### [x] US-AI-002: Cliente MCP HTTP con descubrimiento dinámico de tools
- **Archivo:** `context/user_stories/epic_03_ai_engine/US-AI-002_mcp_http_client/US-AI-002_mcp_http_client.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 5 pts
- **Dependencias:** US-AI-001
- **Criterios de Aceptación:** 10

#### [x] US-AI-003: Agente LangGraph (razonar → tools → responder)
- **Archivo:** `context/user_stories/epic_03_ai_engine/US-AI-003_langgraph_agent/US-AI-003_langgraph_agent.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 8 pts
- **Dependencias:** US-AI-002
- **Criterios de Aceptación:** 10

#### [x] US-AI-004: API REST FastAPI: `POST /chat` y `GET /health`
- **Archivo:** `context/user_stories/epic_03_ai_engine/US-AI-004_fastapi_chat_endpoint/US-AI-004_fastapi_chat_endpoint.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 5 pts
- **Dependencias:** US-AI-003
- **Criterios de Aceptación:** 11

#### [x] US-AI-005: Dockerfile del AI Engine con venv y arranque de uvicorn
- **Archivo:** `context/user_stories/epic_03_ai_engine/US-AI-005_dockerfile_dependencies/US-AI-005_dockerfile_dependencies.md`
- **Prioridad:** ALTA
- **Estimación:** 3 pts
- **Dependencias:** US-AI-001, US-AI-004
- **Criterios de Aceptación:** 11

---

# 🎯 FASE 4: PUERTA DE ENTRADA — API Gateway y Frontend

**Objetivo:** Convertir los stubs de `api-gateway/` y `frontend/` en el camino público completo:
una SPA de chat (React 19 + Vite) que habla solo con un gateway Express, el cual aplica CORS/validación/límites y
reenvía `POST /api/chat` al ai-engine interno. Ambos servicios con Dockerfile multi-stage sin privilegios e integrados
en `docker-compose.yml`.
**Épicas:** 04 API Gateway, 05 Frontend
**Total US:** 8 (26 pts)
**Progreso:** [███████░░░] 75% (6/8)
**Estado:** Historias aprobadas; en desarrollo (US-GW-001/002/003 y US-FE-001/002/003 completadas; pruebas manuales y Lighthouse a cargo del Tech Lead con el stack Docker completo).

---

## EPIC 04: API Gateway — Punto de entrada público hacia el AI Engine

**Prioridad:** CRÍTICA
**Carpeta:** `context/user_stories/epic_04_api_gateway/`
**Resumen de la épica:** `context/user_stories/epic_04_api_gateway/README.md`

Orden de ejecución: `001 → 002 → 003 → 004`.

### Historias de Usuario

#### [x] US-GW-001: Proyecto Node/Express base y `GET /health`
- **Archivo:** `context/user_stories/epic_04_api_gateway/US-GW-001_express_setup/US-GW-001_express_setup.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 2 pts
- **Dependencias:** Ninguna
- **Criterios de Aceptación:** 11

#### [x] US-GW-002: `POST /api/chat` — validación y proxy al AI Engine
- **Archivo:** `context/user_stories/epic_04_api_gateway/US-GW-002_chat_proxy/US-GW-002_chat_proxy.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 5 pts
- **Dependencias:** US-GW-001
- **Criterios de Aceptación:** 10

#### [x] US-GW-003: CORS restrictivo y endurecimiento HTTP del gateway
- **Archivo:** `context/user_stories/epic_04_api_gateway/US-GW-003_cors_security/US-GW-003_cors_security.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 3 pts
- **Dependencias:** US-GW-001
- **Criterios de Aceptación:** 10

#### [ ] US-GW-004: Dockerfile multi-stage del gateway e integración en Compose
- **Archivo:** `context/user_stories/epic_04_api_gateway/US-GW-004_dockerfile_compose/US-GW-004_dockerfile_compose.md`
- **Prioridad:** ALTA
- **Estimación:** 3 pts
- **Dependencias:** US-GW-002, US-GW-003
- **Criterios de Aceptación:** 9

---

## EPIC 05: Frontend — Ventana de chat y recomendaciones de películas

**Prioridad:** CRÍTICA
**Carpeta:** `context/user_stories/epic_05_frontend/`
**Resumen de la épica:** `context/user_stories/epic_05_frontend/README.md`

Orden de ejecución: `001 → 002 → 003 → 004`.

### Historias de Usuario

#### [x] US-FE-001: Proyecto Vite + React 19 + TypeScript strict, tokens y tooling
- **Archivo:** `context/user_stories/epic_05_frontend/US-FE-001_vite_react_setup/US-FE-001_vite_react_setup.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 2 pts
- **Dependencias:** Ninguna
- **Criterios de Aceptación:** 10

#### [x] US-FE-002: Feature `chat` — modelos, servicio HTTP y hook `useChat`
- **Archivo:** `context/user_stories/epic_05_frontend/US-FE-002_chat_service_hook/US-FE-002_chat_service_hook.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 3 pts
- **Dependencias:** US-FE-001 (contrato de US-GW-002)
- **Criterios de Aceptación:** 9

#### [x] US-FE-003: UI de chat accesible con recomendaciones
- **Archivo:** `context/user_stories/epic_05_frontend/US-FE-003_chat_ui/US-FE-003_chat_ui.md`
- **Prioridad:** CRÍTICA
- **Estimación:** 5 pts
- **Dependencias:** US-FE-002
- **Criterios de Aceptación:** 19

#### [ ] US-FE-004: Dockerfile multi-stage (Vite → nginx sin privilegios) e integración en Compose
- **Archivo:** `context/user_stories/epic_05_frontend/US-FE-004_dockerfile_compose/US-FE-004_dockerfile_compose.md`
- **Prioridad:** ALTA
- **Estimación:** 3 pts
- **Dependencias:** US-FE-003, US-GW-004
- **Criterios de Aceptación:** 9

---

## 📝 Notas de Implementación

### Cómo usar este plan

1. **Seguir el orden de las fases** — la siguiente fase pendiente es la Fase 4 (en curso: 2/8)
2. **Trabajo incremental** — completar una US antes de avanzar
3. **Marcar progreso** con el checkbox del título: `[ ]` pendiente, `[~]` en progreso (solo UNA), `[x]` completada
4. **Actualizar métricas** — al cerrar cada US: dashboard, fila de la épica en la tabla, barra de la fase y "Última actualización"
5. **Leer el archivo de cada US** — contiene los criterios de aceptación detallados

### Riesgos conocidos (fuera del alcance de las US actuales)

- **Redes inconsistentes con la documentación:** `docs/architecture.md` dice que el mcp-server solo está en `ai_network` (sin internet), pero el compose también lo conecta a `internal_network` (con egress). Resolver en un ADR aparte.

### Cambios de seguridad recientes

- **Puerto del ai-engine cerrado (2026-10-08):** se eliminó el mapeo `8001:8000` de `docker-compose.yml`. El `ai-engine`
  vuelve a ser accesible **solo** desde `internal_network` (`http://ai-engine:8000`); el único camino público es
  frontend → api-gateway. Las pruebas de la Fase 3 que usaban el puerto 8001 deben hacerse con `docker compose exec`.
  El riesgo previo sobre `TMDB_API_KEY` se da por cerrado: el compose ya la pasa al `mcp-server` y la integración real con TMDB fue validada en la Fase 3.

### Referencias del proyecto

- **Historias de usuario:** `context/user_stories/`
- **Workflow de ejecución:** `@context/TASK_EXECUTION.md`
- **Resúmenes de fase:** `context/summaries/`
- **Arquitectura:** `docs/architecture.md`
- **Decisiones (ADRs):** `docs/decisions/`
- **Detalles técnicos:** `@CLAUDE.md`
