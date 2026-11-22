// guía: Ingresar (POST /api/token/): con usuario y contraseña, el token de acceso y el de refresco.
import { prisma } from '@/lib/db';
import { leerJson, responder, validar } from '@/lib/errores';
import { passwordCorrecta } from '@/lib/sesion';
import { cookieDeSesion, crearToken } from '@/lib/tokens';
import { Credenciales } from '@/lib/usuarios';

const CREDENCIALES_INCORRECTAS = 'No se encontró una cuenta de usuario activa para las credenciales dadas';

export async function POST(request: Request) {
  return responder(async () => {
    const { username, password } = validar(Credenciales, await leerJson(request));
    const usuario = await prisma.usuario.findUnique({ where: { username } });
    if (!usuario?.activo || !passwordCorrecta(password, usuario.passwordHash)) {
      return Response.json({ detail: CREDENCIALES_INCORRECTAS }, { status: 401 });
    }
    const access = await crearToken(usuario.id, 'access');
    const refresh = await crearToken(usuario.id, 'refresh');
    // guía: Las otras apps (React, React Native...) usan los tokens de la respuesta; las páginas
    // guía: de este proyecto, la cookie, que el navegador guarda y manda sola.
    return Response.json({ access, refresh }, { headers: { 'Set-Cookie': cookieDeSesion(access, request) } });
  });
}
