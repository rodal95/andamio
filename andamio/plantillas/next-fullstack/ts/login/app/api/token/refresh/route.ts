// guía: Renovar (POST /api/token/refresh/): con el token de refresco, uno de acceso nuevo.
import { leerJson, responder, validar } from '@/lib/errores';
import { usuarioDelToken } from '@/lib/sesion';
import { cookieDeSesion, crearToken } from '@/lib/tokens';
import { Refresco } from '@/lib/usuarios';

export async function POST(request: Request) {
  return responder(async () => {
    const { refresh } = validar(Refresco, await leerJson(request));
    const usuario = await usuarioDelToken(refresh, 'refresh');
    if (!usuario) {
      return Response.json({ detail: 'El token no es válido o expiró.' }, { status: 401 });
    }
    const access = await crearToken(usuario.id, 'access');
    return Response.json({ access }, { headers: { 'Set-Cookie': cookieDeSesion(access, request) } });
  });
}
