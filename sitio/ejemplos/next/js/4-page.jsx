'use client';

import Link from 'next/link';
import { Tarjeta } from '@/components';
import { useProductos } from '@/hooks/useProductos';
import styles from './page.module.css';

export default function CatalogoPage() {
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
          {/* La ruta /productos/3 es la carpeta app/productos/[id] que generó el crud. */}
          <Link href={`/productos/${producto.id}`}>Ver detalle</Link>
        </Tarjeta>
      ))}
    </section>
  );
}
