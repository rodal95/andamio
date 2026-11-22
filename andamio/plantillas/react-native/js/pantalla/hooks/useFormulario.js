import { useEffect, useState } from 'react';
import { ErrorApi } from '@/services/http';

/**
 * Errores por campo, como los devuelve la API: { nombre: ['Este campo es obligatorio.'] }
 * @typedef {Record<string, string[]>} Errores
 */

/**
 * Lo que el formulario necesita de un servicio: obtener, crear y actualizar.
 * @template T, D
 * @typedef {Object} ServicioEditable
 * @property {(id: number) => Promise<T>} obtener
 * @property {(datos: D) => Promise<T>} crear
 * @property {(id: number, datos: Partial<D>) => Promise<T>} actualizar
 */

/**
 * useFormulario: los datos de un formulario para crear o editar con un servicio.
 * Sirve para cualquier servicio:
 *
 *   const { datos, cambiar, errores, guardar, editando } = useFormulario(productoService, id, VACIO, aDatos);
 *
 * - id: undefined para crear; el id del registro para editar (primero lo carga).
 * - vacio: los valores del formulario al crear.
 * - aDatos: pasa un registro de la API a los datos del formulario.
 * cargado es false mientras se cargan los datos del registro que se edita.
 * guardar() crea o actualiza y devuelve lo guardado, o null si la API respondió con errores
 * (quedan en errores, por campo; los que no son de un campo, en errores.general).
 *
 * @template T, D
 * @param {ServicioEditable<T, D>} servicio
 * @param {number | undefined} id
 * @param {D} vacio
 * @param {(registro: T) => D} aDatos
 */
export function useFormulario(servicio, id, vacio, aDatos) {
  const [datos, setDatos] = useState(vacio);
  const [errores, setErrores] = useState(/** @type {Errores} */ ({}));
  const editando = id !== undefined;
  // Al crear no hay nada que cargar; al editar, se pone en true cuando llegan los datos.
  const [cargado, setCargado] = useState(!editando);

  // Al editar, primero se cargan los datos actuales.
  useEffect(() => {
    if (id === undefined) return;
    let vigente = true;
    servicio
      .obtener(id)
      .then((registro) => {
        if (vigente) {
          setDatos(aDatos(registro));
          setCargado(true);
        }
      })
      .catch((e) => {
        if (vigente) setErrores({ general: [e instanceof Error ? e.message : String(e)] });
      });
    return () => {
      vigente = false;
    };
    // Se repite solo si cambia el id (el servicio y aDatos son siempre los mismos).
  }, [id]);

  /**
   * @param {keyof D} campo
   * @param {unknown} valor
   */
  function cambiar(campo, valor) {
    setDatos((actual) => ({ ...actual, [campo]: valor }));
  }

  /** @returns {Promise<T | null>} */
  async function guardar() {
    setErrores({});
    try {
      return id === undefined ? await servicio.crear(datos) : await servicio.actualizar(id, datos);
    } catch (e) {
      if (e instanceof ErrorApi && e.estado === 400) {
        setErrores(/** @type {Errores} */ (e.detalle));
      } else {
        setErrores({ general: [e instanceof Error ? e.message : String(e)] });
      }
      return null;
    }
  }

  return { datos, cambiar, errores, setErrores, guardar, editando, cargado };
}
