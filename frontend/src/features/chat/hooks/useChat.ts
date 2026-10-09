import { useCallback, useEffect, useRef, useState } from 'react';
import { ChatError, toHistory, validateMessage } from '../models/chat';
import type { ChatMessage, ChatMessageStatus, ChatRequest } from '../models/chat';
import { chatService, isAbortError } from '../services/chatService';

export interface UseChatResult {
  messages: ChatMessage[];
  isLoading: boolean;
  error: ChatError | null;
  send: (text: string) => Promise<void>;
  retry: () => Promise<void>;
}

interface PendingAttempt {
  userMessageId: string;
  request: ChatRequest;
}

export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ChatError | null>(null);

  // Los refs evitan closures obsoletas y permiten bloquear envíos concurrentes de forma síncrona.
  const messagesRef = useRef<ChatMessage[]>([]);
  const inFlightRef = useRef(false);
  const controllerRef = useRef<AbortController | null>(null);
  const failedRef = useRef<PendingAttempt | null>(null);

  const commit = useCallback((next: ChatMessage[]): void => {
    messagesRef.current = next;
    setMessages(next);
  }, []);

  const setStatus = useCallback(
    (id: string, status: ChatMessageStatus): void => {
      commit(messagesRef.current.map((m) => (m.id === id ? { ...m, status } : m)));
    },
    [commit],
  );

  useEffect(
    () => () => {
      controllerRef.current?.abort();
    },
    [],
  );

  const dispatch = useCallback(
    async (attempt: PendingAttempt): Promise<void> => {
      const controller = new AbortController();
      controllerRef.current = controller;
      inFlightRef.current = true;
      setIsLoading(true);
      setError(null);
      failedRef.current = null;

      try {
        const { reply } = await chatService.sendMessage(attempt.request, controller.signal);
        if (controller.signal.aborted) return;
        commit([
          ...messagesRef.current.map((m) =>
            m.id === attempt.userMessageId ? { ...m, status: 'sent' as const } : m,
          ),
          { id: crypto.randomUUID(), role: 'assistant', content: reply, status: 'sent' },
        ]);
      } catch (e) {
        if (controller.signal.aborted || isAbortError(e)) return;
        setStatus(attempt.userMessageId, 'error');
        failedRef.current = attempt;
        setError(e instanceof ChatError ? e : new ChatError('unknown'));
      } finally {
        if (controllerRef.current === controller) {
          controllerRef.current = null;
          inFlightRef.current = false;
          if (!controller.signal.aborted) setIsLoading(false);
        }
      }
    },
    [commit, setStatus],
  );

  const send = useCallback(
    async (text: string): Promise<void> => {
      if (inFlightRef.current) return;
      const validation = validateMessage(text);
      if (!validation.valid) {
        setError(validation.error);
        return;
      }

      const request: ChatRequest = {
        message: validation.message,
        history: toHistory(messagesRef.current),
      };
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: validation.message,
        status: 'sending',
      };
      commit([...messagesRef.current, userMessage]);
      await dispatch({ userMessageId: userMessage.id, request });
    },
    [commit, dispatch],
  );

  const retry = useCallback(async (): Promise<void> => {
    const attempt = failedRef.current;
    if (inFlightRef.current || attempt === null) return;
    setStatus(attempt.userMessageId, 'sending');
    await dispatch(attempt);
  }, [dispatch, setStatus]);

  return { messages, isLoading, error, send, retry };
}
