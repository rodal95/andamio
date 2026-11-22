// guía: Las contraseñas (hash) y quién hace cada pedido (por el token o la cookie).
/**
 * Contraseñas (hash con PBKDF2, como Django) y el usuario de cada pedido.
 *
 * La contraseña nunca se guarda: se guarda un hash con "sal" (un valor al azar por usuario).
 * Para comprobarla, se calcula el hash de lo que escribió la persona y se compara.
 */
import { pbkdf2Sync, randomBytes, timingSafeEqual } from 'node:crypto';
import { prisma } from '@/lib/db';
import { COOKIE, idDelToken } from '@/lib/tokens';

/**
 * @typedef {import('@/generated/prisma/client').Usuario} Usuario
 * @typedef {import('@/lib/tokens').TipoDeToken} TipoDeToken
 */

const ITERACIONES = 600_000; // las que recomienda OWASP para PBKDF2-SHA256

/**
 * El hash de una contraseña, con el formato pbkdf2_sha256$iteraciones$sal$hash.
 * @param {string} password
 */
export function hashDe(password) {
  const sal = randomBytes(16); // al azar: dos usuarios con la misma contraseña tienen hashes distintos
  const clave = pbkdf2Sync(password, sal, ITERACIONES, 32, 'sha256');
  return ['pbkdf2_sha256', ITERACIONES, sal.toString('base64'), clave.toString('base64')].join('$');
}

/**
 * @param {string} password
 * @param {string} guardado
 */
export function passwordCorrecta(password, guardado) {
  const [, iteraciones, sal, clave] = guardado.split('$');
  if (!iteraciones || !sal || !clave) return false;
  const esperada = Buffer.from(clave, 'base64');
  const calculada = pbkdf2Sync(password, Buffer.from(sal, 'base64'), Number(iteraciones), esperada.length, 'sha256');
  // timingSafeEqual tarda lo mismo aunque difieran al principio: no da pistas a un atacante.
  return calculada.length === esperada.length && timingSafeEqual(calculada, esperada);
}

/**
 * Si puede ingresar: la contraseña es la del usuario y el usuario está activo. Si el usuario
 * no existe, igual calcula un hash (el de lo que escribió): así la respuesta tarda lo mismo
 * y no da pistas de qué usuarios existen. Lo mismo hace Django.
 * @param {Usuario | null} usuario
 * @param {string} password
 * @returns {usuario is Usuario}
 */
export function puedeIngresar(usuario, password) {
  if (!usuario) {
    hashDe(password); // el mismo trabajo que comprobarla
    return false;
  }
  return passwordCorrecta(password, usuario.passwordHash) && usuario.activo;
}

/**
 * El usuario dueño del token, o null si el token no sirve o el usuario no está activo.
 * @param {string | undefined} token
 * @param {TipoDeToken} tipo
 * @returns {Promise<Usuario | null>}
 */
export async function usuarioDelToken(token, tipo) {
  const id = await idDelToken(token, tipo);
  const usuario = id === null ? null : await prisma.usuario.findUnique({ where: { id } });
  return usuario?.activo ? usuario : null;
}

/**
 * El token del pedido: Authorization: Bearer <token> (otras apps) o la cookie (las páginas de este proyecto).
 * @param {Request} request
 * @returns {string | undefined}
 */
function tokenDelPedido(request) {
  const [tipo, token] = (request.headers.get('authorization') ?? '').split(' ');
  if (tipo === 'Bearer' && token) return token;
  // Las cookies llegan juntas: "sesion=eyJ...; otra=1".
  for (const cookie of (request.headers.get('cookie') ?? '').split(';')) {
    const [nombre, ...valor] = cookie.trim().split('=');
    if (nombre === COOKIE) return valor.join('=');
  }
  return undefined;
}

const METODOS_SEGUROS = new Set(['GET', 'HEAD', 'OPTIONS']);

/**
 * Si el pedido cambia datos con la cookie y viene de otra página (otro origen). El navegador
 * manda la cookie aunque el pedido lo arme otro sitio (CSRF): en POST, PUT, PATCH y DELETE
 * se pide que el encabezado Origin sea el de esta misma app. Con Bearer no hace falta:
 * el token no lo agrega el navegador solo.
 * @param {Request} request
 */
function deOtroOrigen(request) {
  if (METODOS_SEGUROS.has(request.method)) return false;
  if ((request.headers.get('authorization') ?? '').startsWith('Bearer ')) return false;
  const origen = request.headers.get('origin');
  const host = request.headers.get('x-forwarded-host') ?? request.headers.get('host');
  try {
    return !origen || !host || new URL(origen).host !== host;
  } catch {
    return true;
  }
}

/**
 * Para las rutas que piden login: el usuario del pedido o, sin sesión, la respuesta 401.
 *   const usuario = await pedirSesion(request);
 *   if (usuario instanceof Response) return usuario;
 * @param {Request} request
 * @returns {Promise<Usuario | Response>}
 */
export async function pedirSesion(request) {
  const token = tokenDelPedido(request);
  if (!token) {
    return Response.json({ detail: 'Las credenciales de autenticación no se proveyeron.' }, { status: 401 });
  }
  if (deOtroOrigen(request)) {
    return Response.json({ detail: 'El pedido viene de otro sitio (CSRF).' }, { status: 403 });
  }
  return (await usuarioDelToken(token, 'access')) ?? Response.json({ detail: 'El token no es válido o expiró.' }, { status: 401 });
}
