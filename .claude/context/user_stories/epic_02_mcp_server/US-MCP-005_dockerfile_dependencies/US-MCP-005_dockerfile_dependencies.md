# US-MCP-005: Instalación de dependencias en el Dockerfile del MCP Server

**Épica:** 02 — MCP Server
**Prioridad:** ALTA
**Estimación:** 2 pts
**Dependencias:** US-MCP-001

## Historia de usuario
**Como** responsable de la infraestructura,
**quiero** que la imagen del mcp-server instale sus dependencias en la etapa de build,
**para** que el contenedor arranque el servidor MCP real manteniendo la imagen final ligera y sin privilegios.

## Contexto técnico
El `mcp-server/Dockerfile` actual tiene dos etapas. La `builder` está vacía y tiene el comentario
"Aquí Claude Code agregará el COPY requirements.txt y RUN pip install". La final crea `appuser`,
ajusta permisos y corre como ese usuario.

Enfoque: instalar en un **virtualenv** en la etapa `builder` y copiarlo a la final. Así se cumple el
comando pedido (`RUN pip install --no-cache-dir -r requirements.txt`) y la imagen final no lleva
cachés ni herramientas de build.

### Cambios esperados (orientativo)
```dockerfile
# Etapa 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2: Producción
FROM python:3.11-slim
# … líneas de appuser SIN CAMBIOS …
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# … resto SIN CAMBIOS (COPY --chown, EXPOSE 8000, CMD) …
```

## Criterios de aceptación
- [x] La etapa `builder` copia `requirements.txt` y ejecuta exactamente
  `RUN pip install --no-cache-dir -r requirements.txt` (dentro del venv `/opt/venv`).
- [x] Se eliminan el comentario placeholder del builder y cualquier otro comentario que quede obsoleto.
- [x] La etapa final copia el venv con `COPY --from=builder` y añade `/opt/venv/bin` al `PATH`.
- [x] **Restricción estricta:** se mantienen las dos etapas (`builder` + producción) y **no se
  modifican** las líneas existentes de usuario y permisos:
  `RUN groupadd -r appgroup && useradd -r -g appgroup appuser`, `RUN chown -R appuser:appgroup /app`,
  `USER appuser` y `COPY --chown=appuser:appgroup . .`.
- [x] `EXPOSE 8000` y `CMD ["python", "main.py"]` no cambian.
- [x] `requirements-dev.txt` (pytest, respx…) **no** se instala en la imagen.
- [x] Existe `mcp-server/.dockerignore` que excluye `.venv/`, `__pycache__/`, `.pytest_cache/`, `tests/` y `.env`.
- [x] `docker compose build mcp-server` termina sin errores.
- [x] `docker compose run --rm mcp-server whoami` devuelve `appuser`.
- [x] `docker compose up mcp-server` muestra en los logs el arranque del servidor MCP (en modo mock,
  porque el compose aún no pasa `TMDB_API_KEY`).

## Fuera de alcance
- Modificar `docker-compose.yml` (variables de entorno, healthcheck, redes).
- Cambiar la imagen base o la estrategia de usuario.

## Definition of Done
- Criterios marcados `[x]`.
- `git diff mcp-server/Dockerfile` muestra solo líneas añadidas en las zonas de instalación y copia
  del venv; las líneas de `appuser` aparecen intactas.
