# US-MCP-002: Servidor MCP, cliente TMDB y fallback mock

**Épica:** 02 — MCP Server
**Prioridad:** CRÍTICA
**Estimación:** 5 pts
**Dependencias:** US-MCP-001

## Historia de usuario
**Como** agente del ai-engine,
**quiero** conectarme a un servidor MCP que obtenga datos de TMDB, o datos mock si no hay API key,
**para** consultar películas sin hablar directamente con TMDB y sin que la falta de credenciales
bloquee el desarrollo.

## Contexto técnico
- `mcp-server/main.py` reemplaza el stub actual y es el entrypoint (`CMD ["python", "main.py"]`
  del Dockerfile, que no cambia).
- El ai-engine y el mcp-server están en contenedores distintos y se hablan por
  `http://mcp-server:8000` → transporte **Streamable HTTP**.
- Solo el mcp-server conoce `TMDB_API_KEY` (regla 2 de `CLAUDE.md`).
- API de TMDB v3: base `https://api.themoviedb.org/3`. Autenticación con el parámetro de query
  `api_key=<TMDB_API_KEY>`.

### Estructura de módulos propuesta
```
mcp-server/
├── main.py            ← crea FastMCP, elige proveedor, registra tools, arranca el servidor
├── config.py          ← lee variables de entorno (TMDB_API_KEY, host, puerto, timeout)
├── providers/
│   ├── base.py        ← interfaz MovieProvider (Protocol) + modelos normalizados
│   ├── tmdb.py        ← TmdbProvider: httpx.AsyncClient contra TMDB
│   └── mock.py        ← MockProvider: datos falsos en memoria
└── tests/
```
Las tools (US-MCP-003/004) dependen solo de la interfaz `MovieProvider`, no de la implementación concreta.

## Criterios de aceptación

### Servidor
- [x] `main.py` crea una instancia `FastMCP` llamada `cinematch-mcp` y la arranca con transporte
  Streamable HTTP en `0.0.0.0:8000` (host y puerto configurables con `MCP_HOST` / `MCP_PORT`).
- [x] El endpoint MCP queda en `http://<host>:8000/mcp` y responde al handshake `initialize` de un
  cliente MCP.
- [x] El servidor no expone ningún endpoint fuera de MCP ni tools de escritura (todas las tools son de solo lectura).

### Configuración y selección de proveedor
- [x] `config.py` lee `TMDB_API_KEY` del entorno; un valor vacío o solo con espacios se trata como ausente.
- [x] Con `TMDB_API_KEY` presente se usa `TmdbProvider`; si está ausente o vacía se usa `MockProvider`.
- [x] Al arrancar se registra un log claro del modo activo:
  `INFO  TMDB provider enabled` o `WARNING TMDB_API_KEY not set — using mock data`.
- [x] La API key nunca aparece en logs, mensajes de error ni respuestas de tools.

### Cliente TMDB (`TmdbProvider`)
- [x] Usa un único `httpx.AsyncClient` reutilizable con `base_url` de TMDB y timeout configurable
  (`TMDB_TIMEOUT_SECONDS`, default 10).
- [x] Envía `language=es-ES` por defecto (configurable con `TMDB_LANGUAGE`).
- [x] Traduce errores a excepciones de dominio con mensajes seguros:
  - 401 → `TmdbAuthError` ("credenciales de TMDB inválidas")
  - 404 → `MovieNotFoundError`
  - 429 → `TmdbRateLimitError` (incluye `Retry-After` si llega)
  - timeout / error de red / 5xx → `TmdbUnavailableError`
- [x] Las tools convierten estas excepciones en errores MCP legibles para el agente, sin stack traces.

### Proveedor mock (`MockProvider`)
- [x] Contiene al menos 10 películas de géneros variados con todos los campos del esquema normalizado
  (incluidos director y cast de al menos 3 personas).
- [x] Devuelve exactamente la misma forma de datos que `TmdbProvider`, para que el agente no note diferencia.
- [x] Cada respuesta en modo mock es identificable (p. ej. campo `source: "mock"` frente a `source: "tmdb"`).

### Documentación y tests
- [x] ADR `docs/decisions/` "Transporte MCP: Streamable HTTP" con contexto, decisión y consecuencias.
- [x] Tests en `tests/`: selección de proveedor según la variable (presente, ausente, vacía) y
  mapeo de errores HTTP de TMDB (con `respx`, sin llamadas reales a internet).

## Contrato: esquema normalizado compartido
```python
class MovieSummary(TypedDict):     # usado por search_movies
    id: int
    title: str
    release_year: int | None
    overview: str
    genres: list[str]
    vote_average: float
    poster_path: str | None        # ruta relativa de TMDB, el frontend elige el tamaño (w185, w342…)

class CastMember(TypedDict):
    name: str
    character: str

class MovieDetails(TypedDict):     # usado por get_movie_details
    id: int
    title: str
    overview: str
    director: str | None
    cast: list[CastMember]
    runtime: int | None
    genres: list[str]
    release_date: str | None       # ISO 8601
```

## Fuera de alcance
- Lógica de las tools (US-MCP-003 y US-MCP-004).
- Cambios en `docker-compose.yml` (pasar `TMDB_API_KEY` al contenedor).
- Caché de respuestas y reintentos automáticos.

## Definition of Done
- Criterios marcados `[x]`, ADR creado y `pytest tests/ -v` en verde.
- `python main.py` sin `TMDB_API_KEY` arranca en modo mock y un cliente MCP se conecta a `/mcp`.
