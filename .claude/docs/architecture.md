# Arquitectura — CineMatch AI

## Visión general
Recomendador de películas basado en IA agéntica. El usuario conversa desde el frontend;
el api-gateway reenvía la conversación al ai-engine, donde un agente LangGraph decide
qué datos necesita y los obtiene llamando tools del mcp-server, que a su vez consulta TMDB.

Cada servicio corre en su propio contenedor (Docker Compose), con imágenes multi-stage
y usuario sin privilegios.

## Topología de red real (Zero Trust por segmentación)
```
                         host
                  :5173        :3000
                    │            │
  ┌──────── public_network ──────┼──────┐
  │  frontend (nginx, uid 101) ──┤      │   El navegador solo ve estos dos puertos
  │                      api-gateway    │
  └──────────────────────────┬──────────┘
                             │ http://ai-engine:8000
  ┌──────── internal_network ┼──────────┐   bridge con salida a internet (egress)
  │              ai-engine ──┘          │   ai-engine → LLM (OpenAI)
  │              mcp-server             │   mcp-server → TMDB
  └─────────┬──────────────┬────────────┘
  ┌──────── ai_network (internal: true, sin internet) ──┐
  │   ai-engine ── http://mcp-server:8000/mcp ── mcp-server │
  └─────────────────────────────────────────────────────┘
```

| Servicio | Redes | Puerto publicado | Secretos |
|---|---|---|---|
| frontend | `public_network` | 5173 → 3000 | ninguno |
| api-gateway | `public_network`, `internal_network` | 3000 | ninguno |
| ai-engine | `internal_network`, `ai_network` | — | `OPENAI_API_KEY` |
| mcp-server | `ai_network`, `internal_network` | — | `TMDB_API_KEY` |

Principios aplicados:
- **El gateway es el único puente** entre el exterior y el motor de IA; el frontend no tiene ruta a ai-engine ni mcp-server.
- **ai-engine y mcp-server no publican puertos** al host; solo son alcanzables por nombre de servicio dentro de sus redes.
- **El tráfico agente ↔ tools viaja por `ai_network`**, que no tiene salida a internet.
- **Matiz importante:** ambos servicios también están en `internal_network` (bridge normal) porque necesitan egress
  (LLM y TMDB). Por tanto, el aislamiento es de *entrada* (nadie externo los alcanza), no de *salida*. Restringir el
  egress (proxy con allowlist a `api.openai.com` y `api.themoviedb.org`) queda como mejora futura.

## Responsabilidades por servicio

| Servicio | Responsabilidad | NO hace |
|---|---|---|
| frontend | UI de conversación y fichas de películas | Llamar a otro servicio que no sea el gateway |
| api-gateway | Punto de entrada único: validación de input, CORS, rate limiting, (futuro) auth, proxy/streaming hacia el ai-engine | Lógica de recomendación |
| ai-engine | Grafo LangGraph: entender preferencias, planificar, llamar tools MCP, razonar y redactar la recomendación | Llamar a TMDB directamente |
| mcp-server | Exponer tools MCP sobre TMDB (búsqueda, detalles, géneros, similares…) y normalizar sus respuestas | Decidir qué recomendar |

## Flujo de una recomendación
1. El usuario escribe "algo como Interstellar pero más corto" en el frontend.
2. El frontend hace `POST /api/chat` al api-gateway.
3. El gateway valida el body (Zod), aplica CORS y rate limit, y lo reenvía a `http://ai-engine:8000`.
4. El agente LangGraph extrae preferencias y decide qué tools llamar.
5. El ai-engine invoca tools en el mcp-server (`search_movies`, `get_similar_movies`…).
6. El mcp-server consulta TMDB y devuelve datos normalizados.
7. El agente filtra, razona y genera la respuesta con las películas recomendadas.
8. La respuesta vuelve (idealmente en streaming) gateway → frontend.

## Consideraciones de seguridad
- **Exposición mínima**: solo frontend y gateway publican puertos al host.
- **Secretos por servicio**: `TMDB_API_KEY` solo en mcp-server; la key del LLM solo en ai-engine; el gateway y el frontend no reciben ninguna.
- **Superficie del agente**: el agente solo puede actuar mediante las tools MCP definidas; las tools son de solo lectura.
- **Gateway**: validación Zod (límites de tamaño, claves extra descartadas), Helmet, CORS con allowlist exacta (`*` rechazado), rate limit por IP en `/api/chat`, errores genéricos.
- **Frontend**: nginx-unprivileged (uid 101), CSP con `connect-src` limitado al gateway, `frame-ancestors 'none'`, `X-Content-Type-Options`, `X-Frame-Options`.
- **Contenedores**: imágenes multi-stage, todas con usuario sin privilegios.
- Autenticación de usuarios: pendiente de decidir.

## ⚠️ Puntos abiertos
- **Egress sin restricción** en ai-engine y mcp-server (ver topología). Candidato a ADR: proxy de egress con allowlist.
- **Healthchecks** de ai-engine y mcp-server pendientes; `depends_on` solo ordena el arranque.
- **CSP del frontend** acoplada a `VITE_API_URL` (`frontend/nginx.conf`).

## Decisiones pendientes
Ver lista en `CLAUDE.md` → Stack → "Pendiente de decidir". Cada decisión se registra en
`docs/decisions/`.
