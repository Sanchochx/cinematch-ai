import express from 'express';
import { chatRouter } from './routes/chat.js';
import { healthRouter } from './routes/health.js';
import { createAiEngineClient } from './services/aiEngineClient.js';

function requestLogger(logger) {
  return (req, res, next) => {
    const start = process.hrtime.bigint();
    res.on('finish', () => {
      const ms = Number(process.hrtime.bigint() - start) / 1e6;
      logger.info(`${req.method} ${req.path} ${res.statusCode} ${ms.toFixed(1)}ms`);
    });
    next();
  };
}

// `routers` permite montar rutas de negocio (y dobles en tests) antes del 404 y del manejador de errores.
export function createApp(
  config,
  {
    logger = console,
    routers = [],
    aiEngineClient = createAiEngineClient({ baseUrl: config.aiEngineUrl, timeoutMs: config.aiEngineTimeoutMs }),
  } = {},
) {
  const app = express();
  app.disable('x-powered-by');
  app.locals.config = config;

  app.use(requestLogger(logger));
  app.use(healthRouter());
  app.use(chatRouter({ aiEngineClient, logger }));
  routers.forEach((router) => app.use(router));

  app.use((_req, res) => {
    res.status(404).json({ error: 'not_found' });
  });

  // Cuerpo genérico: nunca exponer trazas, URLs internas ni cabeceras.
  // eslint-disable-next-line no-unused-vars -- Express identifica el manejador de errores por su aridad (4).
  app.use((err, _req, res, _next) => {
    logger.error(`Error no controlado: ${err.name}`);
    res.status(500).json({ error: 'internal_error', message: 'Ha ocurrido un error inesperado.' });
  });

  return app;
}
