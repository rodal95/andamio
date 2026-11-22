import { useSyncExternalStore } from 'react';
import { authService, type Credenciales, type DatosRegistro, type Usuario } from '../services/authService';
import { alVencerLaSesion, usarToken } from '../services/http';
import { guardarToken, leerTokenGuardado } from './almacen';

// guía: La sesión: quién ingresó, compartido por toda la app. Cada componente que llama a
// guía: useSesion() se vuelve a dibujar cuando cambia (como con un Context, sin Provider).

interface Estado {
  usuario: Usuario | null;
  // guía: true mientras se averigua, al abrir la app, si el token guardado sigue sirviendo.
  cargando: boolean;
}

let estado: Estado = { usuario: null, cargando: true };
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
async function verificar() {
  const token = await leerTokenGuardado();
  if (!token) {
    cambiar({ usuario: null, cargando: false });
    return;
  }
  usarToken(token);
  try {
    cambiar({ usuario: await authService.yo(), cargando: false });
  } catch {
    await salir(); // venció o no es válido
  }
}
void verificar();

// guía: Si la API responde 401 a un pedido con el token (venció), se cierra la sesión.
alVencerLaSesion(() => {
  void salir();
});

/** El usuario que ingresó (null si nadie) y si todavía se está averiguando. */
export function useSesion(): Estado {
  return useSyncExternalStore(suscribirse, () => estado);
}

export async function ingresar(credenciales: Credenciales): Promise<void> {
  usarToken(null); // si quedó uno viejo, la API lo rechazaría
  const { access } = await authService.pedirTokens(credenciales);
  usarToken(access);
  await guardarToken(access);
  cambiar({ usuario: await authService.yo(), cargando: false });
}

/** Crea el usuario y entra con esos mismos datos. */
export async function registrarse(datos: DatosRegistro): Promise<void> {
  usarToken(null);
  await authService.registrarse(datos);
  await ingresar({ username: datos.username, password: datos.password });
}

export async function salir(): Promise<void> {
  usarToken(null);
  await guardarToken(null);
  cambiar({ usuario: null, cargando: false });
}

/**
 * A dónde volver después de ingresar (?desde=): solo una pantalla de esta app. Si no,
 * alguien podría mandar un enlace a /ingresar?desde=https://sitio-falso.com y, después de
 * ingresar, la persona terminaría en otro sitio (redirección abierta).
 */
export function aDondeVolver(desde: unknown): string {
  // Empieza con una sola / (//sitio.com y /\sitio.com son de otro sitio).
  return typeof desde === 'string' && /^\/(?![/\\])/.test(desde) ? desde : '/';
}
