import { z } from 'zod';

// Única fuente de verdad de los límites (idénticos a los del ai-engine).
export const CHAT_LIMITS = Object.freeze({
  MAX_MESSAGE_LENGTH: 2000,
  // El historial incluye respuestas largas del propio agente, no solo texto del usuario.
  MAX_HISTORY_ITEM_LENGTH: 10000,
  MAX_HISTORY_ITEMS: 20,
});

const historyItemSchema = z.object({
  role: z.enum(['user', 'assistant']),
  content: z.string().min(1).max(CHAT_LIMITS.MAX_HISTORY_ITEM_LENGTH),
});

// `z.object` descarta las claves desconocidas: el body del cliente nunca se reenvía tal cual.
export const chatRequestSchema = z.object({
  message: z.string().trim().min(1).max(CHAT_LIMITS.MAX_MESSAGE_LENGTH),
  history: z.array(historyItemSchema).max(CHAT_LIMITS.MAX_HISTORY_ITEMS).default([]),
});

export const chatResponseSchema = z.object({ reply: z.string() });
