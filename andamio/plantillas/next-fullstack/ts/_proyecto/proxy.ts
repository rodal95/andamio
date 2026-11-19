/**
 * Permite que otras páginas usen la API de este proyecto (CORS): por ejemplo, una app
 * de React con Vite o de Expo en el navegador. Las páginas de este mismo proyecto no lo
 * necesitan. Las direcciones permitidas se configuran en CORS_ALLOWED_ORIGINS (.env).
 * Una app de React Native en el celular tampoco lo necesita.
 */
import { NextResponse, type NextRequest } from 'next/server';

const PERMITIDOS = (process.env.CORS_ALLOWED_ORIGINS ?? '')
  .split(',')
  .map((origen) => origen.trim())
  .filter(Boolean);

const CABECERAS = {
  'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

export function proxy(request: NextRequest) {
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

// Solo para las rutas de la API.
export const config = {
  matcher: '/api/:path*',
};
