import express, { Router } from 'express';
import { chatRequestSchema } from '../models/chatRequest.js';
import { AiEngineError } from '../services/aiEngineClient.js';

const BODY_LIMIT = '64kb';

const ERRORS = {
  invalid_request: { status: 400, message: 'La solicitud no es válida. Revisa tu mensaje e inténtalo de nuevo.' },
  unsupported_media_type: { status: 415, message: 'El contenido debe enviarse como application/json.' },
  upstream_unavailable: { status: 503, message: 'El servicio no está disponible en este momento. Inténtalo más tarde.' },
  upstream_error: { status: 502, message: 'No hemos podido obtener una respuesta. Inténtalo de nuevo.' },
  timeout: { status: 504, message: 'La respuesta ha tardado demasiado. Inténtalo de nuevo.' },
  internal_error: { status: 500, message: 'Ha ocurrido un error inesperado.' },
};

function sendError(res, kind) {
  const { status, message } = ERRORS[kind];
  res.status(status).json({ error: kind === 'unsupported_media_type' ? 'invalid_request' : kind, message });
}

function requireJson(req, res, next) {
  if (!req.is('application/json')) return sendError(res, 'unsupported_media_type');
  next();
}

export function chatRouter({ aiEngineClient, logger = console }) {
  const router = Router();

  router.post('/api/chat', requireJson, express.json({ limit: BODY_LIMIT }), async (req, res) => {
    const parsed = chatRequestSchema.safeParse(req.body);
    if (!parsed.success) return sendError(res, 'invalid_request');

    try {
      const { reply } = await aiEngineClient.chat(parsed.data);
      res.json({ reply });
    } catch (err) {
      const kind = err instanceof AiEngineError ? err.kind : 'internal_error';
      // Solo el tipo: el mensaje del error puede contener URLs internas.
      logger.error(`Fallo en /api/chat: ${kind}`);
      sendError(res, kind);
    }
  });

  // JSON malformado o cuerpo demasiado grande: 400 sin eco del payload.
  router.use('/api/chat', (err, _req, res, next) => {
    if (err?.type === 'entity.parse.failed' || err?.type === 'entity.too.large') {
      return sendError(res, 'invalid_request');
    }
    next(err);
  });

  return router;
}
