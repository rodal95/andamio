import { useEffect, useState } from 'react';
import { productoService } from '../services/productoService';

/**
 * useProductos: pide los productos a la API y avisa si está cargando o si hubo un error.
 * Cualquier página o componente lo puede usar: const { productos } = useProductos();
 */
export function useProductos() {
  const [productos, setProductos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    productoService
      .listar()
      .then(setProductos)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setCargando(false));
  }, []);

  return { productos, cargando, error };
}
