import { useEffect, useState } from 'react';
import { Link, Stack } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text } from 'react-native';

import { Tarjeta } from '@/components';
import { productoService, type Producto } from '@/services/productoService';

const opciones = { title: 'Productos' };

export default function Inicio() {
  const [productos, setProductos] = useState<Producto[]>([]);

  useEffect(() => {
    productoService.listar().then(setProductos);
  }, []);

  return (
    <ScrollView>
      <Stack.Screen options={opciones} />
      {productos.map((p) => (
        <Tarjeta key={p.id}>
          <Text style={styles.nombre}>{p.nombre}</Text>
          <Text>$ {p.precio.toFixed(2)} · Stock: {p.stock}</Text>
        </Tarjeta>
      ))}
      <Link href="/productos/detalle-producto" asChild>
        <Pressable style={styles.boton}>
          <Text style={styles.textoBoton}>Ver detalle</Text>
        </Pressable>
      </Link>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  nombre: { fontSize: 18, fontWeight: 'bold' },
  boton: { margin: 16, padding: 12, borderRadius: 8, backgroundColor: '#1f4e79' },
  textoBoton: { color: 'white', textAlign: 'center', fontWeight: 'bold' },
});
