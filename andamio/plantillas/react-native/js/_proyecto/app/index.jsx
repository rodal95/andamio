import { Stack } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { NOMBRE_APP } from '@/constants/app';

// Opciones de la barra superior. Se definen en una constante para no escribir
// objetos directamente dentro del JSX.
const opciones = { title: 'Inicio' };

export default function Inicio() {
  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      <Text style={styles.titulo}>{NOMBRE_APP}</Text>
      <Text>Editá app/index.tsx para empezar.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  contenedor: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  titulo: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
});
