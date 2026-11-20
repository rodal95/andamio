// guía: La API de la lista: GET lista y POST crea. Ver, modificar y eliminar uno están en [id]/route.
// guía: Valida con esquema y guarda con Prisma.
/**
 * API de @@titulo@@: /api/@@plural@@/  (listar y crear)
 *
 * Cada función se llama como el método HTTP que atiende (GET, POST...). La lista acepta
 * estos parámetros (igual que la API de Django):
 *     ?search=texto       busca en los campos de texto
 *     ?ordering=-creado   ordena por un campo (con "-" es de mayor a menor)
 *     ?campo=valor        filtra por igualdad
 */
import { prisma } from '@/lib/db';
import { leerJson, responder, validar } from '@/lib/errores';
import { @@nombreCamel@@Crear, @@nombreCamel@@Filtros, aJson, CAMPOS_ORDEN } from './esquema';

// Listar, con búsqueda, orden y filtros opcionales.
/** @param {Request} request */
export async function GET(request) {
  return responder(async () => {
    const parametros = Object.fromEntries(new URL(request.url).searchParams);
    const { search, ordering, ...filtros } = validar(@@nombreCamel@@Filtros, parametros);
    const campo = CAMPOS_ORDEN.find((nombre) => nombre === ordering?.replace(/^-/, '')) ?? 'id';
    const criterioDeOrden = { [campo]: ordering?.startsWith('-') ? 'desc' : 'asc' };
    const @@pluralCamel@@ = await prisma.@@nombreCamel@@.findMany({
      where: {
        ...filtros,
        @@busqueda@@
      },
      orderBy: criterioDeOrden,
    });
    return Response.json(@@pluralCamel@@.map(aJson));
  });
}

// Crear.
/** @param {Request} request */
export async function POST(request) {
  return responder(async () => {
    const datos = validar(@@nombreCamel@@Crear, await leerJson(request));
    // TODO(logica): reglas antes de guardar (ej.: que no se repita un nombre, completar un campo).
    const @@nombreCamel@@ = await prisma.@@nombreCamel@@.create({ data: datos });
    return Response.json(aJson(@@nombreCamel@@), { status: 201 });
  });
}
