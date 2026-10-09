export { useChat } from './hooks/useChat';
export type { UseChatResult } from './hooks/useChat';
export { chatService } from './services/chatService';
export { ChatError, validateMessage, MAX_MESSAGE_LENGTH } from './models/chat';
export type {
  ChatErrorKind,
  ChatMessage,
  ChatRequest,
  ChatResponse,
  ChatRole,
} from './models/chat';
