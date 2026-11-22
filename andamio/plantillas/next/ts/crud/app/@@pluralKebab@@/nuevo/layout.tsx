import type { ReactNode } from 'react';
import { RutaProtegida } from '@/sesion';

/** Agregar pide ingresar (crud --protegido): sin sesión, RutaProtegida lleva a /ingresar. */
export default function Nuevo@@Nombre@@Layout({ children }: Readonly<{ children: ReactNode }>) {
  return <RutaProtegida>{children}</RutaProtegida>;
}
