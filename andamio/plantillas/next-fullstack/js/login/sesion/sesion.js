'use client';

import { useSyncExternalStore } from 'react';
import { authService } from '@/services/authService';
@@importar_http@@

/**
 * @typedef {import('@/services/authService').Usuario} Usuario
 * @typedef {import('@/services/authService').Credenciales} Credenciales
 * @typedef {import('@/services/authService').DatosRegistro} DatosRegistro
 */

// guía: La sesión: quién ingresó, compartido por toda la app. Se guarda acá, fuera de los
// guía: componentes; cada componente que llama a useSesion() se vuelve a dibujar cuando cambia
// guía: (como con un Context, pero sin tener que envolver la app en un Provider).
// guía: El token está en una cookie httpOnly: esto solo sabe quién ingresó (se lo pregunta a la API).

/**
 * @typedef {Object} Estado
 * @property {Usuario | null} usuario
 * @property {boolean} cargando true mientras se averigua, al abrir la página, si hay una sesión
 */

// guía: Lo que ve el servidor cuando arma el HTML de la página: todavía no sabe si alguien
// guía: ingresó (eso se averigua en el navegador).
/** @type {Estado} */
const EN_EL_SERVIDOR = { usuario: null, cargando: true };

let estado = EN_EL_SERVIDOR;
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

// guía: Al abrir la página (en el navegador): se le pregunta a la API si hay una sesión.
if (typeof window !== 'undefined') {
  authService
    .yo()
    .then((usuario) => cambiar({ usuario, cargando: false }))
    .catch(() => cambiar({ usuario: null, cargando: false }));
}

@@al_vencer@@
/**
 * El usuario que ingresó (null si nadie) y si todavía se está averiguando.
 * @returns {Estado}
 */
export function useSesion() {
  return useSyncExternalStore(suscribirse, () => estado, () => EN_EL_SERVIDOR);
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

export async function salir() {
  await authService.salir().catch(() => undefined); // si falla, igual se olvida quién ingresó
  cambiar({ usuario: null, cargando: false });
}

/**
 * A dónde volver después de ingresar (?desde=): solo una dirección de esta app. Si no,
 * alguien podría mandar un enlace a /ingresar?desde=https://sitio-falso.com y, después de
 * ingresar, la persona terminaría en otro sitio (redirección abierta).
 * @param {unknown} desde
 * @returns {string}
 */
export function aDondeVolver(desde) {
  // Empieza con una sola / (//sitio.com y /\sitio.com son de otro sitio).
  return typeof desde === 'string' && /^\/(?![/\\])/.test(desde) ? desde : '/';
}
