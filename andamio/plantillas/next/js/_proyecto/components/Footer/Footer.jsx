import styles from './Footer.module.css';

/** El pie, abajo de todas las páginas (lo muestra el Layout). */
export function Footer() {
  return (
    <footer className={styles.root}>
      <small>
        © {new Date().getFullYear()} @@proyectoTitulo@@
      </small>
    </footer>
  );
}
