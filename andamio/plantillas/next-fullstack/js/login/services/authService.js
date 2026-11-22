import { http } from './http';

// guía: El login de la API de este proyecto (app/api/):
// guía:   POST /api/token/     {"username", "password"}  ->  deja la cookie de la sesión
// guía:   POST /api/registro/  crea un usuario: {"username", "email", "password"}
// guía:   GET  /api/yo/        el usuario de la sesión
// guía:   POST /api/salir/     borra la cookie
// guía: El token no se guarda acá: queda en una cookie httpOnly que el navegador manda sola.

/**
 * Un usuario, como lo devuelve la API (nunca trae la contraseña).
 * @typedef {Object} Usuario
 * @property {number} id
 * @property {string} username
 * @property {string} email
 * @property {string} first_name
 * @property {string} last_name
 */

/**
 * Lo que pide el ingreso.
 * @typedef {Object} Credenciales
 * @property {string} username
 * @property {string} password
 */

/**
 * Lo que pide el registro.
 * @typedef {Credenciales & { email: string }} DatosRegistro
 */

export const authService = {
  /**
   * Ingresa (la API deja la cookie de la sesión) y devuelve el usuario.
   * @param {Credenciales} credenciales
   * @returns {Promise<Usuario>}
   */
  async ingresar(credenciales) {
    await http.post('/token/', credenciales);
    return http.get('/yo/');
  },
  /**
   * Crea el usuario (no ingresa: para eso, ingresar).
   * @param {DatosRegistro} datos
   * @returns {Promise<Usuario>}
   */
  registrarse: (datos) => http.post('/registro/', datos),
  /**
   * El usuario de la sesión. Sin sesión (o si venció), la API responde 401.
   * @returns {Promise<Usuario>}
   */
  yo: () => http.get('/yo/'),
  /** Sale: la API borra la cookie (la página no puede: es httpOnly). */
  salir: () => http.post('/salir/', {}),
};
