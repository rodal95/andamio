'use client';

import { useSyncExternalStore } from 'react';
import { authService, type Credenciales, type DatosRegistro, type Usuario } from '@/services/authService';
import { @@importar_http@@ } from '@/services/http';

// guía: La sesión: quién ingresó, compartido por toda la app. Se guarda acá, fuera de los
// guía: componentes; cada componente que llama a useSesion() se vuelve a dibujar cuando cambia
// guía: (como con un Context, pero sin tener que envolver la app en un Provider).
// guía: Es del navegador ('use client'): el token está en localStorage, que el servidor no tiene.

interface Estado {
  usuario: Usuario | null;
  // guía: true mientras se averigua, al abrir la app, si el token guardado sigue sirviendo.
  cargando: boolean;
}

// guía: Lo que ve el servidor cuando arma el HTML de la página: todavía no sabe si alguien
// guía: ingresó (eso se averigua en el navegador).
const EN_EL_SERVIDOR: Estado = { usuario: null, cargando: true };

let estado: Estado = { usuario: null, cargando: leerToken() !== null };
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

// guía: Al abrir la app: si hay un token guardado, se pregunta a la API de quién es.
if (estado.cargando) {
  authService
    .yo()
    .then((usuario) => cambiar({ usuario, cargando: false }))
    .catch(() => {
      authService.salir(); // venció o no es válido
      cambiar({ usuario: null, cargando: false });
    });
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

export function salir(): void {
  authService.salir();
  cambiar({ usuario: null, cargando: false });
}

/**
 * A dónde volver después de ingresar (?desde=): solo una dirección de esta app. Si no,
 * alguien podría mandar un enlace a /ingresar?desde=https://sitio-falso.com y, después de
 * ingresar, la persona terminaría en otro sitio (redirección abierta).
 */
export function aDondeVolver(desde: unknown): string {
  // Empieza con una sola / (//sitio.com y /\sitio.com son de otro sitio).
  return typeof desde === 'string' && /^\/(?![/\\])/.test(desde) ? desde : '/';
}
