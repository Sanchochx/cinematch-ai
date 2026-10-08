# 📋 FLUJO DE EJECUCIÓN DE TAREAS

<!--
  Manual de instrucciones para la IA — CineMatch AI.
  Rutas relativas a `.claude/`.
-->

**Versión:** 1.2
**Última actualización:** 2026-10-06

---

## 📁 Archivos de Contexto

Antes de comenzar cualquier tarea, revisar estos archivos:

- **`@context/IMPLEMENTATION_PLAN.md`** — Plan maestro con historias de usuario (US) y progreso por fases
- **`@CLAUDE.md`** — Detalles del proyecto, stack tecnológico y estándares de código
- **`docs/architecture.md`** — Servicios, redes de Docker Compose y flujo de una recomendación
- **`docs/decisions/`** — ADRs ya tomados (no contradecirlos; si una US exige una decisión nueva, crear su ADR)
- **`context/user_stories/epic_[NN]_[slug]/README.md`** — Resumen de la épica: decisiones, riesgos y orden de ejecución

> Todas las rutas de este documento, incluidas las que aparecen en `CLAUDE.md` (`docs/`, `context/`), son relativas a `.claude/`. Las carpetas de servicio (`frontend/`, `api-gateway/`, `ai-engine/`, `mcp-server/`) son relativas a la raíz del repo.

> En todo este documento, "el plan" = `@context/IMPLEMENTATION_PLAN.md`.

---

## 🔄 Proceso de Ejecución

### 1. Encontrar la siguiente US

- Si hay una US marcada `[~]` en el plan, **retómala primero**.
- Si no hay ninguna, toma la **primera US `[ ]`** del plan y márcala `[~]` antes de empezar (solo UNA `[~]` a la vez).
- Lee el archivo completo de la US: TODOS los criterios de aceptación y el campo **Dependencias** (si existe).
- Si una dependencia no está `[x]`, avisa al usuario antes de continuar.
- Lee también el `README.md` de la épica (decisiones tomadas y riesgos fuera de alcance).

```markdown
[~] US-MCP-001: Entorno Python y dependencias del MCP Server
```

---

### 2. Implementar cada criterio de aceptación

**Regla de oro:** trabaja los criterios **UNO A LA VEZ**.

Para cada criterio:

1. **Explica qué vas a construir y por qué** (objetivo y relación con la arquitectura).
2. **Crea/modifica archivos** solo dentro del servicio de la US (`frontend/`, `api-gateway/`, `ai-engine/` o `mcp-server/`), respetando la estructura existente.
3. **Aplica estándares y convenciones** de `CLAUDE.md`, manteniendo consistencia con el código existente.
4. **Actualiza la documentación afectada** (forma parte del alcance de la US). Si el criterio implica una decisión de arquitectura, crea el ADR en `docs/decisions/`.
5. **Marca el criterio `[x]`** en el archivo de la US al terminar.

```markdown
## Criterios de Aceptación

- [x] [Criterio completado]
- [ ] [Criterio pendiente]
```

---

### 3. Cerrar la US

Cuando TODOS los criterios estén `[x]`:

1. Recorre el **Checklist de Verificación** (al final de este documento) y ejecuta los comandos de la **Definition of Done** de la US.
2. En el plan: marca la US `[x]` (reemplaza `[~]`).
3. Actualiza el dashboard (contadores) y las barras de progreso de **épica** y **fase**.

```markdown
[x] US-MCP-001: Entorno Python y dependencias del MCP Server
```

---

### 4. Checkpoint (obligatorio)

Muestra un resumen y **detente a esperar confirmación**:

```
✅ US-MCP-001 Completada

Archivos creados/modificados:
- [ruta/archivo] - [propósito]

Funcionalidades:
- [Funcionalidad implementada]

Decisiones técnicas:
- [Decisión y motivo]

Verificación:
- [comando ejecutado] → [resultado]

¿Proceder con US-MCP-002?
```

- No avances a la siguiente US sin aprobación explícita del usuario.
- No hagas nada fuera de este flujo mientras esperas.

---

### 5. Resumen de fase (solo si corresponde)

**Cuándo:** al completar TODAS las US de una **fase** (después del checkpoint de la última US).

**Dónde y nombre:** `context/summaries/phase-[N]-resume.md`

**Contenido:**

- **📝 Changes Made:** módulos, funcionalidades core e integraciones de la fase.
- **📂 Files Modified/Created:** ruta, propósito y cambios principales de cada archivo.
- **🎯 Rationale:** qué se completó y por qué, cómo encaja en la arquitectura, decisiones de diseño y patrones usados.
- **🚀 Next Steps:** fase siguiente, dependencias y consideraciones.

**Propósito:** que futuras sesiones de LLM entiendan el estado del proyecto sin releer todo el código.

---

## ⚠️ Guías Importantes

- **Arquitectura:** sigue `CLAUDE.md` (arquitectura, estándares, organización de archivos, nombres).
- **Trabajo incremental:** un criterio a la vez; una US a la vez.
- **Commits:** no hagas commits a menos que el usuario lo pida. Si lo pide, que sean pequeños y atómicos (uno por criterio), con Conventional Commits y el servicio como scope (`feat(mcp-server): ...`).
- **Testing:** toda ruta del gateway, nodo del grafo y tool MCP nueva lleva su test (regla 3 de `CLAUDE.md`). Fuera de eso, escribe solo los tests que pida la US. Nunca llames a TMDB ni al LLM real en los tests: usa mocks (`respx` para `httpx`).
- **Secretos:** nada de credenciales hardcodeadas; cada servicio recibe solo sus variables (`TMDB_API_KEY` solo en `mcp-server`).
- **Docker:** los Dockerfiles mantienen multi-stage y usuario sin privilegios (`appuser`).
- **Dudas:** si un criterio es ambiguo o choca con la arquitectura existente, pregunta antes de implementar.
- **Alcance:** no modifiques archivos fuera del alcance de la US actual.

---

## 🎯 Buenas Prácticas

### ✅ HACER
- Leer toda la US antes de comenzar
- Seguir el orden del plan
- Marcar el progreso en tiempo real
- Explicar decisiones técnicas

### ❌ NO HACER
- Saltarte US
- Trabajar en varias US a la vez
- Asumir implementaciones sin revisar criterios
- Avanzar sin autorización del usuario

---

## 🔍 Checklist de Verificación

Antes de marcar una US como completa:

- [ ] Todos los criterios de aceptación están `[x]`
- [ ] Los archivos están en los directorios correctos
- [ ] El código sigue los estándares de `CLAUDE.md`
- [ ] Los tests del servicio pasan (`pytest tests/ -v` / `npm test`)
- [ ] La imagen construye si la US toca el Dockerfile (`docker compose build <servicio>`)
- [ ] No se filtran secretos en código, logs ni respuestas
- [ ] La documentación está actualizada
- [ ] No hay código comentado sin razón
- [ ] Las funcionalidades cumplen los criterios

---

## 📌 Referencia Rápida

| Archivo | Propósito |
|---------|-----------|
| `@context/IMPLEMENTATION_PLAN.md` | Plan maestro con todas las US y progreso |
| `@CLAUDE.md` | Detalles técnicos y estándares del proyecto |
| `docs/architecture.md` | Servicios, redes y flujo de una recomendación |
| `docs/decisions/` | ADRs |
| `context/user_stories/` | Archivos individuales de historias de usuario (una carpeta por épica) |
| `context/summaries/` | Resúmenes de fase |

### Comandos de verificación por servicio

| Servicio | Tests | Build / arranque |
|----------|-------|------------------|
| `mcp-server` | `cd mcp-server && source .venv/bin/activate && pytest tests/ -v` | `docker compose build mcp-server && docker compose up mcp-server` |
| `ai-engine` | `cd ai-engine && source .venv/bin/activate && pytest tests/ -v` | `docker compose up --build ai-engine` |
| `api-gateway` | `cd api-gateway && npm test` | `docker compose up --build api-gateway` |
| `frontend` | `cd frontend && npm test` | `docker compose up --build frontend` |

---

**Importante:** flujo diseñado para trabajo incremental y colaborativo. Siempre espera confirmación del usuario antes de pasar a la siguiente US.