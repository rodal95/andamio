/**
 * Funciones para hablar con la API (Django, FastAPI o Express, hecha con andamio).
 *
 * La dirección de la API sale de VITE_API_URL (archivo .env). Si cambiás el .env,
 * reiniciá "npm run dev" para que tome el valor nuevo.
 */

export const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api').replace(/\/+$/, '');

/** Error que devuelve la API (ej.: 400 con los errores de validación de cada campo). */
export class ErrorApi extends Error {
  /**
   * @param {number} estado código HTTP (400, 404, 500...)
   * @param {unknown} detalle lo que respondió la API
   */
  constructor(estado, detalle) {
    // Si la API explica el error (detail), ese es el mensaje: "Las credenciales... no se proveyeron."
    const explicacion = detalle && typeof detalle === 'object' && 'detail' in detalle ? String(detalle.detail) : '';
    super(explicacion || `La API respondió con el error ${estado}`);
    this.estado = estado;
    this.detalle = detalle;
  }
}

// --- Login con JWT (API de Django con: python -m andamio nuevo login) -------------------
// Si guardás el token de acceso, cada pedido lo manda solo: Authorization: Bearer <token>.
// Así funcionan los recursos generados con --protegido (crear, modificar y eliminar).

const CLAVE_TOKEN = 'token';

/**
 * Guarda el token "access" que devuelve POST /api/token/.
 * @param {string} token
 */
export function guardarToken(token) {
  localStorage.setItem(CLAVE_TOKEN, token);
}

/** Cierra la sesión: los pedidos dejan de mandar el token. */
export function borrarToken() {
  localStorage.removeItem(CLAVE_TOKEN);
}

/**
 * El token guardado, o null si no hay sesión.
 * @returns {string | null}
 */
export function leerToken() {
  // Fuera del navegador (por ejemplo, en el servidor de Next.js) no hay localStorage.
  return typeof localStorage === 'undefined' ? null : localStorage.getItem(CLAVE_TOKEN);
}

/**
 * @param {unknown} datos
 * @returns {Record<string, string>}
 */
function encabezados(datos) {
  /** @type {Record<string, string>} */
  const resultado = {};
  if (datos !== undefined) resultado['Content-Type'] = 'application/json';
  const token = leerToken();
  if (token) resultado.Authorization = `Bearer ${token}`;
  return resultado;
}

/**
 * @param {string} metodo GET, POST, PUT, PATCH o DELETE
 * @param {string} ruta por ejemplo '/productos/'
 * @param {unknown} [datos] lo que se envía como JSON
 */
async function pedir(metodo, ruta, datos) {
  const respuesta = await fetch(`${API_URL}${ruta}`, {
    method: metodo,
    headers: encabezados(datos),
    body: datos === undefined ? undefined : JSON.stringify(datos),
  });
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => null);
    throw new ErrorApi(respuesta.status, detalle);
  }
  // DELETE responde 204: sin contenido.
  if (respuesta.status === 204) {
    return undefined;
  }
  return respuesta.json();
}

export const http = {
  /** @param {string} ruta */
  get: (ruta) => pedir('GET', ruta),
  /** @param {string} ruta @param {unknown} datos */
  post: (ruta, datos) => pedir('POST', ruta, datos),
  /** @param {string} ruta @param {unknown} datos */
  put: (ruta, datos) => pedir('PUT', ruta, datos),
  /** @param {string} ruta @param {unknown} datos */
  patch: (ruta, datos) => pedir('PATCH', ruta, datos),
  /** @param {string} ruta */
  delete: (ruta) => pedir('DELETE', ruta),
};
