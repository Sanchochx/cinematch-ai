# Etapa 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
# Aquí Claude Code agregará el COPY requirements.txt y RUN pip install

# Etapa 2: Producción
FROM python:3.11-slim

# Comandos de Linux: Crear un grupo y un usuario de sistema (-r) sin directorio home (-M)
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Cambiar propiedad del directorio al nuevo usuario
RUN chown -R appuser:appgroup /app

# Cambiar al usuario sin privilegios
USER appuser

COPY --chown=appuser:appgroup . .

EXPOSE 8000
CMD ["python", "main.py"]
