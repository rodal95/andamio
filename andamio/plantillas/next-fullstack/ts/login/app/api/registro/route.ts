// guía: Crear una cuenta (POST /api/registro/). Responde igual que la API de Django con nuevo login.
import { prisma } from '@/lib/db';
import { ErrorDeValidacion, leerJson, responder, validar } from '@/lib/errores';
import { hashDe } from '@/lib/sesion';
import { aJson, Registro } from '@/lib/usuarios';

/** Reglas para una contraseña (las mismas ideas que Django). */
function problemasDeLaPassword(password: string, username: string): string[] {
  // TODO(logica): más reglas si las necesitás (ej.: que tenga una mayúscula).
  const problemas = [];
  if (password.length < 8) problemas.push('La contraseña es demasiado corta. Debe contener al menos 8 caracteres.');
  if (/^\d+$/.test(password)) problemas.push('La contraseña está completamente en numérico.');
  if (username && password.toLowerCase().includes(username.toLowerCase())) {
    problemas.push('La contraseña es demasiado similar al nombre de usuario.');
  }
  return problemas;
}

export async function POST(request: Request) {
  return responder(async () => {
    const { password, ...datos } = validar(Registro, await leerJson(request));
    const errores: Record<string, string[]> = {};
    if (await prisma.usuario.findUnique({ where: { username: datos.username } })) {
      errores.username = ['Ya existe un usuario con este nombre.'];
    }
    const problemas = problemasDeLaPassword(password, datos.username);
    if (problemas.length) errores.password = problemas;
    // El mismo formato que los demás errores: {"campo": ["mensaje"]}.
    if (Object.keys(errores).length) throw new ErrorDeValidacion(errores);
    const usuario = await prisma.usuario.create({ data: { ...datos, passwordHash: hashDe(password) } });
    return Response.json(aJson(usuario), { status: 201 });
  });
}
