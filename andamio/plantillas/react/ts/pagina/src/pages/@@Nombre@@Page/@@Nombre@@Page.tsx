@@datos_imports@@
import styles from './@@Nombre@@Page.module.css';

@@datos_previo@@
export function @@Nombre@@Page() {
  @@datos_consulta@@
  return (
    <main className={styles.root}>
      <h1>@@nombreTitulo@@</h1>
      @@datos_contenido@@
    </main>
  );
}
