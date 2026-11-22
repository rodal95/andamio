import { RutaProtegida } from '@/sesion';

/**
 * Agregar pide ingresar (crud --protegido): sin sesión, RutaProtegida lleva a /ingresar.
 * @param {{ children: import('react').ReactNode }} props
 */
export default function Nuevo@@Nombre@@Layout({ children }) {
  return <RutaProtegida>{children}</RutaProtegida>;
}
