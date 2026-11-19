import { useEffect, useState } from 'react';
import { Tarjeta } from '../../components';
import { productoService, type Producto } from '../../services/productoService';
import styles from './CatalogoPage.module.css';

export function CatalogoPage() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [error, setError] = useState('');

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
      {/* Cada producto se muestra con el componente Tarjeta: lo de adentro es su children. */}
      {productos.map((producto) => (
        <Tarjeta key={producto.id}>
          <h3>{producto.nombre}</h3>
          <p>
            $ {producto.precio} · {producto.stock} en stock
          </p>
        </Tarjeta>
      ))}
    </main>
  );
}
