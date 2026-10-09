import { useId, useRef, useState } from 'react';
import type { ChangeEvent, FormEvent, KeyboardEvent } from 'react';
import { MAX_MESSAGE_LENGTH, validateMessage } from '../models/chat';
import styles from './ChatComposer.module.css';

interface ChatComposerProps {
  onSend: (text: string) => Promise<void>;
  isLoading: boolean;
}

export function ChatComposer({ onSend, isLoading }: ChatComposerProps): React.JSX.Element {
  const [draft, setDraft] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const id = useId();
  const counterId = `${id}-counter`;
  const errorId = `${id}-error`;

  const tooLong = draft.length > MAX_MESSAGE_LENGTH;
  const canSend = validateMessage(draft).valid && !isLoading;

  const submit = (): void => {
    if (!canSend) return;
    const text = draft;
    setDraft('');
    textareaRef.current?.focus();
    void onSend(text);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    submit();
  };

  // Enter envía; Shift+Enter inserta salto de línea. Se ignora durante la composición IME.
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <label className={styles.srOnly} htmlFor={`${id}-input`}>
        Tu mensaje
      </label>
      <textarea
        id={`${id}-input`}
        ref={textareaRef}
        className={styles.input}
        rows={2}
        value={draft}
        placeholder="Escribe qué te apetece ver…"
        aria-invalid={tooLong}
        aria-describedby={tooLong ? `${counterId} ${errorId}` : counterId}
        onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setDraft(event.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button type="submit" className={styles.send} disabled={!canSend}>
        Enviar
      </button>
      <p id={counterId} className={styles.counter}>
        {draft.length} / {MAX_MESSAGE_LENGTH}
      </p>
      {tooLong && (
        <p id={errorId} className={styles.error}>
          El mensaje no puede superar los {MAX_MESSAGE_LENGTH} caracteres.
        </p>
      )}
    </form>
  );
}
