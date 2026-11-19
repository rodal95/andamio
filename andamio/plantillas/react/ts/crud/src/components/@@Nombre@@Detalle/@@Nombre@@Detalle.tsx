import type { @@Nombre@@ } from '../../services/@@nombreCamel@@Service';
import styles from './@@Nombre@@Detalle.module.css';

export interface @@Nombre@@DetalleProps {
  @@nombreCamel@@: @@Nombre@@;
  /** Se llama al tocar Editar. */
  onEditar: () => void;
  /** Se llama al tocar Eliminar. */
  onEliminar: () => void;
}

/**
 * Muestra los datos de un registro de @@titulo@@ con los botones Editar y Eliminar.
 * No llama a la API: recibe los datos y avisa con onEditar y onEliminar. Así se puede
 * reutilizar en cualquier página.
 */
export function @@Nombre@@Detalle({ @@nombreCamel@@, onEditar, onEliminar }: @@Nombre@@DetalleProps) {
  return (
    <article className={styles.root}>
      <dl className={styles.datos}>
        @@campos_detalle@@
      </dl>
      <div className={styles.acciones}>
        <button type="button" onClick={onEditar}>
          Editar
        </button>
        <button type="button" onClick={onEliminar}>
          Eliminar
        </button>
      </div>
    </article>
  );
}
