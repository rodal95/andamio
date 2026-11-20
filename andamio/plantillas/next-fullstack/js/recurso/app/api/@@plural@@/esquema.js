// guía: Qué datos acepta la API (con Zod) y cómo se ve cada registro en el JSON.
// guía: Lo usan las rutas del recurso; si un dato no sirve, la API responde 400 con el motivo.
/**
 * @@titulo@@: qué datos acepta la API (validación) y cómo se ve cada registro en el JSON.
 */
import { z } from 'zod';
import { @@import_fechas@@ } from '@/lib/fechas';
import { @@import_validacion@@ } from '@/lib/validacion';

// Los campos que se cargan desde la API, con su validación.
const campos = {
  @@campos_zod@@
};

/** Lo que hay que enviar para crear (POST) o reemplazar (PUT). */
export const @@nombreCamel@@Crear = @@esquema_crear@@;

/** Lo que se puede enviar para modificar (PATCH): solo los campos que cambian. */
export const @@nombreCamel@@Actualizar = z.object(campos).partial();

// TODO(logica): validaciones propias, además del tipo. Ejemplo con un precio, en `campos`:
//   precio: decimal().refine((valor) => valor > 0, 'El precio tiene que ser mayor que cero.'),

/** Parámetros de la lista: ?search=, ?ordering= y ?campo=valor (filtra por igualdad). */
export const @@nombreCamel@@Filtros = z.object({
  search: z.string().optional(),
  ordering: z.string().optional(),
  @@filtros_zod@@
});

/** Campos por los que se puede ordenar con ?ordering= */
export const CAMPOS_ORDEN = [@@campos_orden@@];

/**
 * Cómo se ve un registro en el JSON de la API (igual que en Django).
 * @param {import('@/generated/prisma/client').@@Nombre@@} @@nombreCamel@@
 */
export function aJson(@@nombreCamel@@) {
  return {
    id: @@nombreCamel@@.id,
    @@campos_json@@
    creado: jsonFechaHora(@@nombreCamel@@.creado),
    actualizado: jsonFechaHora(@@nombreCamel@@.actualizado),
  };
}
