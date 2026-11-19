import { Stack } from 'expo-router';
import { useEffect, useState } from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';

import { Tarjeta } from '@/components';
import { productoService } from '@/services/productoService';

const opciones = { title: 'Productos' };

export default function Inicio() {
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    productoService
      .listar()
      .then(setProductos)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      {error ? <Text style={styles.error}>No se pudo cargar: {error}</Text> : null}
      <FlatList
        data={productos}
        keyExtractor={(producto) => String(producto.id)}
        // Cada producto se muestra con el componente Tarjeta: lo de adentro es su children.
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
