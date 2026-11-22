import { RutaProtegida } from '@/sesion';

/**
 * Editar pide ingresar (crud --protegido): sin sesión, RutaProtegida lleva a /ingresar.
 * @param {{ children: import('react').ReactNode }} props
 */
export default function Editar@@Nombre@@Layout({ children }) {
  return <RutaProtegida>{children}</RutaProtegida>;
}
