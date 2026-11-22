// guía: Lo delicado del login: cómo se guardan las contraseñas y cómo se arman y se leen los tokens.
/**
 * Contraseñas (hash con PBKDF2, como Django) y tokens JWT (como SimpleJWT).
 *
 * - La contraseña nunca se guarda: se guarda un hash con "sal" (un valor al azar por usuario).
 *   Para comprobarla, se calcula el hash de lo que escribió la persona y se compara.
 * - El token de acceso dura poco (60 minutos); el de refresco sirve para pedir otro sin volver
 *   a escribir la contraseña (7 días). Los dos van firmados con SECRET_KEY (el .env): si
 *   alguien cambia una letra del token, la firma ya no coincide y la API lo rechaza.
 */
import { pbkdf2Sync, randomBytes, timingSafeEqual } from 'node:crypto';
import { jwtVerify, SignJWT } from 'jose';
import { SECRET_KEY } from '../config.js';
import { prisma } from '../db.js';

/** @typedef {import('../generated/prisma/client.js').Usuario} Usuario */

const ITERACIONES = 600_000; // las que recomienda OWASP para PBKDF2-SHA256
const CLAVE = new TextEncoder().encode(SECRET_KEY);
const DURACION = { access: '60m', refresh: '7d' };

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
 * @param {string} guardado el hash guardado (hashDe)
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
 * @param {Usuario} usuario
 * @param {'access' | 'refresh'} tipo
 */
export function crearToken(usuario, tipo) {
  return new SignJWT({ tipo })
    .setProtectedHeader({ alg: 'HS256' })
    .setSubject(String(usuario.id))
    .setExpirationTime(DURACION[tipo])
    .sign(CLAVE);
}

/**
 * El usuario dueño del token, o null si el token no es válido, venció o es de otro tipo.
 * @param {string} token
 * @param {'access' | 'refresh'} tipo
 * @returns {Promise<Usuario | null>}
 */
export async function usuarioDelToken(token, tipo) {
  try {
    const { payload } = await jwtVerify(token, CLAVE, { algorithms: ['HS256'] });
    if (payload.tipo !== tipo) return null;
    const usuario = await prisma.usuario.findUnique({ where: { id: Number(payload.sub) } });
    return usuario?.activo ? usuario : null;
  } catch {
    return null;
  }
}

/**
 * Middleware para las rutas que piden login: lee Authorization: Bearer <token>, y si sirve
 * deja el usuario en res.locals.usuario. Sin token o con uno que no sirve: 401.
 * Uso:  router.post('/', requiereSesion, async (req, res) => { ... })
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
export async function requiereSesion(req, res, next) {
  const [tipo, token] = (req.headers.authorization ?? '').split(' ');
  if (tipo !== 'Bearer' || !token) {
    res.status(401).json({ detail: 'Las credenciales de autenticación no se proveyeron.' });
    return;
  }
  const usuario = await usuarioDelToken(token, 'access');
  if (!usuario) {
    res.status(401).json({ detail: 'El token no es válido o expiró.' });
    return;
  }
  res.locals.usuario = usuario;
  next();
}
