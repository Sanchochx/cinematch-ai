import { useChat } from '../hooks/useChat';
import { ChatComposer } from './ChatComposer';
import { EmptyState } from './EmptyState';
import { ErrorBanner } from './ErrorBanner';
import { MessageList } from './MessageList';
import styles from './ChatWindow.module.css';

export function ChatWindow(): React.JSX.Element {
  const { messages, isLoading, error, send, retry } = useChat();
  const isEmpty = messages.length === 0;

  return (
    <div className={styles.window}>
      <header className={styles.header}>
        <h1 className={styles.title}>CineMatch AI</h1>
        <p className={styles.tagline}>Cuéntame qué te apetece ver y te recomiendo una película.</p>
      </header>
      <div className={styles.body}>
        {isEmpty ? (
          <EmptyState onSelect={(prompt) => void send(prompt)} disabled={isLoading} />
        ) : (
          <MessageList messages={messages} isLoading={isLoading} />
        )}
      </div>
      {error && <ErrorBanner error={error} onRetry={() => void retry()} disabled={isLoading} />}
      <ChatComposer onSend={send} isLoading={isLoading} />
    </div>
  );
}
