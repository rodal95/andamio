import { useSyncExternalStore } from 'react';
import { @@importar_http@@ } from '../services/http';
import { authService } from '../services/authService';

/**
 * @typedef {import('../services/authService').Usuario} Usuario
 * @typedef {import('../services/authService').Credenciales} Credenciales
 * @typedef {import('../services/authService').DatosRegistro} DatosRegistro
 */

// guía: La sesión: quién ingresó, compartido por toda la app. Se guarda acá, fuera de los
// guía: componentes; cada componente que llama a useSesion() se vuelve a dibujar cuando cambia
// guía: (como con un Context, pero sin tener que envolver la app en un Provider).

/**
 * @typedef {Object} Estado
 * @property {Usuario | null} usuario
 * @property {boolean} cargando true mientras se averigua, al abrir la app, si el token guardado sigue sirviendo
 */

/** @type {Estado} */
let estado = { usuario: null, cargando: leerToken() !== null };
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
if (estado.cargando) {
  authService
    .yo()
    .then((usuario) => cambiar({ usuario, cargando: false }))
    .catch((error) => {
      // Se borra si venció o no es válido (401). Si la API no responde o falla, el token se guarda: sirve cuando vuelva.
      if (error?.estado === 401) authService.salir();
      cambiar({ usuario: null, cargando: false });
    });
}

@@al_vencer@@
/**
 * El usuario que ingresó (null si nadie) y si todavía se está averiguando.
 * @returns {Estado}
 */
export function useSesion() {
  return useSyncExternalStore(suscribirse, () => estado);
}

/** @param {Credenciales} credenciales */
export async function ingresar(credenciales) {
  const usuario = await authService.ingresar(credenciales);
  cambiar({ usuario, cargando: false });
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
  cambiar({ usuario: null, cargando: false });
}
