import { router } from 'expo-router';
import { Button } from 'react-native';
import { salir, useSesion } from '@/sesion';

/**
 * Ingresar, o Salir si alguien ingresó. nuevo login lo pone en la barra de arriba de todas
 * las pantallas: headerRight en las opciones del Stack de app/_layout.
 */
export function BotonSesion() {
  const { usuario, cargando } = useSesion();
  if (cargando) {
    return null;
  }
  if (!usuario) {
    return <Button title="Ingresar" onPress={() => router.push('/ingresar')} />;
  }
  return (
    <Button
      title={`Salir (${usuario.username})`}
      onPress={() => {
        void salir().then(() => router.replace('/'));
      }}
    />
  );
}
