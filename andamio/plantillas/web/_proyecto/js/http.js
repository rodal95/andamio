// Funciones para hablar con la API. Los servicios (js/servicios/) las usan.
import { API_URL } from './config.js';

/** Error de la API. `errores` tiene los mensajes por campo: { precio: ['Este campo es requerido.'] } */
export class ErrorApi extends Error {
  constructor(estado, datos) {
    const errores = datos && typeof datos === 'object' && !Array.isArray(datos) ? datos : {};
    super(errores.detail || `La API respondió con el error ${estado}`);
    this.estado = estado;
    this.errores = errores;
  }
}

/**
 * Hace un pedido a la API y devuelve la respuesta ya convertida desde JSON.
 * Si hay un token guardado (login con JWT), lo manda en el encabezado Authorization.
 * @param {string} ruta por ejemplo '/productos/'
 * @param {{ method?: string, body?: unknown }} [opciones]
 */
export async function pedir(ruta, opciones = {}) {
  const encabezados = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('token');
  if (token) encabezados.Authorization = `Bearer ${token}`;
  let respuesta;
  try {
    respuesta = await fetch(API_URL + ruta, {
      method: opciones.method || 'GET',
      headers: encabezados,
      body: opciones.body === undefined ? undefined : JSON.stringify(opciones.body),
    });
  } catch {
    throw new ErrorApi(0, { detail: `No se pudo conectar con la API (${API_URL}). ¿Está andando?` });
  }
  // El token venció (dura 60 minutos) o no es válido: se borra (la próxima página pide ingresar).
  // Solo si es el mismo token con el que salió el pedido (no uno de un ingreso más nuevo).
  if (respuesta.status === 401 && token && token === localStorage.getItem('token')) localStorage.removeItem('token');
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) throw new ErrorApi(respuesta.status, datos);
  return datos;
}
