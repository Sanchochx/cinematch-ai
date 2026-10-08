# Arquitectura — CineMatch AI

## Visión general
Recomendador de películas basado en IA agéntica. El usuario conversa desde el frontend;
el api-gateway reenvía la conversación al ai-engine, donde un agente LangGraph decide
qué datos necesita y los obtiene llamando tools del mcp-server, que a su vez consulta TMDB.

Cada servicio corre en su propio contenedor (Docker Compose), con imágenes multi-stage
y usuario sin privilegios.

## Diagrama de componentes y redes
```
              ┌──────────── public_network ────────────┐
[Navegador] ─►│ frontend (React 19)  ─►  api-gateway   │
   host:5173  └────────────────────────── (Node) ──────┘ host:3000
                                             │
              ┌──────────── internal_network ┼─────────┐
              │                         ai-engine      │
              │                    (Python + LangGraph)│
              └──────────────────────────────┼─────────┘
                                             │ MCP
              ┌─────── ai_network (internal: sin internet) ─┐
              │                         mcp-server          │
              │                   (Python + SDK MCP)        │
              └──────────────────────────────┼──────────────┘
                                             ▼
                                        API de TMDB
```

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
3. El gateway valida el body y lo reenvía a `http://ai-engine:8000`.
4. El agente LangGraph extrae preferencias y decide qué tools llamar.
5. El ai-engine invoca tools en el mcp-server (`search_movies`, `get_similar_movies`…).
6. El mcp-server consulta TMDB y devuelve datos normalizados.
7. El agente filtra, razona y genera la respuesta con las películas recomendadas.
8. La respuesta vuelve (idealmente en streaming) gateway → frontend.

## Consideraciones de seguridad
- **Exposición mínima**: solo frontend y gateway publican puertos al host.
- **Secretos por servicio**: `TMDB_API_KEY` solo en mcp-server; la key del LLM solo en ai-engine.
- **Superficie del agente**: el agente solo puede actuar mediante las tools MCP definidas;
  las tools son de solo lectura.
- **Validación**: el gateway valida y limita tamaño del input antes de llegar al LLM.
- Autenticación de usuarios: pendiente de decidir.

## ⚠️ Problemas abiertos
- **El mcp-server no puede alcanzar TMDB**: está solo en `ai_network`, que es
  `internal: true` (sin salida a internet). Opciones: (a) conectarlo además a una red
  con salida solo para egress, (b) un proxy de egress con allowlist a `api.themoviedb.org`.
  Decidir y registrar como ADR.
- **El ai-engine necesita salida a internet** para el proveedor de LLM: hoy la tiene vía
  `internal_network` (bridge normal). Si se quiere restringir, usar también un proxy de egress.

## Decisiones pendientes
Ver lista en `CLAUDE.md` → Stack → "Pendiente de decidir". Cada decisión se registra en
`docs/decisions/`.
