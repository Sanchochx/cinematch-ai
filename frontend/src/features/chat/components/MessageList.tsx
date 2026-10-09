import { useEffect, useRef } from 'react';
import type { ChatMessage } from '../models/chat';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import styles from './MessageList.module.css';

interface MessageListProps {
  messages: readonly ChatMessage[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps): React.JSX.Element {
  const containerRef = useRef<HTMLDivElement>(null);

  // El contenedor tiene altura fija por layout, así que hacer scroll no provoca saltos de diseño (CLS).
  useEffect(() => {
    const container = containerRef.current;
    if (container) container.scrollTop = container.scrollHeight;
  }, [messages, isLoading]);

  return (
    <div
      ref={containerRef}
      className={styles.list}
      role="log"
      aria-live="polite"
      aria-label="Conversación"
      tabIndex={0}
    >
      <ul className={styles.items}>
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <TypingIndicator />}
      </ul>
    </div>
  );
}
