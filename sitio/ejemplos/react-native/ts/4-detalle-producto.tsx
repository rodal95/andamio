import { Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { productoService, type Producto } from '@/services/productoService';

const opciones = { title: 'Detalle' };

/** Pantalla en la ruta /productos/detalle-producto: el id llega en la ruta (?id=3). */
export default function DetalleProductoPantalla() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [producto, setProducto] = useState<Producto | null>(null);

  // Cada vez que cambia el id, se pide ese producto a la API.
  useEffect(() => {
    productoService.obtener(Number(id)).then(setProducto);
  }, [id]);

  return (
    <View style={styles.contenedor}>
      <Stack.Screen options={opciones} />
      {producto ? (
        <>
          <Text style={styles.titulo}>{producto.nombre}</Text>
          <Text>
            $ {producto.precio} · {producto.stock} en stock
          </Text>
        </>
      ) : (
        <Text>Cargando…</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  contenedor: { flex: 1, padding: 16 },
  titulo: { fontSize: 20, fontWeight: 'bold' },
});
