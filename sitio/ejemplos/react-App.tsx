import { useEffect, useState } from 'react';
import { Tarjeta } from './components';
import { useContador } from './hooks/useContador';
import { ProductosPage } from './pages/ProductosPage';
import { productoService, type Producto } from './services/productoService';

function App() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const { valor: carrito, setValor: setCarrito, reiniciar } = useContador(0);

  useEffect(() => {
    productoService.listar().then(setProductos);
  }, []);

  return (
    <>
      <ProductosPage />
      <p>En el carrito: {carrito} <button onClick={reiniciar}>Vaciar</button></p>
      {productos.map((p) => (
        <Tarjeta key={p.id}>
          <h3>{p.nombre}</h3>
          <p>$ {p.precio.toFixed(2)} · Stock: {p.stock}</p>
          <button onClick={() => setCarrito(carrito + 1)}>Agregar</button>
        </Tarjeta>
      ))}
    </>
  );
}

export default App;
