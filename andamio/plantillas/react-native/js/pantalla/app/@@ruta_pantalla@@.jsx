import { Stack } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

// Opciones de la barra superior (título, colores, etc.).
const opciones = { title: '@@nombreTitulo@@' };

/** Pantalla en la ruta @@url_pantalla@@ */
export default function @@Nombre@@Pantalla() {
  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      <Text style={styles.titulo}>@@nombreTitulo@@</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  contenedor: {
    flex: 1,
    padding: 16,
  },
  titulo: {
    fontSize: 20,
    fontWeight: 'bold',
  },
});
