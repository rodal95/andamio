import type { ReactNode } from 'react';
import { type Href, Redirect, useLocalSearchParams, usePathname } from 'expo-router';
import { ActivityIndicator, StyleSheet } from 'react-native';
import { useSesion } from './sesion';

/**
 * Para una pantalla que pide ingresar (nuevo pantalla X --protegido): si nadie ingresó, lo que
 * hay que mostrar en su lugar ("cargando" mientras se averigua, o ir a /ingresar, y después
 * volver). Si alguien ingresó, null. Uso, al principio de la pantalla:
 *
 *   const pedirIngreso = usePedirIngreso();
 *   ...los demás hooks...
 *   if (pedirIngreso) return pedirIngreso;
 *
 * Ojo: esto es para que se vea bien, no es seguridad: lo que protege los datos es la API.
 */
export function usePedirIngreso(): ReactNode {
  const { usuario, cargando } = useSesion();
  const ruta = usePathname();
  // Los parámetros de la pantalla (ej.: el id de una para editar), para volver a la misma.
  const consulta = new URLSearchParams(useLocalSearchParams() as Record<string, string>).toString();
  const desde = consulta ? `${ruta}?${consulta}` : ruta;
  const aIngresar = { pathname: '/ingresar', params: { desde } } as Href;
  if (cargando) {
    return <ActivityIndicator style={estilos.cargando} />;
  }
  if (!usuario) {
    return <Redirect href={aIngresar} />;
  }
  return null;
}

const estilos = StyleSheet.create({
  cargando: {
    marginTop: 24,
  },
});
