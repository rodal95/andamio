import styles from './@@Nombre@@.module.css';

/**
 * @typedef {Object} @@Nombre@@Props
 * @property {import('react').ReactNode} [children] Lo que va adentro: <@@Nombre@@>contenido</@@Nombre@@>
 */

/** @param {@@Nombre@@Props} props */
export function @@Nombre@@({ children }) {
  return <div className={styles.root}>{children}</div>;
}
