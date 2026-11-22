import { borrarToken, guardarToken, http } from './http';

// guía: El login de la API (Django con: python -m andamio nuevo login):
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
   * Pide el token, lo guarda (desde ahí cada pedido lo manda solo) y devuelve el usuario.
   * @param {Credenciales} credenciales
   * @returns {Promise<Usuario>}
   */
  async ingresar(credenciales) {
    borrarToken(); // si quedó uno viejo, la API lo rechazaría
    // access: el que se manda en cada pedido (dura 60 minutos); refresh: acá no se usa.
    /** @type {{ access: string, refresh: string }} */
    const tokens = await http.post('/token/', credenciales);
    guardarToken(tokens.access);
    return http.get('/yo/');
  },
  /**
   * Crea el usuario (no ingresa: para eso, ingresar).
   * @param {DatosRegistro} datos
   * @returns {Promise<Usuario>}
   */
  registrarse(datos) {
    borrarToken();
    return http.post('/registro/', datos);
  },
  /**
   * El usuario del token guardado. Si venció, la API responde 401.
   * @returns {Promise<Usuario>}
   */
  yo: () => http.get('/yo/'),
  /** Cierra la sesión: borra el token. */
  salir: () => borrarToken(),
};
