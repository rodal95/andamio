// --- andamio:directivas (no borrar esta línea) ---
import { Footer } from '../Footer';
import { Navbar } from '../Navbar';
import styles from './Layout.module.css';
// --- andamio:imports_layout (no borrar esta línea) ---

/**
 * Lo que se ve en todas las páginas: el menú (Navbar), la página y el pie (Footer).
 * Lo usa app/layout.jsx, que envuelve a todas las páginas.
 * @param {{ children: import('react').ReactNode }} props
 */
export function Layout({ children }) {
  // --- andamio:layout (no borrar esta línea) ---
  return (
    <div className={styles.root}>
      <Navbar />
      <main className={styles.contenido}>{children}</main>
      <Footer />
    </div>
  );
}
