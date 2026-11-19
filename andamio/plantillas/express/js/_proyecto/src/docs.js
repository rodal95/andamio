/**
 * Documentación interactiva (Swagger) en /docs, armada con los esquemas de cada
 * recurso. Funciona sin internet: swagger-ui-express trae todos sus archivos.
 */
import { z } from 'zod';

/**
 * Lo que cada recurso le cuenta a la documentación.
 * @typedef {object} DocsRecurso
 * @property {string} ruta      '/api/productos/'
 * @property {string} titulo    'Productos'
 * @property {import('zod').ZodObject} esquema   lo que se envía para crear
 */

/** @param {import('zod').ZodType} esquema */
function esquemaJson(esquema) {
  const { $schema, ...resto } = z.toJSONSchema(esquema, { io: 'input', unrepresentable: 'any' });
  return resto;
}

/**
 * @param {string} titulo
 * @param {DocsRecurso[]} recursos
 */
export function crearDocumentacion(titulo, recursos) {
  /** @type {Record<string, object>} */
  const paths = {};
  for (const { ruta, titulo: tag, esquema } of recursos) {
    const cuerpo = (parcial) => ({
      required: true,
      content: { 'application/json': { schema: esquemaJson(parcial ? esquema.partial() : esquema) } },
    });
    const id = { name: 'id', in: 'path', required: true, schema: { type: 'integer' } };
    const filtros = Object.keys(esquema.shape).map((campo) => ({ name: campo, in: 'query', schema: { type: 'string' } }));
    const respuestas = (codigo, texto) => ({
      [codigo]: { description: texto },
      400: { description: 'Datos inválidos: {"campo": ["mensaje"]}' },
      404: { description: 'No encontrado' },
    });
    paths[ruta] = {
      get: {
        tags: [tag],
        summary: 'Listar',
        parameters: [
          { name: 'search', in: 'query', description: 'Busca en los campos de texto', schema: { type: 'string' } },
          { name: 'ordering', in: 'query', description: 'Campo para ordenar (con - es de mayor a menor)', schema: { type: 'string' } },
          ...filtros,
        ],
        responses: { 200: { description: 'La lista (un array)' } },
      },
      post: { tags: [tag], summary: 'Crear', requestBody: cuerpo(false), responses: respuestas(201, 'Creado') },
    };
    paths[`${ruta}{id}/`] = {
      get: { tags: [tag], summary: 'Obtener', parameters: [id], responses: respuestas(200, 'El registro') },
      put: { tags: [tag], summary: 'Reemplazar', parameters: [id], requestBody: cuerpo(false), responses: respuestas(200, 'Modificado') },
      patch: { tags: [tag], summary: 'Actualizar', parameters: [id], requestBody: cuerpo(true), responses: respuestas(200, 'Modificado') },
      delete: { tags: [tag], summary: 'Eliminar', parameters: [id], responses: respuestas(204, 'Eliminado') },
    };
  }
  return { openapi: '3.1.0', info: { title: titulo, version: '0.1.0' }, paths };
}
