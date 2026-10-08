# US-FE-004: Dockerfile multi-stage (Vite → nginx sin privilegios) e integración en Compose

**Épica:** 05 — Frontend
**Prioridad:** ALTA
**Estimación:** 3 pts
**Dependencias:** US-FE-003, US-GW-004

## Historia de usuario
**Como** responsable de la infraestructura,
**quiero** una imagen del frontend que compile la SPA y la sirva con un servidor ligero sin privilegios,
**para** desplegar la UI junto al resto de servicios con `docker compose up --build`.

## Contexto técnico
Dockerfile actual: `builder` vacío y etapa final con `USER node` que ejecuta `node index.js`. Cambios esperados (orientativo):
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=http://localhost:3000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf   # listen 3000; SPA fallback; cache de assets; cabeceras
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 3000
HEALTHCHECK CMD wget -qO- http://localhost:3000/ || exit 1
```
Bloque en `docker-compose.yml`:
```yaml
frontend:
  build:
    context: ./frontend
    args:
      VITE_API_URL: ${VITE_API_URL:-http://localhost:3000}
  ports: ["5173:3000"]
  networks: [public_network]
  depends_on: [api-gateway]
```
- `VITE_API_URL` se inlinea en el bundle en build time; es la URL **pública** del gateway vista desde el navegador.
- `nginx-unprivileged` corre como usuario no-root (uid 101) y no necesita puertos < 1024.
- El frontend permanece solo en `public_network`: no tiene ruta a `ai-engine` ni `mcp-server`.

## Criterios de aceptación
- [ ] `builder` ejecuta `npm ci` + `npm run build`; la imagen final contiene **solo** `dist/` y la config de nginx
  (sin `node_modules`, sin código fuente, sin Node).
- [ ] Dos etapas; la imagen final corre como usuario **no-root** (`docker compose exec frontend id` ≠ uid 0).
- [ ] `nginx.conf` escucha en el puerto 3000, con *fallback* a `index.html` para la SPA, `Cache-Control` largo para assets con hash
  y `no-cache` para `index.html`, `gzip` activo y cabeceras `X-Content-Type-Options`, `X-Frame-Options`/`frame-ancestors`
  y una `Content-Security-Policy` cuyo `connect-src` permite únicamente el origen del gateway.
- [ ] `VITE_API_URL` se pasa como `build.args` en Compose con valor por defecto `http://localhost:3000`.
- [ ] Compose: `ports: "5173:3000"`, red `public_network` únicamente, `depends_on: api-gateway`; sin variables secretas.
- [ ] `.dockerignore` con `node_modules`, `dist`, `.env*`, `.git`, `tests`.
- [ ] `HEALTHCHECK` operativo (contenedor `healthy`).
- [ ] `docker compose up --build` levanta los 4 servicios y la UI en `http://localhost:5173` completa una conversación real.
- [ ] Verificación de CORS: la petición del navegador desde `http://localhost:5173` al gateway tiene éxito (sin errores CORS en consola).

## Fuera de alcance
- TLS/HTTPS, CDN, despliegue en la nube, CI/CD, E2E con Playwright.

## Definition of Done
- Criterios marcados `[x]`.
- Prueba de integración manual de extremo a extremo: navegador → frontend → gateway → ai-engine → mcp-server → TMDB,
  con recomendación visible en la UI.
- `docker compose ps` muestra los 4 servicios `Up`/`healthy`; `docker compose exec frontend id` sin root.
- Confirmado que los puertos del `ai-engine` (8000/8001) y del `mcp-server` no están publicados en el host.
- `docs/architecture.md` y `CLAUDE.md` (variables, decisiones tomadas) actualizados.
- Plan de implementación actualizado y resumen de fase en `context/summaries/phase-4-resume.md`.
