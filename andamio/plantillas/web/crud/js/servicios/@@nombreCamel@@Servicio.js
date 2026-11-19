// Funciones para usar el recurso /api/@@plural@@/ de la API (Django, FastAPI, Express o
// Next.js full stack). Generalo con los mismos campos que el recurso.
import { pedir } from '../http.js';

/**
 * @typedef {Object} @@Nombre@@
 * @property {number} id
 @@campos_jsdoc@@
 */

const RUTA = '/@@plural@@/';

export const @@nombreCamel@@Servicio = {
  /** @param {Record<string, string>} [filtros] ej.: { search: 'yerba', ordering: '-precio' } */
  listar: (filtros = {}) => pedir(RUTA + (Object.keys(filtros).length ? `?${new URLSearchParams(filtros)}` : '')),
  /** @param {number} id */
  obtener: (id) => pedir(`${RUTA}${id}/`),
  /** @param {Omit<@@Nombre@@, 'id'>} datos */
  crear: (datos) => pedir(RUTA, { method: 'POST', body: datos }),
  /** @param {number} id @param {Omit<@@Nombre@@, 'id'>} datos */
  actualizar: (id, datos) => pedir(`${RUTA}${id}/`, { method: 'PUT', body: datos }),
  /** @param {number} id */
  eliminar: (id) => pedir(`${RUTA}${id}/`, { method: 'DELETE' }),
};
