import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ChatError } from '../../../src/features/chat/models/chat';
import type { ChatRequest, ChatResponse } from '../../../src/features/chat/models/chat';
import { useChat } from '../../../src/features/chat/hooks/useChat';
import { chatService } from '../../../src/features/chat/services/chatService';

type SendMock = ReturnType<typeof mockSend>;
const mockSend = () => vi.spyOn(chatService, 'sendMessage');

afterEach(() => vi.restoreAllMocks());

function deferred<T>(): {
  promise: Promise<T>;
  resolve: (v: T) => void;
  reject: (e: unknown) => void;
} {
  let resolve!: (v: T) => void;
  let reject!: (e: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

const ok = (reply: string): Promise<ChatResponse> => Promise.resolve({ reply });
const lastRequest = (m: SendMock): ChatRequest => m.mock.calls.at(-1)![0];

describe('useChat', () => {
  it('añade el mensaje del usuario y la respuesta del asistente', async () => {
    mockSend().mockImplementation(() => ok('Arrival'));
    const { result } = renderHook(() => useChat());

    await act(() => result.current.send('  hola  '));

    expect(
      result.current.messages.map(({ role, content, status }) => ({ role, content, status })),
    ).toEqual([
      { role: 'user', content: 'hola', status: 'sent' },
      { role: 'assistant', content: 'Arrival', status: 'sent' },
    ]);
    expect(result.current.error).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  it('muestra el mensaje de forma optimista mientras carga', async () => {
    const d = deferred<ChatResponse>();
    mockSend().mockReturnValue(d.promise);
    const { result } = renderHook(() => useChat());

    act(() => void result.current.send('hola'));

    expect(result.current.isLoading).toBe(true);
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]?.status).toBe('sending');
    await act(async () => d.resolve({ reply: 'x' }));
    expect(result.current.isLoading).toBe(false);
  });

  it.each([
    ['vacío', '   '],
    ['demasiado largo', 'a'.repeat(2001)],
  ])('rechaza mensaje %s sin llamar al servicio', async (_n, text) => {
    const m = mockSend();
    const { result } = renderHook(() => useChat());
    await act(() => result.current.send(text));
    expect(m).not.toHaveBeenCalled();
    expect(result.current.messages).toEqual([]);
    expect(result.current.error?.kind).toBe('validation');
  });

  it('bloquea envíos concurrentes', async () => {
    const d = deferred<ChatResponse>();
    const m = mockSend().mockReturnValue(d.promise);
    const { result } = renderHook(() => useChat());

    act(() => {
      void result.current.send('uno');
      void result.current.send('dos');
    });
    expect(m).toHaveBeenCalledTimes(1);
    expect(result.current.messages).toHaveLength(1);
    await act(async () => d.resolve({ reply: 'x' }));
  });

  it('envía el historial sin el mensaje actual, limitado a 20 y solo con role/content', async () => {
    const m = mockSend().mockImplementation(() => ok('r'));
    const { result } = renderHook(() => useChat());

    for (let i = 0; i < 13; i++) await act(() => result.current.send(`m${i}`));
    // Antes del envío 13 había 24 mensajes → historial recortado a los últimos 20.
    const history = lastRequest(m).history;
    expect(lastRequest(m).message).toBe('m12');
    expect(history).toHaveLength(20);
    expect(history.at(-1)).toEqual({ role: 'assistant', content: 'r' });
    expect(Object.keys(history[0]!).sort()).toEqual(['content', 'role']);
    expect(history.some((h) => h.content === 'm12')).toBe(false);
  });

  it('en error conserva el mensaje y retry reenvía sin duplicarlo', async () => {
    const m = mockSend()
      .mockRejectedValueOnce(new ChatError('unavailable'))
      .mockImplementation(() => ok('ya'));
    const { result } = renderHook(() => useChat());

    await act(() => result.current.send('hola'));
    expect(result.current.error?.kind).toBe('unavailable');
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]?.status).toBe('error');

    await act(() => result.current.retry());
    expect(m).toHaveBeenCalledTimes(2);
    expect(m.mock.calls[1]![0]).toEqual(m.mock.calls[0]![0]);
    expect(result.current.error).toBeNull();
    expect(result.current.messages.map((x) => x.content)).toEqual(['hola', 'ya']);
    expect(result.current.messages[0]?.status).toBe('sent');
  });

  it('el historial excluye mensajes fallidos', async () => {
    const m = mockSend()
      .mockRejectedValueOnce(new ChatError('timeout'))
      .mockImplementation(() => ok('r'));
    const { result } = renderHook(() => useChat());
    await act(() => result.current.send('falla'));
    await act(() => result.current.send('siguiente'));
    expect(lastRequest(m).history).toEqual([]);
  });

  it('retry sin error previo no hace nada', async () => {
    const m = mockSend();
    const { result } = renderHook(() => useChat());
    await act(() => result.current.retry());
    expect(m).not.toHaveBeenCalled();
  });

  it('errores desconocidos se convierten en ChatError unknown', async () => {
    mockSend().mockRejectedValue(new Error('boom'));
    const { result } = renderHook(() => useChat());
    await act(() => result.current.send('hola'));
    expect(result.current.error?.kind).toBe('unknown');
  });

  it('cancela la petición al desmontar y no actualiza estado tarde', async () => {
    let signal: AbortSignal | undefined;
    const d = deferred<ChatResponse>();
    mockSend().mockImplementation((_req, s) => {
      signal = s;
      return d.promise;
    });
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    const { result, unmount } = renderHook(() => useChat());

    act(() => void result.current.send('hola'));
    unmount();
    expect(signal?.aborted).toBe(true);

    d.reject(new DOMException('abort', 'AbortError'));
    await waitFor(() => expect(errorSpy).not.toHaveBeenCalled());
  });
});
