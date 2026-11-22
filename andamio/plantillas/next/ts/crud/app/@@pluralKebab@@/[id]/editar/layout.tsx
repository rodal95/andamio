import type { ReactNode } from 'react';
import { RutaProtegida } from '@/sesion';

/** Editar pide ingresar (crud --protegido): sin sesión, RutaProtegida lleva a /ingresar. */
export default function Editar@@Nombre@@Layout({ children }: Readonly<{ children: ReactNode }>) {
  return <RutaProtegida>{children}</RutaProtegida>;
}
