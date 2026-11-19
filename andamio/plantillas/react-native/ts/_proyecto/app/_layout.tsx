import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

/**
 * Layout principal: todas las pantallas de app/ se muestran dentro de un Stack
 * (una pila de pantallas con botón para volver).
 */
export default function Layout() {
  return (
    <>
      <StatusBar style="auto" />
      <Stack />
    </>
  );
}
