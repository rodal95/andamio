'use client';

import { Tarjeta } from '@/components';
import { useProductos } from '@/hooks/useProductos';
import styles from './page.module.css';

export default function CatalogoPage() {
  // Toda la lógica de pedir los datos quedó en el hook: la página solo los muestra.
  const { productos, cargando, error } = useProductos();

  return (
    <section className={styles.root}>
      <h1>Catálogo</h1>
      {cargando && <p>Cargando…</p>}
      {error && <p>No se pudo cargar: {error}</p>}
      {productos.map((producto) => (
        <Tarjeta key={producto.id}>
          <h3>{producto.nombre}</h3>
          <p>
            $ {producto.precio} · {producto.stock} en stock
          </p>
        </Tarjeta>
      ))}
    </section>
  );
}
