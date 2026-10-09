import type { ChatMessage } from '../models/chat';
import { FormattedText } from './FormattedText';
import styles from './MessageBubble.module.css';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps): React.JSX.Element {
  const isUser = message.role === 'user';
  return (
    <li className={`${styles.row} ${isUser ? styles.user : styles.assistant}`}>
      <div className={styles.bubble}>
        <span className={styles.author}>{isUser ? 'Tú' : 'CineMatch'}</span>
        {isUser ? (
          <p className={styles.plain}>{message.content}</p>
        ) : (
          <FormattedText text={message.content} />
        )}
        {message.status === 'error' && <span className={styles.failed}>No se pudo enviar</span>}
      </div>
    </li>
  );
}
