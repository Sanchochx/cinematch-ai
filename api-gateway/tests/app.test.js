import { Router } from 'express';
import request from 'supertest';
import { describe, expect, it, vi } from 'vitest';
import { createApp } from '../src/app.js';
import { loadConfig } from '../src/config.js';

const logger = { info: vi.fn(), error: vi.fn() };
const buildApp = (routers) => createApp(loadConfig({}), { logger, routers });

describe('GET /health', () => {
  it('responde 200 {"status":"ok"}', async () => {
    const res = await request(buildApp()).get('/health');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: 'ok' });
  });

  it('no expone X-Powered-By', async () => {
    const res = await request(buildApp()).get('/health');
    expect(res.headers['x-powered-by']).toBeUndefined();
  });
});

describe('rutas desconocidas', () => {
  it('devuelven 404 en JSON', async () => {
    const res = await request(buildApp()).get('/nope');
    expect(res.status).toBe(404);
    expect(res.headers['content-type']).toMatch(/json/);
    expect(res.body).toEqual({ error: 'not_found' });
  });
});

describe('manejador global de errores', () => {
  it('devuelve 500 genérico sin filtrar detalles internos', async () => {
    const boom = Router().get('/boom', () => {
      throw new Error('secreto http://ai-engine:8000');
    });
    const res = await request(buildApp([boom])).get('/boom');
    expect(res.status).toBe(500);
    expect(res.body.error).toBe('internal_error');
    expect(JSON.stringify(res.body)).not.toContain('ai-engine');
  });
});

describe('logging', () => {
  it('registra método, ruta, status y duración', async () => {
    logger.info.mockClear();
    await request(buildApp()).get('/health');
    expect(logger.info).toHaveBeenCalledWith(expect.stringMatching(/^GET \/health 200 [\d.]+ms$/));
  });
});
