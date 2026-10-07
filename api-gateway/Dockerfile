# Etapa 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
# Aquí Claude Code agregará el COPY package.json y RUN npm install

# Etapa 2: Producción (Imagen ligera)
FROM node:20-alpine
WORKDIR /app

# Cambiamos al usuario sin privilegios que trae la imagen Alpine
USER node

# Copiamos el código cambiando el propietario a 'node'
COPY --chown=node:node . .

EXPOSE 3000
CMD ["node", "index.js"]
