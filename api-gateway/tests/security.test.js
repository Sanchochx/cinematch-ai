import request from 'supertest';
import { describe, expect, it, vi } from 'vitest';
import { createApp } from '../src/app.js';
import { loadConfig } from '../src/config.js';

const logger = { info: vi.fn(), error: vi.fn() };
const ALLOWED = 'http://localhost:5173';
const EVIL = 'http://evil.example';

function setup(env = {}) {
  const aiEngineClient = { chat: vi.fn(async () => ({ reply: 'ok' })) };
  const app = createApp(loadConfig(env), { logger, aiEngineClient });
  return { app, aiEngineClient };
}

const chat = (app) => request(app).post('/api/chat').set('Content-Type', 'application/json');

describe('CORS', () => {
  it('origen permitido: ACAO exacto y Vary: Origin', async () => {
    const { app } = setup();
    const res = await chat(app).set('Origin', ALLOWED).send({ message: 'hola' });
    expect(res.status).toBe(200);
    expect(res.headers['access-control-allow-origin']).toBe(ALLOWED);
    expect(res.headers.vary).toMatch(/Origin/i);
    expect(res.headers['access-control-allow-credentials']).toBeUndefined();
  });

  it('origen no permitido: 403, sin cabeceras CORS y sin llegar al ai-engine', async () => {
    const { app, aiEngineClient } = setup();
    const res = await chat(app).set('Origin', EVIL).send({ message: 'hola' });
    expect(res.status).toBe(403);
    expect(Object.keys(res.headers).filter((h) => h.startsWith('access-control-'))).toEqual([]);
    expect(aiEngineClient.chat).not.toHaveBeenCalled();
  });

  it('nunca devuelve * ni refleja el Origin', async () => {
    const { app } = setup({ CORS_ORIGIN: 'http://a.com,http://b.com' });
    const res = await chat(app).set('Origin', 'http://b.com').send({ message: 'hola' });
    expect(res.headers['access-control-allow-origin']).toBe('http://b.com');
    const other = await chat(app).set('Origin', 'http://c.com').send({ message: 'hola' });
    expect(other.headers['access-control-allow-origin']).toBeUndefined();
  });

  it('preflight OPTIONS /api/chat: 204 con métodos, cabeceras y max-age', async () => {
    const { app } = setup();
    const res = await request(app)
      .options('/api/chat')
      .set('Origin', ALLOWED)
      .set('Access-Control-Request-Method', 'POST')
      .set('Access-Control-Request-Headers', 'content-type');
    expect(res.status).toBe(204);
    expect(res.headers['access-control-allow-origin']).toBe(ALLOWED);
    expect(res.headers['access-control-allow-methods']).toBe('POST,OPTIONS');
    expect(res.headers['access-control-allow-headers']).toBe('Content-Type');
    expect(Number(res.headers['access-control-max-age'])).toBeGreaterThan(0);
    expect(res.headers['access-control-allow-credentials']).toBeUndefined();
  });

  it('preflight desde origen no permitido: sin cabeceras CORS', async () => {
    const { app } = setup();
    const res = await request(app)
      .options('/api/chat')
      .set('Origin', EVIL)
      .set('Access-Control-Request-Method', 'POST');
    expect(res.status).toBe(403);
    expect(res.headers['access-control-allow-origin']).toBeUndefined();
  });
});

describe('límite de body', () => {
  it('> 512kb → 413 payload_too_large', async () => {
    const { app, aiEngineClient } = setup();
    const res = await chat(app).send({ message: 'hola', padding: 'a'.repeat(513 * 1024) });
    expect(res.status).toBe(413);
    expect(res.body.error).toBe('payload_too_large');
    expect(aiEngineClient.chat).not.toHaveBeenCalled();
  });
});

describe('límite de body vs. límites del chat', () => {
  it('un historial máximo (> 200 kb) sigue siendo aceptado', async () => {
    const { app } = setup();
    const history = Array.from({ length: 20 }, () => ({ role: 'assistant', content: 'a'.repeat(10000) }));
    const res = await chat(app).send({ message: 'a'.repeat(2000), history });
    expect(res.status).toBe(200);
  });
});

describe('rate limit', () => {
  it('429 rate_limited con Retry-After al superar el máximo', async () => {
    const { app } = setup({ RATE_LIMIT_MAX: '2', RATE_LIMIT_WINDOW_MS: '60000' });
    expect((await chat(app).send({ message: 'a' })).status).toBe(200);
    expect((await chat(app).send({ message: 'b' })).status).toBe(200);
    const res = await chat(app).send({ message: 'c' });
    expect(res.status).toBe(429);
    expect(res.body.error).toBe('rate_limited');
    expect(Number(res.headers['retry-after'])).toBe(60);
  });

  it('/health queda excluido y los preflights no consumen cupo', async () => {
    const { app } = setup({ RATE_LIMIT_MAX: '1' });
    for (let i = 0; i < 5; i++) {
      expect((await request(app).get('/health')).status).toBe(200);
      expect((await request(app).options('/api/chat').set('Origin', ALLOWED)).status).toBe(204);
    }
    expect((await chat(app).send({ message: 'a' })).status).toBe(200);
  });
});

describe('métodos y cabeceras HTTP', () => {
  it.each(['get', 'put', 'delete', 'patch'])('%s /api/chat → 405 con Allow', async (method) => {
    const { app } = setup();
    const res = await request(app)[method]('/api/chat');
    expect(res.status).toBe(405);
    expect(res.headers.allow).toBe('POST, OPTIONS');
  });

  it('helmet añade cabeceras de seguridad', async () => {
    const { app } = setup();
    const res = await request(app).get('/health');
    expect(res.headers['x-content-type-options']).toBe('nosniff');
    expect(res.headers['x-frame-options']).toBeDefined();
    expect(res.headers['x-powered-by']).toBeUndefined();
  });
});

describe('arranque', () => {
  it('falla con CORS_ORIGIN=* en producción', () => {
    expect(() => loadConfig({ NODE_ENV: 'production', CORS_ORIGIN: '*' })).toThrow(/CORS_ORIGIN/);
  });
});
