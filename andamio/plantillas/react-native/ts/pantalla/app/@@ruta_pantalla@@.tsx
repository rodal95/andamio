import { @@expo_router@@ } from 'expo-router';
import { @@react_native@@ } from 'react-native';
@@datos_imports@@

// Opciones de la barra superior (título, colores, etc.).
const opciones = { title: '@@nombreTitulo@@' };

/** Pantalla en la ruta @@url_pantalla@@ */
export default function @@Nombre@@Pantalla() {
  @@datos_consulta@@
  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      <Text style={styles.titulo}>@@nombreTitulo@@</Text>
      @@datos_contenido@@
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
  @@datos_estilos@@
});
