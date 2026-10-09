import { API_URL } from '../../../config/env';
import { ChatError, isChatResponse } from '../models/chat';
import type { ChatErrorKind, ChatRequest, ChatResponse } from '../models/chat';

function kindForStatus(status: number): ChatErrorKind {
  switch (status) {
    case 400:
      return 'validation';
    case 429:
      return 'rate_limited';
    case 502:
    case 503:
      return 'unavailable';
    case 504:
      return 'timeout';
    default:
      return 'unknown';
  }
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}

async function sendMessage(request: ChatRequest, signal?: AbortSignal): Promise<ChatResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: request.message, history: request.history }),
      signal,
    });
  } catch (error) {
    // La cancelación no es un fallo: se propaga tal cual para que el llamador la ignore.
    if (isAbortError(error)) throw error;
    throw new ChatError('network');
  }

  if (!response.ok) throw new ChatError(kindForStatus(response.status));

  let payload: unknown;
  try {
    payload = await response.json();
  } catch (error) {
    if (isAbortError(error)) throw error;
    throw new ChatError('unknown');
  }
  if (!isChatResponse(payload)) throw new ChatError('unknown');
  return { reply: payload.reply };
}

export const chatService = { sendMessage };
export { isAbortError };
