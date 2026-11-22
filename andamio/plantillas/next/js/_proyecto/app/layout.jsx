import { Layout } from '@/components';
import './globals.css';
// --- andamio:estilos (no borrar esta línea) ---

/** @type {import('next').Metadata} */
export const metadata = {
  title: '@@proyectoTitulo@@',
};

/**
 * Layout principal: envuelve a todas las páginas con el menú y el pie (components/Layout).
 * Con Next.js no hace falta registrar las rutas: cada carpeta de app/ con un page.jsx
 * es una dirección; andamio agrega el enlace en el menú (components/Navbar).
 */
export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <Layout>{children}</Layout>
      </body>
    </html>
  );
}
