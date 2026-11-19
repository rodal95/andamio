import { Link } from 'react-router';
import { Tarjeta } from '../../components';
import { useProductos } from '../../hooks/useProductos';
import styles from './CatalogoPage.module.css';

export function CatalogoPage() {
  const { productos, cargando, error } = useProductos();

  return (
    <main className={styles.root}>
      <h1>Catálogo</h1>
      {cargando && <p>Cargando…</p>}
      {error && <p>No se pudo cargar: {error}</p>}
      {productos.map((producto) => (
        <Tarjeta key={producto.id}>
          <h3>{producto.nombre}</h3>
          <p>
            $ {producto.precio} · {producto.stock} en stock
          </p>
          {/* La ruta /productos/:id es la del detalle que generó el crud. */}
          <Link to={`/productos/${producto.id}`}>Ver detalle</Link>
        </Tarjeta>
      ))}
    </main>
  );
}
