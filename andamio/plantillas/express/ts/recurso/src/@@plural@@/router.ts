// guía: La API: una ruta por operación (listar, crear, ver, reemplazar, modificar y eliminar).
// guía: Valida con esquema.ts y guarda con Prisma; src/app conecta el router en /api/@@plural@@.
/**
 * API de @@titulo@@: /api/@@plural@@/
 *
 * La lista acepta estos parámetros (igual que la API de Django):
 *     ?search=texto       busca en los campos de texto
 *     ?ordering=-creado   ordena por un campo (con "-" es de mayor a menor)
 *     ?campo=valor        filtra por igualdad
 */
import { Router } from 'express';
import { prisma } from '../db.ts';
import type { DocsRecurso } from '../docs.ts';
import { NoEncontrado, validar } from '../errores.ts';
@@import_login@@
import type { Prisma } from '../generated/prisma/client.ts';
import { @@nombreCamel@@Actualizar, @@nombreCamel@@Crear, @@nombreCamel@@Filtros, aJson, CAMPOS_ORDEN } from './esquema.ts';

export const @@pluralCamel@@Router = Router();

/** Busca el registro por su id. Si no existe (o el id no es un número): 404. */
async function buscarO404(texto: string) {
  const id = Number(texto);
  const @@nombreCamel@@ = Number.isInteger(id) ? await prisma.@@nombreCamel@@.findUnique({ where: { id } }) : null;
  if (!@@nombreCamel@@) throw new NoEncontrado();
  return @@nombreCamel@@;
}

// Listar, con búsqueda, orden y filtros opcionales.
@@pluralCamel@@Router.get('/', async (req, res) => {
  const { search, ordering, ...filtros } = validar(@@nombreCamel@@Filtros, req.query);
  const campo = CAMPOS_ORDEN.find((nombre) => nombre === ordering?.replace(/^-/, '')) ?? 'id';
  const criterioDeOrden = { [campo]: ordering?.startsWith('-') ? 'desc' : 'asc' } as Prisma.@@Nombre@@OrderByWithRelationInput;
  const @@pluralCamel@@ = await prisma.@@nombreCamel@@.findMany({
    where: {
      ...filtros,
      @@busqueda@@
    },
    orderBy: criterioDeOrden,
  });
  res.json(@@pluralCamel@@.map(aJson));
});

// Crear.
@@pluralCamel@@Router.post('/', @@pide_login@@async (req, res) => {
  // TODO(logica): reglas antes de guardar (ej.: que no se repita un nombre, completar un campo).
  const datos = validar(@@nombreCamel@@Crear, req.body);
  const @@nombreCamel@@ = await prisma.@@nombreCamel@@.create({ data: datos });
  res.status(201).json(aJson(@@nombreCamel@@));
});

// Obtener uno.
@@pluralCamel@@Router.get('/:id/', async (req, res) => {
  res.json(aJson(await buscarO404(req.params.id)));
});

// Reemplazar (PUT): hay que enviar todos los campos.
@@pluralCamel@@Router.put('/:id/', @@pide_login@@async (req, res) => {
  const { id } = await buscarO404(req.params.id);
  const datos = validar(@@nombreCamel@@Crear, req.body);
  res.json(aJson(await prisma.@@nombreCamel@@.update({ where: { id }, data: datos })));
});

// Modificar (PATCH): solo los campos que se envían.
@@pluralCamel@@Router.patch('/:id/', @@pide_login@@async (req, res) => {
  const { id } = await buscarO404(req.params.id);
  const datos = validar(@@nombreCamel@@Actualizar, req.body);
  res.json(aJson(await prisma.@@nombreCamel@@.update({ where: { id }, data: datos })));
});

// Eliminar.
@@pluralCamel@@Router.delete('/:id/', @@pide_login@@async (req, res) => {
  const { id } = await buscarO404(req.params.id);
  await prisma.@@nombreCamel@@.delete({ where: { id } });
  res.status(204).end();
});

// Para la documentación de /docs.
export const @@pluralCamel@@Docs: DocsRecurso = { ruta: '/api/@@plural@@/', titulo: '@@titulo@@', esquema: @@nombreCamel@@Crear };
