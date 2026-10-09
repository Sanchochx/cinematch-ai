import { SUGGESTED_PROMPTS } from '../models/suggestions';
import styles from './EmptyState.module.css';

interface EmptyStateProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

export function EmptyState({ onSelect, disabled = false }: EmptyStateProps): React.JSX.Element {
  return (
    <div className={styles.empty}>
      <h2 className={styles.title}>¿Qué te apetece ver hoy?</h2>
      <p className={styles.text}>
        Cuéntame qué tipo de película buscas y te recomendaré opciones. También puedes empezar con
        una idea:
      </p>
      <ul className={styles.suggestions}>
        {SUGGESTED_PROMPTS.map((prompt) => (
          <li key={prompt}>
            <button
              type="button"
              className={styles.suggestion}
              disabled={disabled}
              onClick={() => onSelect(prompt)}
            >
              {prompt}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
