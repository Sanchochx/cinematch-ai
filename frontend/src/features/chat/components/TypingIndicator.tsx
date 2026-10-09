import styles from './TypingIndicator.module.css';

export function TypingIndicator(): React.JSX.Element {
  return (
    <li className={styles.row}>
      <div className={styles.bubble}>
        <span className={styles.srOnly}>El asistente está escribiendo</span>
        <span className={styles.dots} aria-hidden="true">
          <span />
          <span />
          <span />
        </span>
      </div>
    </li>
  );
}
