/**
 * Funciones para hablar con la API (Django, FastAPI o Express, hecha con andamio).
 *
 * La dirección de la API sale de EXPO_PUBLIC_API_URL (archivo .env).
 * Ojo con "localhost": en el celular o el emulador, localhost es el propio
 * dispositivo, no tu PC. Por eso:
 *   - Emulador de Android:    http://10.0.2.2:8000/api   (10.0.2.2 = tu PC)
 *   - Navegador o iOS:        http://localhost:8000/api
 *   - Celular real con Expo Go: http://IP-DE-TU-PC:8000/api  (ej: 192.168.0.10)
 *     y la API tiene que escuchar en la red:
 *       Django:  python manage.py runserver 0.0.0.0:8000  (y agregá esa IP a ALLOWED_HOSTS en su .env)
 *       FastAPI: python -m uvicorn app.main:app --reload --host 0.0.0.0
 *       Express: ya escucha en la red (npm run dev)
 * Si cambiás el .env, reiniciá "npx expo start".
 */

export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000/api').replace(/\/+$/, '');

/** Error que devuelve la API (ej.: 400 con los errores de validación de cada campo). */
export class ErrorApi extends Error {
  /**
   * @param {number} estado código HTTP (400, 404, 500...)
   * @param {unknown} detalle lo que respondió la API
   */
  constructor(estado, detalle) {
    // Si la API explica el error (detail), ese es el mensaje: "No se encontró una cuenta...".
    const explicacion = typeof detalle === 'object' && detalle !== null && 'detail' in detalle ? String(detalle.detail) : '';
    super(explicacion || `La API respondió con el error ${estado}`);
    this.estado = estado;
    this.detalle = detalle;
  }
}

// --- Login (nuevo login): el token se guarda en memoria y va en cada pedido ---------------
/** @type {string | null} */
let token = null;
/** @type {(() => void) | null} */
let alVencer = null;

/**
 * Desde acá, cada pedido manda este token (Authorization: Bearer ...); null: sin sesión.
 * @param {string | null} nuevo
 */
export function usarToken(nuevo) {
  token = nuevo;
}

/**
 * Qué hacer si la API responde 401 a un pedido que mandó el token (venció o no es válido).
 * @param {() => void} funcion
 */
export function alVencerLaSesion(funcion) {
  alVencer = funcion;
}

/**
 * @param {string} metodo GET, POST, PUT, PATCH o DELETE
 * @param {string} ruta por ejemplo '/productos/'
 * @param {unknown} [datos] lo que se envía como JSON
 */
async function pedir(metodo, ruta, datos) {
  /** @type {Record<string, string>} */
  const encabezados = {};
  if (datos !== undefined) encabezados['Content-Type'] = 'application/json';
  const enviado = token; // el token con el que sale el pedido
  if (enviado) encabezados.Authorization = `Bearer ${enviado}`;
  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      method: metodo,
      headers: encabezados,
      body: datos === undefined ? undefined : JSON.stringify(datos),
    });
  } catch {
    // Sin respuesta: la API no está en marcha, la dirección está mal o no hay conexión.
    throw new ErrorApi(0, { detail: `No se pudo conectar con la API (${API_URL}). ¿Está en marcha?` });
  }
  if (respuesta.status === 401 && enviado && enviado === token) {
    // Solo si es el mismo token con el que salió el pedido: si mientras tanto se volvió a
    // ingresar, el token nuevo no se toca.
    // El token venció (dura 60 minutos) o no es válido: se deja de usar y se avisa.
    token = null;
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
