import { createApp } from './app.js';
import { loadConfig } from './config.js';

const config = loadConfig();
const app = createApp(config);

const server = app.listen(config.port, () => {
  console.info(`api-gateway escuchando en el puerto ${config.port}`);
});

function shutdown(signal) {
  console.info(`${signal} recibido, cerrando servidor`);
  server.close(() => process.exit(0));
  // Evita colgar `docker compose down` si hay conexiones keep-alive abiertas.
  setTimeout(() => process.exit(1), 10_000).unref();
  server.closeIdleConnections?.();
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
