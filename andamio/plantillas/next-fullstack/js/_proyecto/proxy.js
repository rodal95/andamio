/**
 * Se ejecuta en el servidor antes de cada pedido (Next.js lo llama "proxy"):
 * - La API (/api/...): permite que otras páginas la usen (CORS), por ejemplo una app de
 *   React con Vite o de Expo en el navegador. Las páginas de este mismo proyecto no lo
 *   necesitan. Las direcciones permitidas se configuran en CORS_ALLOWED_ORIGINS (.env).
 * - Las páginas que piden ingresar (con nuevo login): sin sesión, lleva a /ingresar.
 */
import { NextResponse } from 'next/server';
// --- andamio:imports_proxy (no borrar esta línea) ---

const PERMITIDOS = (process.env.CORS_ALLOWED_ORIGINS ?? '')
  .split(',')
  .map((origen) => origen.trim())
  .filter(Boolean);

const CABECERAS = {
  'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

/** @param {import('next/server').NextRequest} request */
export async function proxy(request) {
  if (request.nextUrl.pathname.startsWith('/api/')) {
    return cors(request);
  }
  // --- andamio:paginas (no borrar esta línea) ---
  return NextResponse.next();
}

/** @param {import('next/server').NextRequest} request */
function cors(request) {
  const cabeceras = new Headers(CABECERAS);
  const origen = request.headers.get('origin') ?? '';
  if (PERMITIDOS.includes(origen)) {
    cabeceras.set('Access-Control-Allow-Origin', origen);
    cabeceras.set('Vary', 'Origin');
  }
  // Antes de un POST, PUT, PATCH o DELETE, el navegador pregunta si puede (OPTIONS).
  if (request.method === 'OPTIONS') {
    return new NextResponse(null, { status: 204, headers: cabeceras });
  }
  const respuesta = NextResponse.next();
  cabeceras.forEach((valor, nombre) => respuesta.headers.set(nombre, valor));
  return respuesta;
}

// Todos los pedidos, menos los archivos que arma Next.js (_next/) y el ícono.
export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
