import styles from './@@Nombre@@Detalle.module.css';

/**
 * @typedef {Object} @@Nombre@@DetalleProps
 * @property {import('../../services/@@nombreCamel@@Service').@@Nombre@@} @@nombreCamel@@
 * @property {() => void} onEditar Se llama al tocar Editar.
 * @property {() => void} onEliminar Se llama al tocar Eliminar.
 */

/**
 * Muestra los datos de un registro de @@titulo@@ con los botones Editar y Eliminar.
 * No llama a la API: recibe los datos y avisa con onEditar y onEliminar. Así se puede
 * reutilizar en cualquier página.
 *
 * @param {@@Nombre@@DetalleProps} props
 */
export function @@Nombre@@Detalle({ @@nombreCamel@@, onEditar, onEliminar }) {
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
