'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useSesion } from './sesion';

const RUTAS_DEL_LOGIN = ['/ingresar', '/registro'];

/**
 * Si nadie ingresó, lo que hay que mostrar en lugar de la página ("Cargando…") mientras lleva
 * a /ingresar (y después de ingresar, vuelve acá). Si alguien ingresó, null.
 * activo: false para no pedir nada (los hooks se llaman siempre, aunque no hagan falta).
 * @param {boolean} [activo]
 * @returns {import('react').ReactNode}
 */
export function usePedirIngreso(activo = true) {
  const { usuario, cargando } = useSesion();
  const router = useRouter();
  const ruta = usePathname();
  const falta = activo && !cargando && !usuario;
  useEffect(() => {
    if (falta) {
      // guía: Con los parámetros de la página (ej.: ?id=3), para volver a la misma.
      router.replace(`/ingresar?desde=${encodeURIComponent(ruta + window.location.search)}`);
    }
  }, [falta, ruta, router]);
  return !activo || usuario ? null : <p>Cargando…</p>;
}

/**
 * Muestra la página solo si alguien ingresó. La usa el layout de una carpeta con --protegido:
 * app/perfil/layout  ->  <RutaProtegida>{children}</RutaProtegida>
 *
 * Ojo: esto es para que se vea bien, no es seguridad. Lo que protege los datos es la API
 * (recurso --protegido): sin token responde 401, aunque alguien saltee esto.
 *
 * @param {{ children: import('react').ReactNode }} props
 */
export function RutaProtegida({ children }) {
  return usePedirIngreso() ?? children;
}

/**
 * Con nuevo login --obligatorio, en el Layout: toda la app pide ingresar. esDelLogin: es
 * /ingresar o /registro y nadie ingresó (se muestra sola, sin el menú ni el pie).
 * pedirIngreso: lo que hay que mostrar en lugar de la app, o null si alguien ingresó.
 * @returns {{ esDelLogin: boolean, pedirIngreso: import('react').ReactNode }}
 */
export function useLoginObligatorio() {
  const { usuario } = useSesion();
  // Sin la barra del final: con trailingSlash (Next.js full stack), la ruta es /ingresar/.
  const esDelLogin = RUTAS_DEL_LOGIN.includes(usePathname().replace(/(.)\/$/, '$1')) && !usuario;
  const pedirIngreso = usePedirIngreso(!esDelLogin);
  return { esDelLogin, pedirIngreso };
}
