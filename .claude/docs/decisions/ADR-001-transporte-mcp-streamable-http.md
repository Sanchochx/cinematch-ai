# ADR-001: Transporte MCP: Streamable HTTP

**Fecha:** 2026-10-07
**Estado:** Aceptada
**Historia:** US-MCP-002

## Contexto
El agente del `ai-engine` consume las tools del `mcp-server` mediante el protocolo MCP. Ambos
servicios corren en **contenedores distintos** y solo comparten la red `ai_network`, así que el
transporte tiene que funcionar por red usando el nombre de servicio de Compose
(`http://mcp-server:8000`).

El SDK oficial `mcp` (rama 1.x, ver `mcp-server/README.md`) ofrece tres transportes:

| Transporte | Funciona entre contenedores | Observaciones |
|---|---|---|
| `stdio` | No | El cliente lanza el servidor como subproceso; obligaría a meter el mcp-server dentro de la imagen del ai-engine y a darle allí `TMDB_API_KEY`. |
| SSE (HTTP+SSE) | Sí | Marcado como obsoleto en la especificación de MCP desde 2025-03-26; dos endpoints (`/sse` y `/messages/`). |
| Streamable HTTP | Sí | Transporte HTTP actual de la especificación; un único endpoint, soporta streaming y sesiones. |

## Decisión
El `mcp-server` usa **Streamable HTTP**:
- Instancia `FastMCP("cinematch-mcp")` arrancada con `run_streamable_http_async()`.
- Escucha en `0.0.0.0:8000` (configurable con `MCP_HOST` / `MCP_PORT`).
- Único endpoint: `/mcp`. El servidor no expone ninguna otra ruta HTTP.
- El ai-engine se conectará con `MCP_SERVER_URL=http://mcp-server:8000/mcp`.

## Consecuencias
**Ventajas**
- Cada servicio sigue en su propio contenedor y solo el mcp-server conoce `TMDB_API_KEY`
  (regla 2 de `CLAUDE.md`).
- Es el transporte vigente de la especificación y el que soportan los clientes MCP actuales
  (incluido el adaptador MCP de LangChain/LangGraph).
- Un único endpoint simplifica la red: no hace falta publicar el puerto al host, basta `ai_network`.

**Trade-offs y pendientes**
- Sin autenticación: cualquier contenedor en `ai_network` puede llamar a las tools. Es aceptable
  porque la red es interna y las tools son de solo lectura; si se añaden más servicios a esa red,
  revisar (token compartido o `auth` de FastMCP).
- Al escuchar en `0.0.0.0`, el SDK no activa la protección contra DNS rebinding (solo la activa
  para `localhost`). No aplica mientras el puerto no se publique al host.
- Sesiones con estado en memoria del proceso: con varias réplicas del mcp-server haría falta
  `stateless_http=True` o afinidad de sesión.
- `MCP_SERVER_URL` en `CLAUDE.md` debe incluir la ruta `/mcp` al configurar el ai-engine.
