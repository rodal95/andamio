import { Link, Stack } from 'expo-router';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { Tarjeta } from '@/components';
import { useProductos } from '@/hooks/useProductos';

const opciones = { title: 'Productos' };

export default function Inicio() {
  const { productos, cargando, error } = useProductos();

  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      {cargando ? <ActivityIndicator /> : null}
      {error ? <Text style={styles.error}>No se pudo cargar: {error}</Text> : null}
      <FlatList
        data={productos}
        keyExtractor={(producto) => String(producto.id)}
        // Al tocar una tarjeta se abre la pantalla de detalle, con el id en la ruta.
        renderItem={({ item }) => (
          <Link href={{ pathname: '/productos/detalle-producto', params: { id: item.id } }} asChild>
            <Pressable>
              <Tarjeta>
                <Text style={styles.nombre}>{item.nombre}</Text>
                <Text>
                  $ {item.precio} · {item.stock} en stock
                </Text>
              </Tarjeta>
            </Pressable>
          </Link>
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
