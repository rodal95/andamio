import { Outlet } from 'react-router';
import { Footer } from '../Footer';
import { Navbar } from '../Navbar';
import styles from './Layout.module.css';
// --- andamio:imports_layout (no borrar esta línea) ---

/**
 * Lo que se ve en todas las páginas: el menú (Navbar), la página de la ruta (Outlet) y el
 * pie (Footer). Son las rutas que en App.tsx están dentro de <Route element={<Layout />}>.
 */
export function Layout() {
  // --- andamio:layout (no borrar esta línea) ---
  return (
    <div className={styles.root}>
      <Navbar />
      <main className={styles.contenido}>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
