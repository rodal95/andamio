import { reactive, readonly } from 'vue';
import { @@importar_http@@ } from '../services/http';
import { authService } from '../services/authService';

/**
 * @typedef {import('../services/authService').Usuario} Usuario
 * @typedef {import('../services/authService').Credenciales} Credenciales
 * @typedef {import('../services/authService').DatosRegistro} DatosRegistro
 */

// guía: La sesión: quién ingresó, compartido por toda la app. Es reactiva: los componentes que
// guía: la usan (sesion.usuario) se actualizan solos cuando cambia.

const estado = reactive({
  /** @type {Usuario | null} */
  usuario: null,
  // guía: true mientras se averigua, al abrir la app, si el token guardado sigue sirviendo.
  cargando: leerToken() !== null,
});

/** Para leer: sesion.usuario (null si nadie ingresó) y sesion.cargando. Se cambia con ingresar y salir. */
export const sesion = readonly(estado);

// guía: Al abrir la app: si hay un token guardado, se pregunta a la API de quién es.
const verificacion = estado.cargando
  ? authService
      .yo()
      .then((usuario) => {
        estado.usuario = usuario;
      })
      .catch((error) => {
        // Se borra si venció o no es válido (401). Si la API no responde o falla, el token se guarda: sirve cuando vuelva.
        if (error?.estado === 401) authService.salir();
      })
      .finally(() => {
        estado.cargando = false;
      })
  : Promise.resolve();

/** Se cumple cuando ya se sabe si hay sesión (lo espera el router antes de cada página). */
export function sesionLista() {
  return verificacion;
}

@@al_vencer@@
/** @param {Credenciales} credenciales */
export async function ingresar(credenciales) {
  estado.usuario = await authService.ingresar(credenciales);
}

/**
 * Crea el usuario y entra con esos mismos datos.
 * @param {DatosRegistro} datos
 */
export async function registrarse(datos) {
  await authService.registrarse(datos);
  await ingresar({ username: datos.username, password: datos.password });
}

export function salir() {
  authService.salir();
  estado.usuario = null;
}

/**
 * A dónde volver después de ingresar (?desde=): solo una dirección de esta app. Si no,
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
