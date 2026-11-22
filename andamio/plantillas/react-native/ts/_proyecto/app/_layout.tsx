import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
// andamio:imports

// Opciones de la barra de arriba de todas las pantallas (cada pantalla puede cambiarlas
// con <Stack.Screen options={...} />). nuevo login agrega acá el botón Ingresar / Salir.
const opciones = {
  // andamio:opciones
};

/**
 * Layout principal: todas las pantallas de app/ se muestran dentro de un Stack
 * (una pila de pantallas con botón para volver).
 */
export default function Layout() {
  return (
    <>
      <StatusBar style="auto" />
      <Stack screenOptions={opciones} />
    </>
  );
}
