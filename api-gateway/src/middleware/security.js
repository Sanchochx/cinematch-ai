import cors from 'cors';
import rateLimit from 'express-rate-limit';

const PREFLIGHT_MAX_AGE_SECONDS = 600;

// Un navegador desde un origen ajeno recibe 403 sin cabeceras CORS. Las peticiones sin `Origin`
// (curl, servidores) pasan: CORS solo protege a navegadores; el coste lo limita el rate limit.
export function originGuard(allowedOrigins) {
  const allowed = new Set(allowedOrigins);
  return (req, res, next) => {
    const { origin } = req.headers;
    if (origin !== undefined && !allowed.has(origin)) {
      return res.status(403).json({ error: 'forbidden_origin', message: 'Origen no permitido.' });
    }
    next();
  };
}

export function corsMiddleware(allowedOrigins) {
  return cors({
    origin: allowedOrigins, // allowlist exacta: nunca `*` ni reflejo del Origin
    methods: ['POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type'],
    credentials: false,
    maxAge: PREFLIGHT_MAX_AGE_SECONDS,
    optionsSuccessStatus: 204,
  });
}

export function createRateLimiter({ rateLimitMax, rateLimitWindowMs }) {
  return rateLimit({
    windowMs: rateLimitWindowMs,
    limit: rateLimitMax,
    standardHeaders: 'draft-7',
    legacyHeaders: false,
    handler: (_req, res) => {
      res.set('Retry-After', String(Math.ceil(rateLimitWindowMs / 1000)));
      res.status(429).json({
        error: 'rate_limited',
        message: 'Demasiadas solicitudes. Espera un momento antes de volver a intentarlo.',
      });
    },
  });
}
