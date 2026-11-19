import { useEffect, useState } from 'react';
import { productoService, type Producto } from '../../services/productoService';
import styles from './CatalogoPage.module.css';

export function CatalogoPage() {
  // El estado de la página: la lista de productos y, si falla, el error.
  const [productos, setProductos] = useState<Producto[]>([]);
  const [error, setError] = useState('');

  // Al abrir la página, se piden los productos a la API (una sola vez: por eso el []).
  useEffect(() => {
    productoService
      .listar()
      .then(setProductos)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <main className={styles.root}>
      <h1>Catálogo</h1>
      {error && <p>No se pudo cargar: {error}</p>}
      <ul>
        {productos.map((producto) => (
          <li key={producto.id}>
            {producto.nombre}: $ {producto.precio}
          </li>
        ))}
      </ul>
    </main>
  );
}
