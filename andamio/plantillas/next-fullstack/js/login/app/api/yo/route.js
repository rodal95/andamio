// guía: Quién soy (GET /api/yo/): el usuario del token o de la cookie. Sin sesión: 401.
import { pedirSesion } from '@/lib/sesion';
import { aJson } from '@/lib/usuarios';

/** @param {Request} request */
export async function GET(request) {
  const usuario = await pedirSesion(request);
  if (usuario instanceof Response) return usuario;
  return Response.json(aJson(usuario));
}
