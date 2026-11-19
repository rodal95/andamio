import type { Metadata } from 'next';
import Link from 'next/link';
import type { ReactNode } from 'react';
import './globals.css';
import styles from './layout.module.css';

export const metadata: Metadata = {
  title: '@@proyectoTitulo@@',
};

/**
 * Layout principal: envuelve a todas las páginas. Acá está el menú de navegación;
 * andamio agrega un enlace por cada página que generes. Con Next.js no hace falta
 * registrar las rutas: cada carpeta de app/ con un page.tsx es una dirección.
 */
export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
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
