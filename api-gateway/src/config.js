const DEFAULTS = {
  PORT: '3000',
  AI_ENGINE_URL: 'http://ai-engine:8000',
  CORS_ORIGIN: 'http://localhost:5173',
  AI_ENGINE_TIMEOUT_MS: '30000',
  RATE_LIMIT_MAX: '20',
  RATE_LIMIT_WINDOW_MS: '60000',
};

function parsePositiveInt(name, raw) {
  if (!/^\d+$/.test(raw) || Number(raw) <= 0) {
    throw new Error(`${name} debe ser un entero positivo (recibido: "${raw}")`);
  }
  return Number(raw);
}

function parseUrl(name, raw) {
  try {
    const url = new URL(raw);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') throw new Error();
    return raw.replace(/\/+$/, '');
  } catch {
    throw new Error(`${name} debe ser una URL http(s) válida (recibido: "${raw}")`);
  }
}

// Allowlist exacta de orígenes (esquema + host + puerto). `*` nunca es válido: el gateway no refleja orígenes.
function parseCorsOrigins(raw, { production }) {
  if (production && !raw) throw new Error('CORS_ORIGIN es obligatorio en producción');
  const origins = (raw || DEFAULTS.CORS_ORIGIN).split(',').map((o) => o.trim()).filter(Boolean);
  if (origins.length === 0) throw new Error('CORS_ORIGIN no contiene ningún origen');
  return origins.map((origin) => {
    try {
      const url = new URL(origin);
      if ((url.protocol !== 'http:' && url.protocol !== 'https:') || url.origin !== origin.replace(/\/+$/, '')) {
        throw new Error();
      }
      return url.origin;
    } catch {
      throw new Error(`CORS_ORIGIN debe ser una lista de orígenes http(s) exactos, sin comodines (recibido: "${origin}")`);
    }
  });
}

export function loadConfig(env = process.env) {
  const rawValue = (name) => (env[name] ?? '').trim();
  const read = (name) => rawValue(name) || DEFAULTS[name];
  const production = rawValue('NODE_ENV') === 'production';

  return {
    port: parsePositiveInt('PORT', read('PORT')),
    aiEngineUrl: parseUrl('AI_ENGINE_URL', read('AI_ENGINE_URL')),
    corsOrigins: parseCorsOrigins(rawValue('CORS_ORIGIN'), { production }),
    aiEngineTimeoutMs: parsePositiveInt('AI_ENGINE_TIMEOUT_MS', read('AI_ENGINE_TIMEOUT_MS')),
    rateLimitMax: parsePositiveInt('RATE_LIMIT_MAX', read('RATE_LIMIT_MAX')),
    rateLimitWindowMs: parsePositiveInt('RATE_LIMIT_WINDOW_MS', read('RATE_LIMIT_WINDOW_MS')),
  };
}
