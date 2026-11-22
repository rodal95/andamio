import { RutaProtegida } from '@/sesion';

/**
 * La página pide ingresar (--protegido): este layout de la carpeta la envuelve (a ella y a las
 * páginas que estén adentro) con RutaProtegida, que sin sesión lleva a /ingresar.
 * @param {{ children: import('react').ReactNode }} props
 */
export default function @@Nombre@@Layout({ children }) {
  return <RutaProtegida>{children}</RutaProtegida>;
}
