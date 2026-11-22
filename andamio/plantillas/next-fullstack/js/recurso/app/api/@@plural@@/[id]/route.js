/**
 * API de @@titulo@@: /api/@@plural@@/3/  (ver, reemplazar, modificar y eliminar uno)
 *
 * La carpeta [id] hace que la dirección tenga una parte variable: Next.js la pasa en
 * params ({ id: '3' }).
 */
import { prisma } from '@/lib/db';
import { leerJson, NoEncontrado, responder, validar } from '@/lib/errores';
@@import_login@@
import { @@nombreCamel@@Actualizar, @@nombreCamel@@Crear, aJson } from '../esquema';

/** @typedef {{ params: Promise<{ id: string }> }} Contexto */

/**
 * Busca el registro por su id. Si no existe (o el id no es un número): 404.
 * @param {Contexto} contexto
 */
async function buscarO404({ params }) {
  const id = Number((await params).id);
  const @@nombreCamel@@ = Number.isInteger(id) ? await prisma.@@nombreCamel@@.findUnique({ where: { id } }) : null;
  if (!@@nombreCamel@@) throw new NoEncontrado();
  return @@nombreCamel@@;
}

// Obtener uno.
/** @param {Request} request @param {Contexto} contexto */
export async function GET(request, contexto) {
  return responder(async () => Response.json(aJson(await buscarO404(contexto))));
}

// Reemplazar (PUT): hay que enviar todos los campos.
/** @param {Request} request @param {Contexto} contexto */
export async function PUT(request, contexto) {
  @@pedir_sesion@@
  return responder(async () => {
    const { id } = await buscarO404(contexto);
    const datos = validar(@@nombreCamel@@Crear, await leerJson(request));
    return Response.json(aJson(await prisma.@@nombreCamel@@.update({ where: { id }, data: datos })));
  });
}

// Modificar (PATCH): solo los campos que se envían.
/** @param {Request} request @param {Contexto} contexto */
export async function PATCH(request, contexto) {
  @@pedir_sesion@@
  return responder(async () => {
    const { id } = await buscarO404(contexto);
    const datos = validar(@@nombreCamel@@Actualizar, await leerJson(request));
    return Response.json(aJson(await prisma.@@nombreCamel@@.update({ where: { id }, data: datos })));
  });
}

// Eliminar.
/** @param {Request} request @param {Contexto} contexto */
export async function DELETE(request, contexto) {
  @@pedir_sesion@@
  return responder(async () => {
    const { id } = await buscarO404(contexto);
    await prisma.@@nombreCamel@@.delete({ where: { id } });
    return new Response(null, { status: 204 });
  });
}
