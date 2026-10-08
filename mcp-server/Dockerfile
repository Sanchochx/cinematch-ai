# Etapa 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2: Producción
FROM python:3.11-slim

# Comandos de Linux: Crear un grupo y un usuario de sistema (-r) sin directorio home (-M)
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Cambiar propiedad del directorio al nuevo usuario
RUN chown -R appuser:appgroup /app

# Cambiar al usuario sin privilegios
USER appuser

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=appuser:appgroup . .

EXPOSE 8000
CMD ["python", "main.py"]
