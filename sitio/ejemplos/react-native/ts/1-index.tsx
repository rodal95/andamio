import { Stack } from 'expo-router';
import { useEffect, useState } from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';

import { productoService, type Producto } from '@/services/productoService';

const opciones = { title: 'Productos' };

export default function Inicio() {
  // El estado de la pantalla: la lista de productos y, si falla, el error.
  const [productos, setProductos] = useState<Producto[]>([]);
  const [error, setError] = useState('');

  // Al abrir la pantalla, se piden los productos a la API (una sola vez: por eso el []).
  useEffect(() => {
    productoService
      .listar()
      .then(setProductos)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      {/* En React Native el texto va siempre dentro de <Text>: por eso "? :" y no "&&". */}
      {error ? <Text style={styles.error}>No se pudo cargar: {error}</Text> : null}
      <FlatList
        data={productos}
        keyExtractor={(producto) => String(producto.id)}
        renderItem={({ item }) => (
          <Text style={styles.fila}>
            {item.nombre}: $ {item.precio}
          </Text>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  contenedor: { flex: 1, padding: 16 },
  fila: { paddingVertical: 8 },
  error: { color: '#b42318' },
});
