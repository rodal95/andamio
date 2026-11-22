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
  readonly estado: number;
  readonly detalle: unknown;

  constructor(estado: number, detalle: unknown) {
    // Si la API explica el error (detail), ese es el mensaje: "No se encontró una cuenta...".
    const explicacion = typeof detalle === 'object' && detalle !== null && 'detail' in detalle ? String(detalle.detail) : '';
    super(explicacion || `La API respondió con el error ${estado}`);
    this.estado = estado;
    this.detalle = detalle;
  }
}

// --- Login (nuevo login): el token se guarda en memoria y va en cada pedido ---------------
let token: string | null = null;
let alVencer: (() => void) | null = null;

/** Desde acá, cada pedido manda este token (Authorization: Bearer ...); null: sin sesión. */
export function usarToken(nuevo: string | null): void {
  token = nuevo;
}

/** Qué hacer si la API responde 401 a un pedido que mandó el token (venció o no es válido). */
export function alVencerLaSesion(funcion: () => void): void {
  alVencer = funcion;
}

async function pedir<T>(metodo: string, ruta: string, datos?: unknown): Promise<T> {
  const encabezados: Record<string, string> = {};
  if (datos !== undefined) encabezados['Content-Type'] = 'application/json';
  if (token) encabezados.Authorization = `Bearer ${token}`;
  let respuesta: Response;
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
  if (respuesta.status === 401 && token) {
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
    return undefined as T;
  }
  return (await respuesta.json()) as T;
}

export const http = {
  get: <T>(ruta: string) => pedir<T>('GET', ruta),
  post: <T>(ruta: string, datos: unknown) => pedir<T>('POST', ruta, datos),
  put: <T>(ruta: string, datos: unknown) => pedir<T>('PUT', ruta, datos),
  patch: <T>(ruta: string, datos: unknown) => pedir<T>('PATCH', ruta, datos),
  delete: (ruta: string) => pedir<void>('DELETE', ruta),
};
