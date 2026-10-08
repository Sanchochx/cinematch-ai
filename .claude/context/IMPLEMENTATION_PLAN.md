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
**Versión:** 1.4

---

## 📊 Dashboard General

```
┌─────────────────────────────────────────────────────────────┐
│  PROGRESO GLOBAL DEL PROYECTO                               │
├─────────────────────────────────────────────────────────────┤
│  Total Historias de Usuario:     10                         │
│  ✅ Completadas:                 10                         │
│  ⏳ En Progreso:                 0                          │
│  ⏸️  Pendientes:                 0                          │
│                                                             │
│  Progreso: [██████████] 100% (10/10)                          │
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

# 🔭 PRÓXIMAS FASES (sin historias de usuario todavía)

Se añadirán a este plan cuando existan sus historias en `context/user_stories/`. Cada una requiere
antes las decisiones pendientes de `CLAUDE.md`, registradas como ADR en `docs/decisions/`.

| Fase | Épica prevista | Prefijo | Decisiones previas |
|------|----------------|---------|--------------------|
| 4 | API Gateway — `POST /api/chat` con validación, CORS y streaming | `US-GW` | Framework HTTP (Express/Fastify) |
| 5 | Frontend — UI de conversación y fichas de películas | `US-FE` | Bundler (Vite sugerido) |

---

## 📝 Notas de Implementación

### Cómo usar este plan

1. **Seguir el orden de las fases** — la siguiente fase pendiente es la Fase 4 (sin historias de usuario todavía)
2. **Trabajo incremental** — completar una US antes de avanzar
3. **Marcar progreso** con el checkbox del título: `[ ]` pendiente, `[~]` en progreso (solo UNA), `[x]` completada
4. **Actualizar métricas** — al cerrar cada US: dashboard, fila de la épica en la tabla, barra de la fase y "Última actualización"
5. **Leer el archivo de cada US** — contiene los criterios de aceptación detallados

### Riesgos conocidos (fuera del alcance de las US actuales)

- **`TMDB_API_KEY` no llega al contenedor:** `docker-compose.yml` no la pasa al `mcp-server`, así que en Docker el servidor arrancará en modo mock hasta que se añada (`env_file`/`environment`).
- **Redes inconsistentes con la documentación:** `docs/architecture.md` dice que el mcp-server solo está en `ai_network` (sin internet), pero el compose también lo conecta a `internal_network` (con egress). Resolver en un ADR aparte.

### Referencias del proyecto

- **Historias de usuario:** `context/user_stories/`
- **Workflow de ejecución:** `@context/TASK_EXECUTION.md`
- **Resúmenes de fase:** `context/summaries/`
- **Arquitectura:** `docs/architecture.md`
- **Decisiones (ADRs):** `docs/decisions/`
- **Detalles técnicos:** `@CLAUDE.md`
