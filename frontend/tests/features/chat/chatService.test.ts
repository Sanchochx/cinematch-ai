import { afterEach, describe, expect, it, vi } from 'vitest';
import { ChatError, isChatResponse, validateMessage } from '../../../src/features/chat/models/chat';
import type { ChatErrorKind } from '../../../src/features/chat/models/chat';
import { chatService } from '../../../src/features/chat/services/chatService';

const request = { message: 'hola', history: [] };
const json = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status });

afterEach(() => vi.unstubAllGlobals());

async function kindOf(promise: Promise<unknown>): Promise<ChatErrorKind | 'other'> {
  try {
    await promise;
  } catch (e) {
    return e instanceof ChatError ? e.kind : 'other';
  }
  return 'other';
}

describe('chatService.sendMessage', () => {
  it('hace POST /api/chat con JSON y devuelve la respuesta', async () => {
    const fetchMock = vi.fn().mockResolvedValue(json(200, { reply: 'Arrival' }));
    vi.stubGlobal('fetch', fetchMock);
    const signal = new AbortController().signal;

    await expect(chatService.sendMessage(request, signal)).resolves.toEqual({ reply: 'Arrival' });

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('http://localhost:3000/api/chat');
    expect(init.method).toBe('POST');
    expect(init.headers).toEqual({ 'Content-Type': 'application/json' });
    expect(JSON.parse(init.body as string)).toEqual(request);
    expect(init.signal).toBe(signal);
  });

  it.each<[number, ChatErrorKind]>([
    [400, 'validation'],
    [429, 'rate_limited'],
    [502, 'unavailable'],
    [503, 'unavailable'],
    [504, 'timeout'],
    [500, 'unknown'],
    [404, 'unknown'],
  ])('status %i → %s', async (status, kind) => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(json(status, { error: 'x', message: 'detalle técnico' })),
    );
    const promise = chatService.sendMessage(request);
    expect(await kindOf(promise)).toBe(kind);
  });

  it('fallo de red/CORS → network', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    expect(await kindOf(chatService.sendMessage(request))).toBe('network');
  });

  it('respuesta 200 con forma inesperada → unknown', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(json(200, { reply: 3 })));
    expect(await kindOf(chatService.sendMessage(request))).toBe('unknown');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>', { status: 200 })));
    expect(await kindOf(chatService.sendMessage(request))).toBe('unknown');
  });

  it('los mensajes de error están en español y sin detalles técnicos', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(json(503, { message: 'ai-engine:8000' })));
    const error = await chatService.sendMessage(request).catch((e: unknown) => e);
    expect((error as ChatError).message).not.toMatch(/ai-engine|8000|fetch/i);
  });

  it('propaga el AbortError al cancelar', async () => {
    const controller = new AbortController();
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url: string, init: RequestInit) =>
          new Promise((_resolve, reject) => {
            init.signal?.addEventListener('abort', () =>
              reject(new DOMException('abort', 'AbortError')),
            );
          }),
      ),
    );
    const promise = chatService.sendMessage(request, controller.signal);
    controller.abort();
    await expect(promise).rejects.toMatchObject({ name: 'AbortError' });
  });
});

describe('modelo', () => {
  it('validateMessage recorta, rechaza vacío y >2000', () => {
    expect(validateMessage('  hola ')).toEqual({ valid: true, message: 'hola' });
    expect(validateMessage('   ').valid).toBe(false);
    expect(validateMessage('a'.repeat(2000)).valid).toBe(true);
    expect(validateMessage('a'.repeat(2001)).valid).toBe(false);
  });

  it('isChatResponse', () => {
    expect(isChatResponse({ reply: 'x' })).toBe(true);
    expect(isChatResponse({ reply: 1 })).toBe(false);
    expect(isChatResponse(null)).toBe(false);
    expect(isChatResponse('x')).toBe(false);
  });
});
