import { lazy, Suspense } from 'react';
import styles from './App.module.css';

// Bundle splitting por feature: el chat se descarga bajo demanda.
const ChatWindow = lazy(() => import('./features/chat').then((m) => ({ default: m.ChatWindow })));

export default function App(): React.JSX.Element {
  return (
    <main className={styles.app}>
      <Suspense
        fallback={<div className={styles.fallback} role="status" aria-label="Cargando chat" />}
      >
        <ChatWindow />
      </Suspense>
    </main>
  );
}
