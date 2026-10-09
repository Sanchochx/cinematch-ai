import request from 'supertest';
import { describe, expect, it, vi } from 'vitest';
import { createApp } from '../src/app.js';
import { loadConfig } from '../src/config.js';
import { CHAT_LIMITS } from '../src/models/chatRequest.js';
import { AiEngineError, createAiEngineClient } from '../src/services/aiEngineClient.js';

const logger = { info: vi.fn(), error: vi.fn() };

function setup(chatImpl = async () => ({ reply: 'Te recomiendo Arrival' })) {
  const aiEngineClient = { chat: vi.fn(chatImpl) };
  const app = createApp(loadConfig({}), { logger, aiEngineClient });
  return { app, aiEngineClient };
}

const post = (app, body) => request(app).post('/api/chat').set('Content-Type', 'application/json').send(body);

describe('POST /api/chat — caso feliz', () => {
  it('reenvía solo {message, history} saneados y devuelve el reply', async () => {
    const { app, aiEngineClient } = setup();
    const res = await post(app, {
      message: '  Quiero ciencia ficción  ',
      history: [{ role: 'user', content: 'hola', extra: 'x' }],
      isAdmin: true,
    });
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ reply: 'Te recomiendo Arrival' });
    expect(aiEngineClient.chat).toHaveBeenCalledWith({
      message: 'Quiero ciencia ficción',
      history: [{ role: 'user', content: 'hola' }],
    });
  });

  it('history es [] por defecto', async () => {
    const { app, aiEngineClient } = setup();
    await post(app, { message: 'hola' });
    expect(aiEngineClient.chat).toHaveBeenCalledWith({ message: 'hola', history: [] });
  });
});

describe('POST /api/chat — validación (400)', () => {
  const longText = 'a'.repeat(CHAT_LIMITS.MAX_MESSAGE_LENGTH + 1);
  const cases = {
    'message faltante': {},
    'message vacío': { message: '   ' },
    'message no string': { message: 42 },
    'message demasiado largo': { message: longText },
    'history no es array': { message: 'hola', history: 'x' },
    'rol inválido': { message: 'hola', history: [{ role: 'system', content: 'x' }] },
    'content vacío': { message: 'hola', history: [{ role: 'user', content: '' }] },
    'content demasiado largo': { message: 'hola', history: [{ role: 'user', content: longText }] },
    'history con demasiados ítems': {
      message: 'hola',
      history: Array.from({ length: CHAT_LIMITS.MAX_HISTORY_ITEMS + 1 }, () => ({ role: 'user', content: 'x' })),
    },
  };

  it.each(Object.entries(cases))('%s', async (_name, body) => {
    const { app, aiEngineClient } = setup();
    const res = await post(app, body);
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_request');
    expect(res.body.message).toEqual(expect.any(String));
    expect(aiEngineClient.chat).not.toHaveBeenCalled();
  });

  it('JSON malformado: 400 sin eco del payload', async () => {
    const { app } = setup();
    const res = await request(app).post('/api/chat').set('Content-Type', 'application/json').send('{"message": SECRETO');
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_request');
    expect(JSON.stringify(res.body)).not.toContain('SECRETO');
  });


  it('acepta exactamente los límites', async () => {
    const { app } = setup();
    const res = await post(app, {
      message: 'a'.repeat(CHAT_LIMITS.MAX_MESSAGE_LENGTH),
      history: Array.from({ length: CHAT_LIMITS.MAX_HISTORY_ITEMS }, () => ({ role: 'assistant', content: 'x' })),
    });
    expect(res.status).toBe(200);
  });
});

describe('POST /api/chat — Content-Type', () => {
  it.each(['text/plain', 'application/x-www-form-urlencoded'])('%s → 415', async (type) => {
    const { app, aiEngineClient } = setup();
    const res = await request(app).post('/api/chat').set('Content-Type', type).send('message=hola');
    expect(res.status).toBe(415);
    expect(aiEngineClient.chat).not.toHaveBeenCalled();
  });

  it('sin Content-Type → 415', async () => {
    const { app } = setup();
    expect((await request(app).post('/api/chat')).status).toBe(415);
  });
});

describe('POST /api/chat — errores aguas abajo', () => {
  it.each([
    ['upstream_unavailable', 503],
    ['upstream_error', 502],
    ['timeout', 504],
  ])('%s → %i', async (kind, status) => {
    const { app } = setup(async () => {
      throw new AiEngineError(kind);
    });
    const res = await post(app, { message: 'hola' });
    expect(res.status).toBe(status);
    expect(res.body.error).toBe(kind);
  });

  it('error inesperado → 500 sin filtrar detalles', async () => {
    const { app } = setup(async () => {
      throw new Error('fallo en http://ai-engine:8000/chat');
    });
    const res = await post(app, { message: 'hola' });
    expect(res.status).toBe(500);
    expect(res.body.error).toBe('internal_error');
    expect(JSON.stringify(res.body)).not.toMatch(/ai-engine|8000/);
    expect(JSON.stringify(logger.error.mock.calls)).not.toContain('ai-engine');
  });
});

describe('aiEngineClient', () => {
  const build = (fetchImpl) => createAiEngineClient({ baseUrl: 'http://ai-engine:8000', timeoutMs: 1000, fetchImpl });
  const jsonResponse = (status, body) => new Response(JSON.stringify(body), { status });
  const kindOf = async (client) => client.chat({ message: 'hola', history: [] }).catch((e) => e.kind);

  it('hace POST a /chat con JSON, sin cabeceras del cliente, y con timeout', async () => {
    const fetchImpl = vi.fn(async () => jsonResponse(200, { reply: 'ok' }));
    const result = await build(fetchImpl).chat({ message: 'hola', history: [] });
    expect(result).toEqual({ reply: 'ok' });
    const [url, init] = fetchImpl.mock.calls[0];
    expect(url).toBe('http://ai-engine:8000/chat');
    expect(init.method).toBe('POST');
    expect(init.headers).toEqual({ 'Content-Type': 'application/json' });
    expect(JSON.parse(init.body)).toEqual({ message: 'hola', history: [] });
    expect(init.signal).toBeInstanceOf(AbortSignal);
  });

  it.each([
    [200, { nope: 1 }, 'upstream_error'],
    [200, { reply: 5 }, 'upstream_error'],
    [502, { detail: 'x' }, 'upstream_error'],
    [500, {}, 'upstream_error'],
    [422, {}, 'upstream_error'],
    [503, {}, 'upstream_unavailable'],
  ])('status %i %j → %s', async (status, body, kind) => {
    expect(await kindOf(build(async () => jsonResponse(status, body)))).toBe(kind);
  });

  it('cuerpo no JSON → upstream_error', async () => {
    expect(await kindOf(build(async () => new Response('<html>', { status: 200 })))).toBe('upstream_error');
  });

  it('fallo de red → upstream_unavailable', async () => {
    expect(await kindOf(build(async () => { throw new TypeError('fetch failed'); }))).toBe('upstream_unavailable');
  });

  it('timeout → timeout', async () => {
    const err = new DOMException('timed out', 'TimeoutError');
    expect(await kindOf(build(async () => { throw err; }))).toBe('timeout');
  });
});
