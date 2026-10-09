import { chatResponseSchema } from '../models/chatRequest.js';

// Cada `kind` se traduce a un status HTTP y un mensaje genérico en la ruta; nada del upstream se propaga.
export class AiEngineError extends Error {
  constructor(kind) {
    super(kind);
    this.name = 'AiEngineError';
    this.kind = kind;
  }
}

function kindForStatus(status) {
  return status === 503 ? 'upstream_unavailable' : 'upstream_error';
}

export function createAiEngineClient({ baseUrl, timeoutMs, fetchImpl = fetch }) {
  return {
    async chat({ message, history }) {
      let response;
      try {
        response = await fetchImpl(`${baseUrl}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, history }),
          signal: AbortSignal.timeout(timeoutMs),
        });
      } catch (err) {
        throw new AiEngineError(err?.name === 'TimeoutError' ? 'timeout' : 'upstream_unavailable');
      }

      if (!response.ok) throw new AiEngineError(kindForStatus(response.status));

      let payload;
      try {
        payload = await response.json();
      } catch (err) {
        if (err?.name === 'TimeoutError') throw new AiEngineError('timeout');
        throw new AiEngineError('upstream_error');
      }
      const parsed = chatResponseSchema.safeParse(payload);
      if (!parsed.success) throw new AiEngineError('upstream_error');
      return { reply: parsed.data.reply };
    },
  };
}
