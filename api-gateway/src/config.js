const DEFAULTS = {
  PORT: '3000',
  AI_ENGINE_URL: 'http://ai-engine:8000',
  CORS_ORIGIN: 'http://localhost:5173',
  AI_ENGINE_TIMEOUT_MS: '30000',
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

export function loadConfig(env = process.env) {
  const read = (name) => (env[name] ?? '').trim() || DEFAULTS[name];

  return {
    port: parsePositiveInt('PORT', read('PORT')),
    aiEngineUrl: parseUrl('AI_ENGINE_URL', read('AI_ENGINE_URL')),
    corsOrigin: read('CORS_ORIGIN'),
    aiEngineTimeoutMs: parsePositiveInt('AI_ENGINE_TIMEOUT_MS', read('AI_ENGINE_TIMEOUT_MS')),
  };
}
