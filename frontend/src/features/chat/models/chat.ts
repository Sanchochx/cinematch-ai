export const MAX_MESSAGE_LENGTH = 2000;
export const MAX_HISTORY_ITEMS = 20;

export type ChatRole = 'user' | 'assistant';
export type ChatMessageStatus = 'sending' | 'sent' | 'error';
export type ChatErrorKind =
  'network' | 'validation' | 'rate_limited' | 'unavailable' | 'timeout' | 'unknown';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  status?: ChatMessageStatus;
}

export interface HistoryItem {
  role: ChatRole;
  content: string;
}

export interface ChatRequest {
  message: string;
  history: HistoryItem[];
}

export interface ChatResponse {
  reply: string;
}

export const CHAT_ERROR_MESSAGES: Record<ChatErrorKind, string> = {
  network: 'No se pudo conectar. Revisa tu conexión e inténtalo de nuevo.',
  validation: 'Tu mensaje no es válido. Revisa el texto e inténtalo de nuevo.',
  rate_limited: 'Demasiadas solicitudes. Espera un momento antes de volver a intentarlo.',
  unavailable: 'El servicio no está disponible ahora mismo. Inténtalo más tarde.',
  timeout: 'La respuesta ha tardado demasiado. Inténtalo de nuevo.',
  unknown: 'Ha ocurrido un error inesperado. Inténtalo de nuevo.',
};

export class ChatError extends Error {
  readonly kind: ChatErrorKind;

  constructor(kind: ChatErrorKind) {
    super(CHAT_ERROR_MESSAGES[kind]);
    this.name = 'ChatError';
    this.kind = kind;
  }
}

export function isChatResponse(value: unknown): value is ChatResponse {
  return (
    typeof value === 'object' &&
    value !== null &&
    'reply' in value &&
    typeof (value as { reply: unknown }).reply === 'string'
  );
}

export type MessageValidation =
  { valid: true; message: string } | { valid: false; error: ChatError };

export function validateMessage(text: string): MessageValidation {
  const message = text.trim();
  if (message.length === 0 || message.length > MAX_MESSAGE_LENGTH) {
    return { valid: false, error: new ChatError('validation') };
  }
  return { valid: true, message };
}

/** Historial para el backend: excluye mensajes fallidos o pendientes, recorta y deja solo role/content. */
export function toHistory(messages: readonly ChatMessage[]): HistoryItem[] {
  return messages
    .filter((m) => m.status === undefined || m.status === 'sent')
    .slice(-MAX_HISTORY_ITEMS)
    .map(({ role, content }) => ({ role, content }));
}
