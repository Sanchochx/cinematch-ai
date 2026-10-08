# US-AI-005: Dockerfile del AI Engine con venv y arranque de uvicorn

**Épica:** 03 — AI Engine
**Prioridad:** ALTA
**Estimación:** 3 pts
**Dependencias:** US-AI-001, US-AI-004

## Historia de usuario
**Como** responsable de la infraestructura,
**quiero** que la imagen del ai-engine instale sus dependencias en un entorno virtual durante el build
y arranque la API FastAPI,
**para** desplegar un contenedor ligero, reproducible y sin privilegios.

## Contexto técnico
El `ai-engine/Dockerfile` actual tiene dos etapas; la `builder` está vacía y la final crea `appuser`
y corre con él. Se replica el enfoque del `mcp-server/Dockerfile`: venv en `/opt/venv` creado en
`builder` y copiado a la etapa final.

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
# … COPY --chown, EXPOSE 8000 …
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Criterios de aceptación
- [ ] La etapa `builder` crea el venv `/opt/venv`, copia `requirements.txt` y ejecuta
  `RUN pip install --no-cache-dir -r requirements.txt`.
- [ ] Se eliminan el comentario placeholder del builder y cualquier comentario obsoleto.
- [ ] La etapa final copia el venv con `COPY --from=builder` y añade `/opt/venv/bin` al `PATH`.
- [ ] **Restricción estricta:** se mantienen las dos etapas y **no se modifican** las líneas
  `RUN groupadd -r appgroup && useradd -r -g appgroup appuser`, `RUN chown -R appuser:appgroup /app`,
  `USER appuser` y `COPY --chown=appuser:appgroup . .`.
- [ ] `EXPOSE 8000` se mantiene; `CMD` pasa a `["uvicorn","main:app","--host","0.0.0.0","--port","8000"]`
  (único cambio permitido en líneas existentes).
- [ ] `requirements-dev.txt` y `tests/` **no** se instalan ni copian en la imagen.
- [ ] Existe `ai-engine/.dockerignore` que excluye `.venv/`, `__pycache__/`, `.pytest_cache/`,
  `tests/` y `.env`.
- [ ] `docker compose build ai-engine` termina sin errores.
- [ ] `docker compose run --rm ai-engine whoami` devuelve `appuser`.
- [ ] `docker compose up ai-engine mcp-server` arranca uvicorn (log `Uvicorn running on
  http://0.0.0.0:8000`) y `GET /health` responde 200 desde otro contenedor de la red.
- [ ] El ai-engine sigue sin publicar puertos al host (`docker compose ps` no muestra mapeo).

## Fuera de alcance
- Modificar `docker-compose.yml` (variables, healthcheck, redes).
- Cambiar imagen base o estrategia de usuario.

## Definition of Done
- Criterios marcados `[x]`.
- `git diff ai-engine/Dockerfile` muestra solo las adiciones de instalación/copia del venv y el
  cambio de `CMD`; las líneas de `appuser` aparecen intactas.
