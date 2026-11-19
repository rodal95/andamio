/**
 * @@titulo@@: qué datos acepta la API (validación) y cómo se ve cada registro en el JSON.
 */
import { z } from 'zod';
import { @@import_fechas@@ } from '@/lib/fechas';
import type { @@Nombre@@ } from '@/generated/prisma/client';
import { @@import_validacion@@ } from '@/lib/validacion';

// Los campos que se cargan desde la API, con su validación.
const campos = {
  @@campos_zod@@
};

/** Lo que hay que enviar para crear (POST) o reemplazar (PUT). */
export const @@nombreCamel@@Crear = @@esquema_crear@@;

/** Lo que se puede enviar para modificar (PATCH): solo los campos que cambian. */
export const @@nombreCamel@@Actualizar = z.object(campos).partial();

/** Parámetros de la lista: ?search=, ?ordering= y ?campo=valor (filtra por igualdad). */
export const @@nombreCamel@@Filtros = z.object({
  search: z.string().optional(),
  ordering: z.string().optional(),
  @@filtros_zod@@
});

/** Campos por los que se puede ordenar con ?ordering= */
export const CAMPOS_ORDEN = [@@campos_orden@@] as const;

/** Cómo se ve un registro en el JSON de la API (igual que en Django). */
export function aJson(@@nombreCamel@@: @@Nombre@@) {
  return {
    id: @@nombreCamel@@.id,
    @@campos_json@@
    creado: jsonFechaHora(@@nombreCamel@@.creado),
    actualizado: jsonFechaHora(@@nombreCamel@@.actualizado),
  };
}
