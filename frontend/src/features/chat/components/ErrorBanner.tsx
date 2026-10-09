import type { ChatError } from '../models/chat';
import styles from './ErrorBanner.module.css';

interface ErrorBannerProps {
  error: ChatError;
  onRetry: () => void;
  disabled?: boolean;
}

export function ErrorBanner({
  error,
  onRetry,
  disabled = false,
}: ErrorBannerProps): React.JSX.Element {
  return (
    <div className={styles.banner} role="alert">
      <p className={styles.message}>{error.message}</p>
      <button type="button" className={styles.retry} onClick={onRetry} disabled={disabled}>
        Reintentar
      </button>
    </div>
  );
}
