# mcp-server

Servidor MCP de CineMatch AI: expone tools de solo lectura sobre la API de TMDB al agente del
`ai-engine`. Arquitectura general en [`.claude/docs/architecture.md`](../.claude/docs/architecture.md).

## Servidor
- `FastMCP("cinematch-mcp")` con transporte **Streamable HTTP** en `http://<host>:8000/mcp`
  ([ADR-001](../.claude/docs/decisions/ADR-001-transporte-mcp-streamable-http.md)). No expone
  ninguna otra ruta HTTP y todas sus tools son de solo lectura.
- Arranque: `python main.py`.

```
main.py              ← entrypoint: logging, proveedor, servidor
config.py            ← Settings desde variables de entorno
server.py            ← create_server(): instancia FastMCP
providers/
├── __init__.py      ← create_provider(): TMDB si hay key, mock si no
├── base.py          ← MovieProvider (Protocol) + esquema normalizado (MovieSummary, MovieDetails)
├── errors.py        ← excepciones de dominio con mensajes seguros
├── genres.py        ← nombres de género (es/en) → id de TMDB, sin distinguir mayúsculas ni tildes
├── tmdb.py          ← TmdbProvider: httpx.AsyncClient único contra TMDB v3
└── mock.py          ← MockProvider: 12 películas en memoria
tools/
├── __init__.py      ← READ_ONLY: anotaciones comunes de las tools
├── errors.py        ← @handle_provider_errors: excepciones → ToolError legible
├── search_movies.py ← tool search_movies
└── get_movie_details.py ← tool get_movie_details
```

### Tools
| Tool | Parámetros | Salida |
|---|---|---|
| `search_movies` | `genre` (es/en), `keyword` (≤100 car.), `limit` (1-20, default 10); todos opcionales | `{source, results: [MovieSummary]}` |
| `get_movie_details` | `movie_id` (entero > 0, obligatorio): el `id` que devuelve `search_movies` | `{source, movie: MovieDetails}` |

`search_movies` elige el endpoint de TMDB según los filtros: sin ellos `/movie/popular`; solo `genre`
→ `/discover/movie`; con `keyword` → `/search/movie` (y, si hay `genre`, filtra por `genre_ids`).
El mapa de géneros (`/genre/movie/list`) se carga una vez por proceso. Un género desconocido
devuelve un error que lista los válidos; sin coincidencias devuelve `results: []`. En modo mock
aplica los mismos filtros sobre el catálogo en memoria.

`get_movie_details` hace una sola petición, `/movie/{id}?append_to_response=credits`. `director` son
los `credits.crew` con `job == "Director"` unidos con `", "` (`null` si no hay); `cast` son los 5
primeros de `credits.cast` por `order`. `overview` queda en `""` si TMDB no tiene sinopsis en el
idioma configurado, y `runtime`/`release_date` en `null` si TMDB no los conoce. `movie_id` se valida
de forma estricta (un `"157336"` o `157336.0` se rechaza) antes de llamar a TMDB; un id inexistente
devuelve «No se encontró la película con id X». En modo mock sirve las películas del catálogo en memoria.

### Variables de entorno
| Variable | Default | Descripción |
|---|---|---|
| `TMDB_API_KEY` | — | Ausente, vacía o solo espacios → **modo mock** (`WARNING TMDB_API_KEY not set — using mock data`) |
| `MCP_HOST` | `0.0.0.0` | Interfaz de escucha |
| `MCP_PORT` | `8000` | Puerto |
| `TMDB_TIMEOUT_SECONDS` | `10` | Timeout de cada petición a TMDB |
| `TMDB_LANGUAGE` | `es-ES` | Idioma de títulos, sinopsis y géneros |

Cada respuesta de las tools incluye `source: "tmdb" | "mock"`.

### Errores de TMDB
| Situación | Excepción | Mensaje al agente |
|---|---|---|
| 401 | `TmdbAuthError` | credenciales de TMDB inválidas |
| 404 | `MovieNotFoundError` | No se encontró la película solicitada |
| 429 | `TmdbRateLimitError` | Límite de peticiones de TMDB alcanzado; reintenta en N s |
| timeout, red, 5xx, otro 4xx | `TmdbUnavailableError` | TMDB no está disponible en este momento |

Cualquier otra excepción en una tool se registra en el log del servidor y llega al agente como un
mensaje genérico. La API key viaja como parámetro `api_key`; `TmdbProvider` la redacta (`***`)
de los logs de `httpx`/`httpcore` y nunca encadena las excepciones de httpx (su texto incluye la URL).

## Dependencias
- `requirements.txt` — runtime (lo que instala la imagen Docker):
  - `mcp>=1.30,<2` — SDK oficial de MCP. Se fija la rama **1.x** porque la 2.x renombró `FastMCP`
    a `MCPServer` y cambió otras APIs; migrar es una decisión aparte.
  - `httpx>=0.28,<1` — cliente HTTP async hacia TMDB.
- `requirements-dev.txt` — runtime + `pytest`, `pytest-asyncio` y `respx` (mock de `httpx`).

## Entorno local (Python 3.11)
```bash
cd mcp-server && python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && python -c "import mcp, httpx"
pytest tests/ -v
```

Sin Python 3.11 en el host, la misma verificación en un contenedor desechable:
```bash
docker run --rm -v "$PWD/mcp-server":/src:ro python:3.11-slim sh -c \
  "python -m venv /tmp/venv && . /tmp/venv/bin/activate && \
   pip install -q -r /src/requirements-dev.txt && pip check && \
   python -c 'import mcp, httpx' && cd /src && pytest -p no:cacheprovider"
```

Los tests nunca llaman a TMDB real: las peticiones se mockean con `respx`. `pytest.ini` activa
`asyncio_mode = auto`, así que los tests `async def` no necesitan decorador.
