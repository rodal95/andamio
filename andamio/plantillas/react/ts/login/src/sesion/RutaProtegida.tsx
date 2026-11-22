import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router';
import { useSesion } from './sesion';

/**
 * Si nadie ingresó, lo que hay que mostrar en lugar de la página: "Cargando…" mientras se
 * averigua, o ir a /ingresar (y después de ingresar, volver acá). Si alguien ingresó, null.
 * La usan RutaProtegida y, con nuevo login --obligatorio, el Layout (toda la app).
 */
export function usePedirIngreso(): ReactNode {
  const { usuario, cargando } = useSesion();
  const ubicacion = useLocation();
  if (cargando) {
    return <p>Cargando…</p>;
  }
  if (!usuario) {
    return <Navigate to="/ingresar" replace state={{ desde: ubicacion.pathname }} />;
  }
  return null;
}

/**
 * Muestra la página solo si alguien ingresó. En App.tsx: <RutaProtegida><PerfilPage /></RutaProtegida>
 *
 * Ojo: esto es para que se vea bien, no es seguridad. Lo que protege los datos es la API
 * (recurso --protegido en Django): sin token responde 401, aunque alguien saltee esto.
 */
export function RutaProtegida({ children }: { children: ReactNode }) {
  return usePedirIngreso() ?? children;
}
