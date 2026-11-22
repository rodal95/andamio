// guía: Qué páginas piden ingresar. Lo usa proxy.ts antes de mostrar cada página.
/**
 * Las páginas que piden ingresar. proxy.ts lo consulta en el servidor antes de mostrar cada
 * página: sin sesión (la cookie con un token válido), manda a /ingresar y después vuelve.
 * Así la página ni siquiera llega al navegador.
 */
import { NextResponse } from 'next/server';
import { COOKIE, idDelToken } from '@/lib/tokens';

// Las páginas que piden ingresar (y las que estén adentro: /perfil abarca /perfil/datos).
// nuevo pagina X --protegido y nuevo crud X --protegido agregan las suyas; [id] es cualquier valor.
/** @type {string[]} */
const PAGINAS = [
  // --- andamio:paginas_protegidas (no borrar esta línea) ---
];

// Con nuevo login --obligatorio, todas (salvo las del login).
const TODAS = @@todas@@;

const DEL_LOGIN = ['/ingresar', '/registro'];

const ARCHIVO_PUBLICO = /\.(png|jpe?g|gif|svg|webp|avif|ico|txt|xml|webmanifest|json|css|js|map|woff2?|ttf|otf|pdf|mp4|webm|mp3)$/i;

/**
 * Si la ruta es la de la página o está adentro.
 * @param {string} pagina
 * @param {string} ruta
 */
function abarca(pagina, ruta) {
  const partes = pagina.split('/').filter(Boolean);
  const deLaRuta = ruta.split('/').filter(Boolean);
  return partes.length <= deLaRuta.length && partes.every((parte, i) => parte.startsWith('[') || parte === deLaRuta[i]);
}

/** @param {string} ruta */
function pideIngreso(ruta) {
  // Los archivos de public/ (logo.png...) y las páginas del login siempre se ven. Solo con
  // estas extensiones: con cualquier punto, /productos/1.x se saltearía el ingreso.
  if (ARCHIVO_PUBLICO.test(ruta) || DEL_LOGIN.some((pagina) => abarca(pagina, ruta))) return false;
  return TODAS || PAGINAS.some((pagina) => abarca(pagina, ruta));
}

/**
 * Si la página pide ingresar y no hay sesión, la respuesta que lleva a /ingresar. Si no, null.
 * @param {import('next/server').NextRequest} request
 * @returns {Promise<NextResponse | null>}
 */
export async function pedirIngreso(request) {
  const { pathname, search } = request.nextUrl;
  if (!pideIngreso(pathname) || (await idDelToken(request.cookies.get(COOKIE)?.value, 'access')) !== null) {
    return null;
  }
  const ingresar = new URL('/ingresar/', request.url);
  ingresar.searchParams.set('desde', pathname + search);
  return NextResponse.redirect(ingresar);
}
