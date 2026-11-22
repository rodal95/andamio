import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router';
import { useSesion } from './sesion';

/**
 * Muestra la página solo si hay alguien que ingresó; si no, lleva a /ingresar (y después
 * de ingresar, vuelve acá). En App.tsx: <RutaProtegida><PerfilPage /></RutaProtegida>
 *
 * Ojo: esto es para que se vea bien, no es seguridad. Lo que protege los datos es la API
 * (recurso --protegido en Django): sin token responde 401, aunque alguien saltee esto.
 */
export function RutaProtegida({ children }: { children: ReactNode }) {
  const { usuario, cargando } = useSesion();
  const ubicacion = useLocation();
  if (cargando) {
    return <p>Cargando…</p>;
  }
  if (!usuario) {
    return <Navigate to="/ingresar" replace state={{ desde: ubicacion.pathname }} />;
  }
  return children;
}
