# US-GW-004: Dockerfile multi-stage del gateway e integración en Compose

**Épica:** 04 — API Gateway
**Prioridad:** ALTA
**Estimación:** 3 pts
**Dependencias:** US-GW-002, US-GW-003

## Historia de usuario
**Como** responsable de la infraestructura,
**quiero** una imagen del gateway multi-stage, sin privilegios y declarada en `docker-compose.yml`,
**para** desplegarlo junto al resto de servicios respetando el aislamiento de redes.

## Contexto técnico
Dockerfile actual: etapa `builder` vacía y etapa final con `USER node`, `COPY --chown=node:node . .`,
`EXPOSE 3000`, `CMD ["node","index.js"]`. Cambios esperados (orientativo):
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:20-alpine
ENV NODE_ENV=production
WORKDIR /app
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node package.json ./
COPY --chown=node:node src ./src
USER node
EXPOSE 3000
HEALTHCHECK CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "src/server.js"]
```
Bloque del servicio en `docker-compose.yml` (sin tocar el resto):
```yaml
api-gateway:
  environment:
    - PORT=3000
    - AI_ENGINE_URL=http://ai-engine:8000
    - CORS_ORIGIN=${CORS_ORIGIN:-http://localhost:5173}
  depends_on: [ai-engine]
```
- Se mantienen `public_network` + `internal_network`; el gateway es el único puente entre el exterior y el ai-engine.
- El gateway **no** recibe `OPENAI_API_KEY` ni `TMDB_API_KEY` (regla 2 de `CLAUDE.md`).
- `.dockerignore` con `node_modules`, `tests`, `.env*`, `.git`.

## Criterios de aceptación
- [x] La etapa `builder` copia `package*.json` y ejecuta `npm ci --omit=dev`; la imagen final no incluye devDependencies ni tests.
- [x] Se mantienen **dos etapas** y la ejecución como usuario no-root (`USER node`); `docker compose exec api-gateway id` ≠ uid 0.
- [x] `CMD` arranca `src/server.js`; `EXPOSE 3000`; `NODE_ENV=production`.
- [x] `HEALTHCHECK` contra `/health` (el contenedor pasa a `healthy`).
- [x] `docker-compose.yml` define `AI_ENGINE_URL`, `CORS_ORIGIN` (con valor por defecto) y `PORT` para el gateway;
  conserva `ports: "3000:3000"` y las redes `public_network` + `internal_network`.
- [x] `depends_on` del `ai-engine` (orden de arranque; la tolerancia a caídas la cubre el 503 del gateway).
- [x] Ninguna credencial (`OPENAI_API_KEY`, `TMDB_API_KEY`) llega al contenedor del gateway.
- [x] `.dockerignore` presente; la imagen final es ligera (se documenta el tamaño obtenido).
- [x] `docker compose build api-gateway` termina sin errores ni warnings de npm críticos.

## Fuera de alcance
- Orquestación avanzada (réplicas, balanceador, TLS), CI/CD y publicación de imágenes.

## Definition of Done
- Criterios marcados `[x]`.
- Prueba de integración manual: `docker compose up --build` → `curl localhost:3000/health` OK;
  `POST /api/chat` devuelve recomendación real atravesando gateway → ai-engine → mcp-server;
  `docker compose ps` muestra el gateway `healthy`.
- Desde el host: puertos del ai-engine (8000/8001) **no** accesibles.
- Verificado `docker compose exec api-gateway sh -c 'env | grep -E "OPENAI|TMDB"'` sin resultados.
- Plan de implementación y `docs/architecture.md` actualizados si cambia algo del flujo.
