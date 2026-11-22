// guía: Los tokens y la cookie de la sesión. No usa la base de datos: así lo puede usar proxy.ts.
/**
 * Tokens JWT (como SimpleJWT de Django) y la cookie de la sesión.
 *
 * - El token de acceso dura poco (60 minutos); el de refresco sirve para pedir otro sin volver
 *   a escribir la contraseña (7 días). Los dos van firmados con SECRET_KEY (el .env): si
 *   alguien cambia una letra del token, la firma ya no coincide y la API lo rechaza.
 * - Las páginas de este proyecto no guardan el token: la API lo deja en una cookie httpOnly
 *   (el JavaScript de la página no la puede leer, así que un script malicioso tampoco) y el
 *   navegador la manda sola en cada pedido a este mismo sitio.
 */
import { jwtVerify, SignJWT } from 'jose';

// Con esta clave se firman los tokens: si alguien la conoce, puede armar tokens válidos.
// Va en el .env (que no se sube a git); cambiala en cada instalación.
const CLAVE = new TextEncoder().encode(process.env.SECRET_KEY || 'cambiar-por-una-clave-larga-y-secreta');
const DURACION = { access: 60 * 60, refresh: 7 * 24 * 60 * 60 }; // en segundos

/** @typedef {keyof typeof DURACION} TipoDeToken */

/** El nombre de la cookie con el token de acceso. */
export const COOKIE = 'sesion';

/**
 * @param {number} idUsuario
 * @param {TipoDeToken} tipo
 * @returns {Promise<string>}
 */
export function crearToken(idUsuario, tipo) {
  return new SignJWT({ tipo })
    .setProtectedHeader({ alg: 'HS256' })
    .setSubject(String(idUsuario))
    .setExpirationTime(`${DURACION[tipo]}s`)
    .sign(CLAVE);
}

/**
 * El id del usuario dueño del token, o null si no es válido, venció o es de otro tipo.
 * @param {string | undefined} token
 * @param {TipoDeToken} tipo
 * @returns {Promise<number | null>}
 */
export async function idDelToken(token, tipo) {
  if (!token) return null;
  try {
    const { payload } = await jwtVerify(token, CLAVE, { algorithms: ['HS256'] });
    return payload.tipo === tipo ? Number(payload.sub) : null;
  } catch {
    return null;
  }
}

/**
 * El encabezado Set-Cookie que guarda el token de acceso en el navegador. HttpOnly: el
 * JavaScript de la página no la ve. SameSite=Lax: no viaja en los pedidos que arma otro
 * sitio (protege de CSRF). Secure (con https): solo viaja cifrada.
 * @param {string} token
 * @param {Request} request
 */
export function cookieDeSesion(token, request) {
  const segura = new URL(request.url).protocol === 'https:' ? '; Secure' : '';
  return `${COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${DURACION.access}${segura}`;
}

/** El Set-Cookie que borra la cookie de la sesión (salir). */
export function cookieBorrada() {
  return `${COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`;
}
