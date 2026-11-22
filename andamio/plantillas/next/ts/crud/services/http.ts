/**
 * Funciones para hablar con la API.
 *
 * La dirección de la API sale de NEXT_PUBLIC_API_URL (archivo .env); si no está, se usa
 * @@api_por_defecto@@. Si cambiás el .env, reiniciá "npm run dev".
 */

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? '@@api_por_defecto@@').replace(/\/+$/, '');

/** Error que devuelve la API (ej.: 400 con los errores de validación de cada campo). */
export class ErrorApi extends Error {
  readonly estado: number;
  readonly detalle: unknown;

  constructor(estado: number, detalle: unknown) {
    // Si la API explica el error (detail), ese es el mensaje: "Las credenciales... no se proveyeron."
    const explicacion = typeof detalle === 'object' && detalle !== null && 'detail' in detalle ? String(detalle.detail) : '';
    super(explicacion || `La API respondió con el error ${estado}`);
    this.estado = estado;
    this.detalle = detalle;
  }
}

// --- Login con JWT (API de Django con: python -m andamio nuevo login) -------------------
// Si guardás el token de acceso, cada pedido lo manda solo: Authorization: Bearer <token>.
// Así funcionan los recursos generados con --protegido (crear, modificar y eliminar).

const CLAVE_TOKEN = 'token';

/** Guarda el token "access" que devuelve POST /api/token/. */
export function guardarToken(token: string): void {
  localStorage.setItem(CLAVE_TOKEN, token);
}

/** Cierra la sesión: los pedidos dejan de mandar el token. */
export function borrarToken(): void {
  localStorage.removeItem(CLAVE_TOKEN);
}

/** El token guardado, o null si no hay sesión. */
export function leerToken(): string | null {
  // Fuera del navegador (por ejemplo, en el servidor de Next.js) no hay localStorage.
  return typeof localStorage === 'undefined' ? null : localStorage.getItem(CLAVE_TOKEN);
}

function encabezados(datos: unknown): Record<string, string> {
  const resultado: Record<string, string> = {};
  if (datos !== undefined) resultado['Content-Type'] = 'application/json';
  const token = leerToken();
  if (token) resultado.Authorization = `Bearer ${token}`;
  return resultado;
}

async function pedir<T>(metodo: string, ruta: string, datos?: unknown): Promise<T> {
  let respuesta: Response;
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
