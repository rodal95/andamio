// guía: Las contraseñas (hash) y quién hace cada pedido (por el token o la cookie).
/**
 * Contraseñas (hash con PBKDF2, como Django) y el usuario de cada pedido.
 *
 * La contraseña nunca se guarda: se guarda un hash con "sal" (un valor al azar por usuario).
 * Para comprobarla, se calcula el hash de lo que escribió la persona y se compara.
 */
import { pbkdf2Sync, randomBytes, timingSafeEqual } from 'node:crypto';
import type { Usuario } from '@/generated/prisma/client';
import { prisma } from '@/lib/db';
import { COOKIE, idDelToken, type TipoDeToken } from '@/lib/tokens';

const ITERACIONES = 600_000; // las que recomienda OWASP para PBKDF2-SHA256

/** El hash de una contraseña, con el formato pbkdf2_sha256$iteraciones$sal$hash. */
export function hashDe(password: string): string {
  const sal = randomBytes(16); // al azar: dos usuarios con la misma contraseña tienen hashes distintos
  const clave = pbkdf2Sync(password, sal, ITERACIONES, 32, 'sha256');
  return ['pbkdf2_sha256', ITERACIONES, sal.toString('base64'), clave.toString('base64')].join('$');
}

export function passwordCorrecta(password: string, guardado: string): boolean {
  const [, iteraciones, sal, clave] = guardado.split('$');
  if (!iteraciones || !sal || !clave) return false;
  const esperada = Buffer.from(clave, 'base64');
  const calculada = pbkdf2Sync(password, Buffer.from(sal, 'base64'), Number(iteraciones), esperada.length, 'sha256');
  // timingSafeEqual tarda lo mismo aunque difieran al principio: no da pistas a un atacante.
  return calculada.length === esperada.length && timingSafeEqual(calculada, esperada);
}

/** El usuario dueño del token, o null si el token no sirve o el usuario no está activo. */
export async function usuarioDelToken(token: string | undefined, tipo: TipoDeToken): Promise<Usuario | null> {
  const id = await idDelToken(token, tipo);
  const usuario = id === null ? null : await prisma.usuario.findUnique({ where: { id } });
  return usuario?.activo ? usuario : null;
}

/** El token del pedido: Authorization: Bearer <token> (otras apps) o la cookie (las páginas de este proyecto). */
function tokenDelPedido(request: Request): string | undefined {
  const [tipo, token] = (request.headers.get('authorization') ?? '').split(' ');
  if (tipo === 'Bearer' && token) return token;
  // Las cookies llegan juntas: "sesion=eyJ...; otra=1".
  for (const cookie of (request.headers.get('cookie') ?? '').split(';')) {
    const [nombre, ...valor] = cookie.trim().split('=');
    if (nombre === COOKIE) return valor.join('=');
  }
  return undefined;
}

/**
 * Para las rutas que piden login: el usuario del pedido o, sin sesión, la respuesta 401.
 *   const usuario = await pedirSesion(request);
 *   if (usuario instanceof Response) return usuario;
 */
export async function pedirSesion(request: Request): Promise<Usuario | Response> {
  const token = tokenDelPedido(request);
  if (!token) {
    return Response.json({ detail: 'Las credenciales de autenticación no se proveyeron.' }, { status: 401 });
  }
  return (await usuarioDelToken(token, 'access')) ?? Response.json({ detail: 'El token no es válido o expiró.' }, { status: 401 });
}
