import type { NextConfig } from 'next';

// Configuración de Next.js (https://nextjs.org/docs/app/api-reference/config/next-config-js).
const nextConfig: NextConfig = {
  // Las direcciones terminan con barra (/api/productos/), como en las APIs de Django,
  // FastAPI y Express: así los mismos servicios sirven para todas.
  trailingSlash: true,
};

export default nextConfig;
