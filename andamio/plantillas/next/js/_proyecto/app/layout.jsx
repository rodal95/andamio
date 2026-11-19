import Link from 'next/link';
import './globals.css';
import styles from './layout.module.css';

/** @type {import('next').Metadata} */
export const metadata = {
  title: '@@proyectoTitulo@@',
};

/**
 * Layout principal: envuelve a todas las páginas. Acá está el menú de navegación;
 * andamio agrega un enlace por cada página que generes. Con Next.js no hace falta
 * registrar las rutas: cada carpeta de app/ con un page.jsx es una dirección.
 */
export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <nav className={styles.menu}>
          <Link href="/">Inicio</Link>
          {/* --- andamio:enlaces (no borrar esta línea) --- */}
        </nav>
        <main className={styles.contenido}>{children}</main>
      </body>
    </html>
  );
}
