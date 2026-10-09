# CineMatch AI

## Descripción
Recomendador de películas basado en **IA agéntica**. Un agente construido con LangGraph
conversa con el usuario, entiende sus gustos y consulta TMDB a través de un servidor MCP
para devolver recomendaciones fundamentadas en datos reales.

Arquitectura de **microservicios contenerizados** (Docker Compose) con aislamiento de redes.
Los cuatro servicios están implementados y orquestados con Docker Compose (Fase 4 completada).

## Stack
| Servicio | Carpeta | Tecnología | Puerto interno |
|---|---|---|---|
| Frontend | `frontend/` | React 19 + TypeScript | 3000 (host: 5173) |
| API Gateway | `api-gateway/` | Node.js 20 | 3000 (host: 3000) |
| AI Engine | `ai-engine/` | Python 3.11 + LangGraph | 8000 |
| MCP Server | `mcp-server/` | Python 3.11 + SDK oficial de MCP (`mcp`) | 8000 |
| Datos externos | — | API de TMDB | — |

**Pendiente de decidir** (registrar como ADR en `docs/decisions/` al decidirlo):
- Persistencia de historial y perfiles de usuario (hoy sin checkpointer: el cliente envía `history`)
- Autenticación de usuarios
- Restricción de egress (proxy con allowlist a OpenAI y TMDB) para ai-engine y mcp-server

**Decidido:**
- Transporte MCP entre AI Engine y MCP Server: Streamable HTTP en `/mcp` ([ADR-001](docs/decisions/ADR-001-transporte-mcp-streamable-http.md))
- LLM (OpenAI) y agente sin checkpointer ([ADR-002](docs/decisions/ADR-002-proveedor-llm-y-agente-sin-checkpointer.md))
- AI Engine: FastAPI + uvicorn ([ADR-003](docs/decisions/ADR-003-fastapi-uvicorn-ai-engine.md))
- API Gateway: Express ([ADR-004](docs/decisions/ADR-004-express-api-gateway.md))
- Frontend: Vite + React ([ADR-005](docs/decisions/ADR-005-vite-react-frontend.md)), servido con nginx-unprivileged
- Variable de build del frontend: `VITE_API_URL` (build arg en Compose, por defecto `http://localhost:3000`); la CSP de `frontend/nginx.conf` debe coincidir

## Arquitectura y redes
```
[Navegador] ──► frontend ──► api-gateway ──► ai-engine ──► mcp-server ──► TMDB
               public_network   │  internal_network   ai_network (internal)
                                └──────────────────┘
```
- `public_network`: frontend ↔ api-gateway (expuestos al host)
- `internal_network`: api-gateway ↔ ai-engine (el ai-engine NO se expone al host). Bridge con egress: ai-engine (LLM) y mcp-server (TMDB) también están aquí para salir a internet
- `ai_network` (`internal: true`, sin internet): tráfico ai-engine ↔ mcp-server
- Solo `frontend` (5173) y `api-gateway` (3000) publican puertos; ai-engine y mcp-server nunca

Reglas:
- El frontend **solo** habla con el api-gateway. Nunca con ai-engine ni mcp-server.
- Solo el mcp-server habla con TMDB. El agente accede a películas únicamente vía tools MCP.
- Los servicios se comunican por nombre de servicio de Compose (`http://ai-engine:8000`), nunca por IP.

Detalle completo: [docs/architecture.md](docs/architecture.md)

## Comandos clave
```bash
# Levantar todo
docker compose up --build
docker compose up --build <servicio>     # uno solo: frontend | api-gateway | ai-engine | mcp-server

# Logs / estado
docker compose logs -f <servicio>
docker compose ps

# Bajar
docker compose down
```

Desarrollo local por servicio (cuando existan los manifiestos):
```bash
# Frontend / API Gateway
cd frontend && npm install && npm run dev
cd api-gateway && npm install && npm run dev
npm test

# AI Engine / MCP Server
cd ai-engine && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Estructura del proyecto
```
cinematch-ai/
├── docker-compose.yml
├── frontend/        ← React 19 (estructura por feature, ver Frontend Standards)
├── api-gateway/     ← Node: rutas → servicios → cliente HTTP al ai-engine
├── ai-engine/       ← LangGraph: grafo del agente, nodos, estado, cliente MCP
├── mcp-server/      ← tools MCP sobre la API de TMDB
└── .claude/         ← memoria, skills, hooks, docs y plan de implementación
```
Cada servicio tiene su propio manifiesto (`package.json` / `requirements.txt`), sus tests en
`tests/` y su `Dockerfile` multi-stage que corre con usuario sin privilegios.

## Convenciones de código

### Nombres
- Variables y funciones: `snake_case` (Python) / `camelCase` (JS/TS)
- Clases y componentes React: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Rutas API: `/kebab-case`
- Tools MCP: `snake_case` con verbo (`search_movies`, `get_movie_details`)
- Archivos: `snake_case.py` / `camelCase.ts` / `PascalCase.tsx` (componentes)

### Commits (Conventional Commits)
El scope es el servicio o la feature:
```
feat(ai-engine): agregar nodo de extracción de preferencias
fix(mcp-server): manejar rate limit de TMDB
refactor(api-gateway): extraer cliente del ai-engine
```

### Ramas
- `main` → producción
- `develop` → integración
- `feature/nombre-descriptivo`
- `fix/nombre-del-bug`

## Reglas importantes
1. No hardcodear credenciales — variables de entorno (`.env`, nunca versionado).
2. Cada servicio recibe **solo** los secretos que necesita (la API key de TMDB solo al mcp-server).
3. Toda ruta del gateway, nodo del grafo y tool MCP nueva requiere su test.
4. Documentar decisiones de arquitectura en `docs/decisions/`.
5. Revisar con el skill `code-review` antes de hacer merge.
6. Gateway: patrón modelo → servicio → ruta → test.
7. Los Dockerfiles mantienen multi-stage + usuario sin privilegios.

## Variables de entorno
```env
# api-gateway
PORT=3000
AI_ENGINE_URL=http://ai-engine:8000
CORS_ORIGIN=http://localhost:5173   # allowlist exacta, lista separada por comas; `*` rechazado; obligatoria con NODE_ENV=production
AI_ENGINE_TIMEOUT_MS=30000      # opcional
RATE_LIMIT_MAX=20               # opcional; peticiones por IP y ventana en /api/chat
RATE_LIMIT_WINDOW_MS=60000      # opcional

# ai-engine
OPENAI_API_KEY=...              # clave del LLM (langchain-openai)
LLM_MODEL=gpt-4o-mini           # opcional
ENABLE_DOCS=false               # opcional; true expone /docs en el ai-engine
MCP_SERVER_URL=http://mcp-server:8000/mcp
MCP_TIMEOUT_SECONDS=10          # opcional

# mcp-server
TMDB_API_KEY=...                 # vacía/ausente → modo mock
MCP_HOST=0.0.0.0                # opcional
MCP_PORT=8000                   # opcional
TMDB_TIMEOUT_SECONDS=10         # opcional
TMDB_LANGUAGE=es-ES             # opcional
```

## Contexto adicional
- [docs/architecture.md](docs/architecture.md)
- [context/IMPLEMENTATION_PLAN.md](context/IMPLEMENTATION_PLAN.md) y [context/TASK_EXECUTION.md](context/TASK_EXECUTION.md)
- API de TMDB: https://developer.themoviedb.org/docs

## Frontend Standards (React 19)

### Filosofía
Cada UI debe ser production-grade: accesible, performante, mantenible y visualmente
intencional. El código debe poder pasar un code review en un equipo senior.

### Arquitectura de Componentes
- **Separación de responsabilidades**: custom hooks para la lógica, componentes solo para renderizado
- **Componentes pequeños y enfocados**: max ~150 líneas, una sola responsabilidad
- **Props tipadas siempre**: TypeScript strict, sin `any`
- **Composición sobre herencia**
- Estructura de carpeta por feature, no por tipo:
```
  feature/
  ├── components/     ← UI puro, sin lógica de negocio
  ├── services/       ← llamadas HTTP (solo al api-gateway)
  ├── models/         ← interfaces y tipos
  ├── hooks/          ← estado y lógica
  └── index.ts        ← barrel export
```

### TypeScript
- `strict: true` siempre en tsconfig
- Interfaces para objetos de dominio, types para uniones/utilidades
- Sin `any` — usar `unknown` + type guards si es necesario
- Tipar explícitamente returns de funciones y hooks públicos
- Enums solo cuando los valores tienen significado semántico real

### Estilos y CSS
- **Design tokens primero**: definir variables en `:root` (spacing base 4px, type scale con
  `clamp()`, colores `--color-*`, radios `--radius-*`, sombras `--shadow-*`) antes de escribir estilos
- **CSS Modules**
- **Fluid layout**: CSS Grid para estructura, Flexbox para alineación lineal
- Mobile-first: estilos base para móvil, `@media (min-width: ...)` para crecer
- `clamp()` para todo lo que necesite escalar: font-size, padding, gap

### Accesibilidad (a11y) — No negociable
- Todo elemento interactivo alcanzable con `Tab` y operable con `Enter/Space`
- Imágenes (pósters) con `alt` descriptivo o `alt=""` si son decorativas
- Formularios: `<label>` asociado a cada input (no solo placeholder)
- Contraste mínimo WCAG AA: 4.5:1 texto normal, 3:1 texto grande
- Roles ARIA solo cuando HTML semántico no alcanza; respuestas del agente en streaming con `aria-live`
- `focus-visible` estilizado — nunca `outline: none` sin reemplazo
- Respetar `prefers-reduced-motion`

### Performance — Core Web Vitals
- **LCP < 2.5s**: imágenes above-the-fold con `loading="eager"`, resto `loading="lazy"`
- **CLS = 0**: reservar espacio para pósters y contenido async con dimensiones explícitas
- **INP < 200ms**: evitar trabajo pesado en el hilo principal
- Lazy loading de rutas con `React.lazy`; bundle splitting por feature
- Pósters de TMDB: pedir el tamaño adecuado (`w185`, `w342`…), no escalar con CSS
- Fuentes: `font-display: swap`, preload de fuentes críticas

### Estado
- **Local first**: `useState` para estado que no necesita compartirse
- **State lifting** cuando 2+ componentes comparten estado
- **Global store** (Zustand) solo cuando el estado cruza features sin relación directa
- Nunca mutar estado directamente

### Formularios
- Validación en el modelo, no en el JSX
- Mensajes de error accesibles: `aria-describedby` apuntando al mensaje
- Estados visuales claros: default → focus → valid → error → disabled

### Animaciones
- CSS transitions para estado simple; Framer Motion solo para secuencias complejas
- Animar solo `transform`, `opacity`, `filter` — nunca `width`, `height`, `top`, `left`
- 150-200ms micro-interacciones, 300-400ms transiciones de vista

### Calidad de código
- ESLint + Prettier sin warnings en CI
- Nombres en inglés: componentes, variables, funciones, archivos
- Comentarios solo para el **por qué**
- Sin `console.log` en producción
- Todo componente nuevo requiere al menos un test de renderizado (Vitest + Testing Library)
- E2E con Playwright
