import { Link } from 'react-router';
import { useConsulta } from '../../hooks/useConsulta';
import { @@nombreCamel@@Service } from '../../services/@@nombreCamel@@Service';
import styles from './@@pluralKebab@@.module.css';

/** Lista de @@titulo@@ (ruta /@@pluralKebab@@): pide todos a la API con listar(). */
export function @@Nombre@@ListaPage() {
  const { datos, cargando, error } = useConsulta(@@nombreCamel@@Service.listar);

  return (
    <main className={styles.pagina}>
      <div className={styles.encabezado}>
        <h1>@@titulo@@</h1>
        <Link to="/@@pluralKebab@@/nuevo">Agregar</Link>
      </div>
      {cargando && <p>Cargando…</p>}
      {error && <p className={styles.error}>No se pudo cargar la lista: {error}</p>}
      {datos?.length === 0 && <p>Todavía no hay registros.</p>}
      <ul className={styles.lista}>
        {datos?.map((item) => (
          <li key={item.id}>
            <Link to={`/@@pluralKebab@@/${item.id}`}>{@@texto_item@@}</Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
