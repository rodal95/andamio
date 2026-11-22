import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { Layout } from '@/components';
import './globals.css';
// --- andamio:estilos (no borrar esta línea) ---

export const metadata: Metadata = {
  title: '@@proyectoTitulo@@',
};

/**
 * Layout principal: envuelve a todas las páginas con el menú y el pie (components/Layout).
 * Con Next.js no hace falta registrar las rutas: cada carpeta de app/ con un page.tsx
 * es una dirección; andamio agrega el enlace en el menú (components/Navbar).
 */
export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="es">
      <body>
        <Layout>{children}</Layout>
      </body>
    </html>
  );
}
