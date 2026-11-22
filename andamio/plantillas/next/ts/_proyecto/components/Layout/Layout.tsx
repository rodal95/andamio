// --- andamio:directivas (no borrar esta línea) ---
import type { ReactNode } from 'react';
import { Footer } from '../Footer';
import { Navbar } from '../Navbar';
import styles from './Layout.module.css';
// --- andamio:imports_layout (no borrar esta línea) ---

/**
 * Lo que se ve en todas las páginas: el menú (Navbar), la página y el pie (Footer).
 * Lo usa app/layout.tsx, que envuelve a todas las páginas.
 */
export function Layout({ children }: Readonly<{ children: ReactNode }>) {
  // --- andamio:layout (no borrar esta línea) ---
  return (
    <div className={styles.root}>
      <Navbar />
      <main className={styles.contenido}>{children}</main>
      <Footer />
    </div>
  );
}
