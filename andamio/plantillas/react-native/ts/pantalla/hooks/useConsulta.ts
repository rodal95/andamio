import { useCallback, useEffect, useState } from 'react';

/**
 * useConsulta: pide datos a la API y guarda el resultado, si está cargando y el error.
 * Sirve para cualquier servicio:
 *
 *   const { datos, cargando, error } = useConsulta(productoService.listar);
 *   const { datos } = useConsulta(() => productoService.obtener(id), [id]);
 *
 * El segundo parámetro son los valores que, si cambian, hacen repetir la consulta.
 */
export function useConsulta<T>(consulta: () => Promise<T>, dependencias: unknown[] = []) {
  const [datos, setDatos] = useState<T | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [vuelta, setVuelta] = useState(0);

  useEffect(() => {
    // Si el componente se cierra antes de que llegue la respuesta, se ignora.
    let vigente = true;
    setCargando(true);
    setError(null);
    consulta()
      .then((resultado) => {
        if (vigente) setDatos(resultado);
      })
      .catch((e: unknown) => {
        if (vigente) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });
    return () => {
      vigente = false;
    };
    // La consulta se repite cuando cambian las dependencias o al llamar a recargar().
  }, [...dependencias, vuelta]);

  const recargar = useCallback(() => setVuelta((v) => v + 1), []);

  return { datos, cargando, error, recargar };
}
