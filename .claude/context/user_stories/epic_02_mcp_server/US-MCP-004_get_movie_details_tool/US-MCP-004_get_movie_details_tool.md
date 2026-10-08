# US-MCP-004: Tool `get_movie_details`

**Épica:** 02 — MCP Server
**Prioridad:** CRÍTICA
**Estimación:** 3 pts
**Dependencias:** US-MCP-002

## Historia de usuario
**Como** agente del ai-engine,
**quiero** obtener la sinopsis, el director y el cast principal de una película a partir de su ID,
**para** justificar mis recomendaciones con datos concretos.

## Contexto técnico
- Se registra con `@mcp.tool()` y llama solo a la interfaz `MovieProvider`.
- Una sola llamada a TMDB: `GET /movie/{movie_id}?append_to_response=credits`
  (detalles + `credits.cast` + `credits.crew` en una petición).
- El `movie_id` es el que devuelve `search_movies` (ID de TMDB).

## Contrato
**Nombre:** `get_movie_details`

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|-------------|-------------|
| `movie_id` | `int` | Sí | ID de TMDB de la película (entero > 0) |

**Salida:** `{"source": "tmdb" | "mock", "movie": MovieDetails}` (esquema en US-MCP-002).

## Criterios de aceptación
- [x] La tool aparece en `tools/list` con el nombre `get_movie_details`, descripción clara y
  `movie_id` marcado como obligatorio.
- [x] Hace una sola petición a TMDB con `append_to_response=credits`.
- [x] `overview` contiene la sinopsis; si TMDB la devuelve vacía en el idioma configurado, se usa
  la cadena vacía (sin inventar texto).
- [x] `director` es el `name` del primer miembro de `credits.crew` con `job == "Director"`;
  si hay varios se unen con `", "`; si no hay ninguno, `null`.
- [x] `cast` contiene los 5 primeros de `credits.cast` ordenados por `order`, cada uno con
  `name` y `character` (menos de 5 si TMDB tiene menos).
- [x] Incluye `runtime`, `genres` (nombres) y `release_date`.
- [x] `movie_id` ≤ 0 o no entero → error de validación sin llamar a TMDB.
- [x] Película inexistente (404) → error "No se encontró la película con id X".
- [x] En modo mock devuelve los detalles de la película mock con ese id, o el mismo error de no encontrada.
- [x] Tests en `tests/test_get_movie_details.py` (TMDB simulado con `respx`):
  caso feliz, película sin director, cast con menos de 5, varios directores, id inválido,
  404, modo mock, error 401/5xx.

## Ejemplo
```json
// get_movie_details(movie_id=157336)
{
  "source": "tmdb",
  "movie": {
    "id": 157336, "title": "Interstellar",
    "overview": "Un grupo de exploradores viaja a través de un agujero de gusano…",
    "director": "Christopher Nolan",
    "cast": [
      {"name": "Matthew McConaughey", "character": "Cooper"},
      {"name": "Anne Hathaway", "character": "Brand"}
    ],
    "runtime": 169, "genres": ["Aventura", "Drama", "Ciencia ficción"],
    "release_date": "2014-11-05"
  }
}
```

## Fuera de alcance
- Películas similares, proveedores de streaming, tráilers o reseñas (futuras tools).

## Definition of Done
- Criterios marcados `[x]` y `pytest tests/test_get_movie_details.py -v` en verde.
- Probada manualmente con MCP Inspector en modo mock (y en modo TMDB si hay key).
