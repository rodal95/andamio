/**
 * Funciones para hablar con la API.
 *
 * La dirección de la API sale de NEXT_PUBLIC_API_URL (archivo .env); si no está, se usa
 * @@api_por_defecto@@. Si cambiás el .env, reiniciá "npm run dev".
 */

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? '@@api_por_defecto@@').replace(/\/+$/, '');

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

// --- Login con JWT (la API con: python -m andamio nuevo login) -------------------------
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

/** @type {(() => void) | null} */
let alVencer = null;

/**
 * Qué hacer si la API responde 401 (sin sesión, o el token venció o no es válido).
 * Lo usa la sesión del login (sesion/): la cierra y vuelve a pedir el ingreso.
 * @param {() => void} funcion
 */
export function alVencerLaSesion(funcion) {
  alVencer = funcion;
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
  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      method: metodo,
      headers: encabezados(datos),
      body: datos === undefined ? undefined : JSON.stringify(datos),
    });
  } catch {
    // Sin respuesta: la API no está en marcha, la dirección está mal o no hay conexión.
    throw new ErrorApi(0, { detail: `No se pudo conectar con la API (${API_URL}). ¿Está en marcha?` });
  }
  if (respuesta.status === 401) {
    // Sin sesión, o venció (el token dura 60 minutos): se borra el token y se avisa a la sesión.
    borrarToken();
    alVencer?.();
  }
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
