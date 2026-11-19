'use client';

import { useEffect, useState } from 'react';
import { productoService } from '@/services/productoService';
import styles from './page.module.css';

export default function CatalogoPage() {
  // El estado de la página: la lista de productos y, si falla, el error.
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState('');

  // Al abrir la página, se piden los productos a la API (una sola vez: por eso el []).
  useEffect(() => {
    productoService
      .listar()
      .then(setProductos)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <section className={styles.root}>
      <h1>Catálogo</h1>
      {error && <p>No se pudo cargar: {error}</p>}
      <ul>
        {productos.map((producto) => (
          <li key={producto.id}>
            {producto.nombre}: $ {producto.precio}
          </li>
        ))}
      </ul>
    </section>
  );
}
