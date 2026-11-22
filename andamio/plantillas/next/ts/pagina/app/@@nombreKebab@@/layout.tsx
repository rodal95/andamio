import type { ReactNode } from 'react';
import { RutaProtegida } from '@/sesion';

/**
 * La página pide ingresar (--protegido): este layout de la carpeta la envuelve (a ella y a las
 * páginas que estén adentro) con RutaProtegida, que sin sesión lleva a /ingresar.
 */
export default function @@Nombre@@Layout({ children }: Readonly<{ children: ReactNode }>) {
  return <RutaProtegida>{children}</RutaProtegida>;
}
