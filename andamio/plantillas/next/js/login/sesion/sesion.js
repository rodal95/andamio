'use client';

import { useSyncExternalStore } from 'react';
import { authService } from '@/services/authService';
import { @@importar_http@@ } from '@/services/http';

/**
 * @typedef {import('@/services/authService').Usuario} Usuario
 * @typedef {import('@/services/authService').Credenciales} Credenciales
 * @typedef {import('@/services/authService').DatosRegistro} DatosRegistro
 */

// guía: La sesión: quién ingresó, compartido por toda la app. Se guarda acá, fuera de los
// guía: componentes; cada componente que llama a useSesion() se vuelve a dibujar cuando cambia
// guía: (como con un Context, pero sin tener que envolver la app en un Provider).
// guía: Es del navegador ('use client'): el token está en localStorage, que el servidor no tiene.

/**
 * @typedef {Object} Estado
 * @property {Usuario | null} usuario
 * @property {boolean} cargando true mientras se averigua, al abrir la app, si el token guardado sigue sirviendo
 */

// guía: Lo que ve el servidor cuando arma el HTML de la página: todavía no sabe si alguien
// guía: ingresó (eso se averigua en el navegador).
/** @type {Estado} */
const EN_EL_SERVIDOR = { usuario: null, cargando: true };

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

export function salir() {
  authService.salir();
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
  // Empieza con una sola / (//sitio.com y /\sitio.com son de otro sitio) y no tiene
  // espacios, tabs ni saltos de línea: el navegador los borra y /<tab>/sitio.com
  // terminaría siendo //sitio.com.
  return typeof desde === 'string' && /^\/(?![/\\])[^\\\u0000-\u0020\u007f]*$/.test(desde) ? desde : '/';
}
