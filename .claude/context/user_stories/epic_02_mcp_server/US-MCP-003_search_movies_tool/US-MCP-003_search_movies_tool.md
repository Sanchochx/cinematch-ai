# US-MCP-003: Tool `search_movies`

**Épica:** 02 — MCP Server
**Prioridad:** CRÍTICA
**Estimación:** 3 pts
**Dependencias:** US-MCP-002

## Historia de usuario
**Como** agente del ai-engine,
**quiero** buscar películas por género y/o palabra clave,
**para** reunir candidatas reales antes de recomendar algo al usuario.

## Contexto técnico
- Se registra con `@mcp.tool()` en el servidor de US-MCP-002 y llama solo a la interfaz `MovieProvider`.
- Endpoints de TMDB:
  - `GET /search/movie?query=<keyword>` — búsqueda por texto.
  - `GET /genre/movie/list` — mapa nombre → id de géneros (se cachea en memoria durante la vida del proceso).
  - `GET /discover/movie?with_genres=<id>&sort_by=popularity.desc` — filtrado por género.
  - `GET /movie/popular` — sin filtros.
- La docstring de la tool es lo que lee el LLM: debe explicar parámetros, combinaciones y forma de la salida.

## Contrato
**Nombre:** `search_movies`

| Parámetro | Tipo | Obligatorio | Default | Descripción |
|-----------|------|-------------|---------|-------------|
| `genre` | `str \| None` | No | `None` | Nombre del género (`"ciencia ficción"`, `"Science Fiction"`, `"terror"`…), sin distinguir mayúsculas ni tildes |
| `keyword` | `str \| None` | No | `None` | Texto libre: título o palabra clave (máx. 100 caracteres) |
| `limit` | `int` | No | `10` | Número máximo de resultados, entre 1 y 20 |

**Salida:** `{"source": "tmdb" | "mock", "results": list[MovieSummary]}` (esquema en US-MCP-002).

## Criterios de aceptación
- [x] La tool aparece en `tools/list` con el nombre `search_movies`, descripción clara y JSON Schema
  de sus tres parámetros opcionales.
- [x] Solo `keyword` → usa `/search/movie` y devuelve hasta `limit` resultados.
- [x] Solo `genre` → resuelve el id con `/genre/movie/list` y usa `/discover/movie`.
- [x] `genre` + `keyword` → usa `/search/movie` y filtra por `genre_ids` del género pedido.
- [x] Sin parámetros → devuelve películas populares (`/movie/popular`).
- [x] La resolución de género ignora mayúsculas y tildes y acepta nombres en español e inglés.
- [x] Género desconocido → error descriptivo que lista los géneros válidos (sin llamar a discover).
- [x] `limit` fuera de 1–20 o `keyword` vacío / de más de 100 caracteres → error de validación.
- [x] Los `genre_ids` de TMDB se convierten a nombres en `genres`; `release_date` se reduce a `release_year`.
- [x] Sin resultados → `results: []` (no es un error).
- [x] En modo mock se aplican los mismos filtros sobre los datos falsos.
- [x] Tests en `tests/test_search_movies.py` (TMDB simulado con `respx`):
  solo keyword, solo género, ambos, sin parámetros, género inválido, `limit` inválido,
  resultados vacíos, modo mock, error 429/5xx de TMDB.

## Ejemplo
```json
// search_movies(genre="ciencia ficción", keyword="espacio", limit=2)
{
  "source": "tmdb",
  "results": [
    {"id": 157336, "title": "Interstellar", "release_year": 2014, "overview": "…",
     "genres": ["Aventura", "Drama", "Ciencia ficción"], "vote_average": 8.4,
     "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"}
  ]
}
```

## Fuera de alcance
- Paginación más allá de la primera página de TMDB.
- Filtros adicionales (año, duración, idioma, puntuación mínima): futuras tools o parámetros.

## Definition of Done
- Criterios marcados `[x]` y `pytest tests/test_search_movies.py -v` en verde.
- Probada manualmente con MCP Inspector en modo mock (y en modo TMDB si hay key).
