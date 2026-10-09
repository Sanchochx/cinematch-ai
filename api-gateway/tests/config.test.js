import { describe, expect, it } from 'vitest';
import { loadConfig } from '../src/config.js';

describe('loadConfig', () => {
  it('usa valores por defecto', () => {
    expect(loadConfig({})).toEqual({
      port: 3000,
      aiEngineUrl: 'http://ai-engine:8000',
      corsOrigins: ['http://localhost:5173'],
      aiEngineTimeoutMs: 30000,
      rateLimitMax: 20,
      rateLimitWindowMs: 60000,
    });
  });

  it('lee variables del entorno y normaliza la barra final de la URL', () => {
    const config = loadConfig({ PORT: '4000', AI_ENGINE_URL: 'http://x:1/', CORS_ORIGIN: 'http://a.com' });
    expect(config).toMatchObject({ port: 4000, aiEngineUrl: 'http://x:1', corsOrigins: ['http://a.com'] });
  });

  it.each(['abc', '0', '-1', '3.5'])('rechaza PORT inválido (%s)', (port) => {
    expect(() => loadConfig({ PORT: port })).toThrow(/PORT/);
  });

  it.each(['no-url', 'ftp://x'])('rechaza AI_ENGINE_URL inválida (%s)', (url) => {
    expect(() => loadConfig({ AI_ENGINE_URL: url })).toThrow(/AI_ENGINE_URL/);
  });

  it('rechaza AI_ENGINE_TIMEOUT_MS inválido', () => {
    expect(() => loadConfig({ AI_ENGINE_TIMEOUT_MS: 'x' })).toThrow(/AI_ENGINE_TIMEOUT_MS/);
  });

  it('admite una lista de orígenes separada por comas', () => {
    const config = loadConfig({ CORS_ORIGIN: 'http://a.com, https://b.com:8443/' });
    expect(config.corsOrigins).toEqual(['http://a.com', 'https://b.com:8443']);
  });

  it.each(['*', 'http://a.com,*', 'localhost', 'http://a.com/ruta', 'ftp://a.com'])(
    'rechaza CORS_ORIGIN inválido (%s)',
    (origin) => {
      expect(() => loadConfig({ CORS_ORIGIN: origin })).toThrow(/CORS_ORIGIN/);
    },
  );

  it('en producción CORS_ORIGIN es obligatorio y no admite *', () => {
    expect(() => loadConfig({ NODE_ENV: 'production' })).toThrow(/CORS_ORIGIN/);
    expect(() => loadConfig({ NODE_ENV: 'production', CORS_ORIGIN: '*' })).toThrow(/CORS_ORIGIN/);
    expect(loadConfig({ NODE_ENV: 'production', CORS_ORIGIN: 'https://app.example' }).corsOrigins).toEqual([
      'https://app.example',
    ]);
  });

  it('lee y valida el rate limit', () => {
    expect(loadConfig({ RATE_LIMIT_MAX: '5', RATE_LIMIT_WINDOW_MS: '1000' })).toMatchObject({
      rateLimitMax: 5,
      rateLimitWindowMs: 1000,
    });
    expect(() => loadConfig({ RATE_LIMIT_MAX: '0' })).toThrow(/RATE_LIMIT_MAX/);
    expect(() => loadConfig({ RATE_LIMIT_WINDOW_MS: 'x' })).toThrow(/RATE_LIMIT_WINDOW_MS/);
  });
});
