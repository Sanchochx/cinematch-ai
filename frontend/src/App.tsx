import styles from './App.module.css';

export default function App(): React.JSX.Element {
  return (
    <main className={styles.app}>
      <div>
        <h1 className={styles.title}>CineMatch AI</h1>
        <p className={styles.tagline}>Cuéntame qué te apetece ver y te recomiendo una película.</p>
      </div>
    </main>
  );
}
