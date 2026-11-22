import { Link } from 'react-router';
import styles from './Navbar.module.css';
// --- andamio:imports_navbar (no borrar esta línea) ---

/**
 * El menú de navegación, arriba de todas las páginas (lo muestra el Layout). andamio agrega
 * acá un enlace por cada página que generes. Para que en el celular se pliegue en un botón ☰:
 * python -m andamio nuevo ui navbar.
 */
export function Navbar() {
  return (
    <nav className={styles.root}>
      <Link to="/">Inicio</Link>
      {/* --- andamio:enlaces (no borrar esta línea) --- */}
    </nav>
  );
}
