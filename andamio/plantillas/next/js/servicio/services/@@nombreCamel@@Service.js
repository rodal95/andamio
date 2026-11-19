import { http } from './http';

/**
 * @@nombreTitulo@@ tal como lo devuelve la API: /api/@@plural@@/
 * (Estos comentarios le dicen al editor qué campos tiene, para que los autocomplete.)
 *
 * @typedef {Object} @@Nombre@@
 * @property {number} id
 @@campos_jsdoc@@
 * @property {string} creado
 * @property {string} actualizado
 */

/**
 * Datos para crear o modificar: todo menos lo que completa el servidor.
 * @typedef {Omit<@@Nombre@@, 'id' | 'creado' | 'actualizado'>} @@Nombre@@Datos
 */

// Con barra al final: así son las rutas de las APIs que genera andamio.
const RUTA = '/@@plural@@/';

export const @@nombreCamel@@Service = {
  /** @returns {Promise<@@Nombre@@[]>} */
  listar: () => http.get(RUTA),
  /** @param {number} id @returns {Promise<@@Nombre@@>} */
  obtener: (id) => http.get(`${RUTA}${id}/`),
  /** @param {@@Nombre@@Datos} datos @returns {Promise<@@Nombre@@>} */
  crear: (datos) => http.post(RUTA, datos),
  /**
   * Modifica solo los campos que mandes.
   * @param {number} id
   * @param {Partial<@@Nombre@@Datos>} datos
   * @returns {Promise<@@Nombre@@>}
   */
  actualizar: (id, datos) => http.patch(`${RUTA}${id}/`, datos),
  /** @param {number} id */
  eliminar: (id) => http.delete(`${RUTA}${id}/`),
};
