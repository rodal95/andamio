import { Stack } from 'expo-router';
import { ActivityIndicator, FlatList, StyleSheet, Text, View } from 'react-native';

import { Tarjeta } from '@/components';
import { useProductos } from '@/hooks/useProductos';

const opciones = { title: 'Productos' };

export default function Inicio() {
  // Toda la lógica de pedir los datos quedó en el hook: la pantalla solo los muestra.
  const { productos, cargando, error } = useProductos();

  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      {cargando ? <ActivityIndicator /> : null}
      {error ? <Text style={styles.error}>No se pudo cargar: {error}</Text> : null}
      <FlatList
        data={productos}
        keyExtractor={(producto) => String(producto.id)}
        renderItem={({ item }) => (
          <Tarjeta>
            <Text style={styles.nombre}>{item.nombre}</Text>
            <Text>
              $ {item.precio} · {item.stock} en stock
            </Text>
          </Tarjeta>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  contenedor: { flex: 1, padding: 16 },
  nombre: { fontSize: 18, fontWeight: 'bold' },
  error: { color: '#b42318' },
});
