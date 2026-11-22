'use client';

import { useSyncExternalStore } from 'react';
import { authService, type Credenciales, type DatosRegistro, type Usuario } from '@/services/authService';
@@importar_http@@

// guía: La sesión: quién ingresó, compartido por toda la app. Se guarda acá, fuera de los
// guía: componentes; cada componente que llama a useSesion() se vuelve a dibujar cuando cambia
// guía: (como con un Context, pero sin tener que envolver la app en un Provider).
// guía: El token está en una cookie httpOnly: esto solo sabe quién ingresó (se lo pregunta a la API).

interface Estado {
  usuario: Usuario | null;
  // guía: true mientras se averigua, al abrir la página, si hay una sesión.
  cargando: boolean;
}

// guía: Lo que ve el servidor cuando arma el HTML de la página: todavía no sabe si alguien
// guía: ingresó (eso se averigua en el navegador).
const EN_EL_SERVIDOR: Estado = { usuario: null, cargando: true };

let estado: Estado = EN_EL_SERVIDOR;
const avisos = new Set<() => void>();

function cambiar(nuevo: Estado) {
  estado = nuevo;
  avisos.forEach((avisar) => avisar());
}

function suscribirse(avisar: () => void) {
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
/** El usuario que ingresó (null si nadie) y si todavía se está averiguando. */
export function useSesion(): Estado {
  return useSyncExternalStore(suscribirse, () => estado, () => EN_EL_SERVIDOR);
}

export async function ingresar(credenciales: Credenciales): Promise<void> {
  const usuario = await authService.ingresar(credenciales);
  cambiar({ usuario, cargando: false });
}

/** Crea el usuario y entra con esos mismos datos. */
export async function registrarse(datos: DatosRegistro): Promise<void> {
  await authService.registrarse(datos);
  await ingresar({ username: datos.username, password: datos.password });
}

export async function salir(): Promise<void> {
  await authService.salir().catch(() => undefined); // si falla, igual se olvida quién ingresó
  cambiar({ usuario: null, cargando: false });
}

/**
 * A dónde volver después de ingresar (?desde=): solo una dirección de esta app. Si no,
 * alguien podría mandar un enlace a /ingresar?desde=https://sitio-falso.com y, después de
 * ingresar, la persona terminaría en otro sitio (redirección abierta).
 */
export function aDondeVolver(desde: unknown): string {
  // Empieza con una sola / (//sitio.com y /\sitio.com son de otro sitio) y no tiene
  // espacios, tabs ni saltos de línea: el navegador los borra y /<tab>/sitio.com
  // terminaría siendo //sitio.com.
  return typeof desde === 'string' && /^\/(?![/\\])[^\\\u0000-\u0020\u007f]*$/.test(desde) ? desde : '/';
}
