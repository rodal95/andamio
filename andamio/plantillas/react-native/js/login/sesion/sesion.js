import { useSyncExternalStore } from 'react';
import { authService } from '../services/authService';
import { alVencerLaSesion, usarToken } from '../services/http';
import { guardarToken, leerTokenGuardado } from './almacen';

// guía: La sesión: quién ingresó, compartido por toda la app. Cada componente que llama a
// guía: useSesion() se vuelve a dibujar cuando cambia (como con un Context, sin Provider).

/**
 * @typedef {import('../services/authService').Usuario} Usuario
 * @typedef {import('../services/authService').Credenciales} Credenciales
 * @typedef {import('../services/authService').DatosRegistro} DatosRegistro
 * @typedef {Object} Estado
 * @property {Usuario | null} usuario
 * @property {boolean} cargando true mientras se averigua, al abrir la app, si el token guardado sigue sirviendo
 */

/** @type {Estado} */
let estado = { usuario: null, cargando: true };
/** @type {Set<() => void>} */
const avisos = new Set();

/** @param {Estado} nuevo */
function cambiar(nuevo) {
  estado = nuevo;
  avisos.forEach((avisar) => avisar());
}

/** @param {() => void} avisar */
function suscribirse(avisar) {
  avisos.add(avisar);
  return () => {
    avisos.delete(avisar);
  };
}

// guía: Al abrir la app: si hay un token guardado, se pregunta a la API de quién es.
async function verificar() {
  const token = await leerTokenGuardado();
  if (!token) {
    cambiar({ usuario: null, cargando: false });
    return;
  }
  usarToken(token);
  try {
    cambiar({ usuario: await authService.yo(), cargando: false });
  } catch (error) {
    // Se borra si venció o no es válido (401). Si la API no responde o falla, el token se guarda: sirve cuando vuelva.
    if (error?.estado === 401) await salir();
    else cambiar({ usuario: null, cargando: false });
  }
}
void verificar();

// guía: Si la API responde 401 a un pedido con el token (venció), se cierra la sesión.
alVencerLaSesion(() => {
  void salir();
});

/**
 * El usuario que ingresó (null si nadie) y si todavía se está averiguando.
 * @returns {Estado}
 */
export function useSesion() {
  return useSyncExternalStore(suscribirse, () => estado);
}

/** @param {Credenciales} credenciales */
export async function ingresar(credenciales) {
  usarToken(null); // si quedó uno viejo, la API lo rechazaría
  const { access } = await authService.pedirTokens(credenciales);
  usarToken(access);
  await guardarToken(access);
  cambiar({ usuario: await authService.yo(), cargando: false });
}

/**
 * Crea el usuario y entra con esos mismos datos.
 * @param {DatosRegistro} datos
 */
export async function registrarse(datos) {
  usarToken(null);
  await authService.registrarse(datos);
  await ingresar({ username: datos.username, password: datos.password });
}

export async function salir() {
  usarToken(null);
  await guardarToken(null);
  cambiar({ usuario: null, cargando: false });
}

/**
 * A dónde volver después de ingresar (?desde=): solo una pantalla de esta app. Si no,
 * alguien podría mandar un enlace a /ingresar?desde=https://sitio-falso.com y, después de
 * ingresar, la persona terminaría en otro sitio (redirección abierta).
 * @param {unknown} desde
 * @returns {string}
 */
export function aDondeVolver(desde) {
  // Empieza con una sola / (//sitio.com y /\sitio.com son de otro sitio) y no tiene
  // espacios, tabs ni saltos de línea: el navegador los borra y /<tab>/sitio.com
  // terminaría siendo //sitio.com.
  return typeof desde === 'string' && /^\/(?![/\\])[^\\\u0000-\u0020\u007f]*$/.test(desde) ? desde : '/';
}
