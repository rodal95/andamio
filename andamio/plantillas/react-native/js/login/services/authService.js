import { http } from './http';

// guía: El login de la API (Django, FastAPI o Express con: python -m andamio nuevo login):
// guía:   POST /api/token/     {"username", "password"}  ->  {"access", "refresh"}
// guía:   POST /api/registro/  crea un usuario: {"username", "email", "password"}
// guía:   GET  /api/yo/        el usuario dueño del token

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
   * Pide los tokens con usuario y contraseña: access (va en cada pedido; dura 60 minutos) y refresh.
   * @param {Credenciales} credenciales
   * @returns {Promise<{ access: string, refresh: string }>}
   */
  pedirTokens: (credenciales) => http.post('/token/', credenciales),
  /**
   * Crea el usuario (no ingresa: para eso, pedirTokens).
   * @param {DatosRegistro} datos
   * @returns {Promise<Usuario>}
   */
  registrarse: (datos) => http.post('/registro/', datos),
  /**
   * El usuario del token que se está usando. Si venció, la API responde 401.
   * @returns {Promise<Usuario>}
   */
  yo: () => http.get('/yo/'),
};
