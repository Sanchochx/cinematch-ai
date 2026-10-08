import { describe, expect, it } from 'vitest';
import { loadConfig } from '../src/config.js';

describe('loadConfig', () => {
  it('usa valores por defecto', () => {
    expect(loadConfig({})).toEqual({
      port: 3000,
      aiEngineUrl: 'http://ai-engine:8000',
      corsOrigin: 'http://localhost:5173',
      aiEngineTimeoutMs: 30000,
    });
  });

  it('lee variables del entorno y normaliza la barra final de la URL', () => {
    const config = loadConfig({ PORT: '4000', AI_ENGINE_URL: 'http://x:1/', CORS_ORIGIN: 'http://a.com' });
    expect(config).toMatchObject({ port: 4000, aiEngineUrl: 'http://x:1', corsOrigin: 'http://a.com' });
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
});
