import { Link } from 'react-router';
import { salir, useSesion } from './sesion';
import styles from './MenuSesion.module.css';

/** En el menú: Ingresar@@y_registrarse@@, o quién ingresó y Salir. */
export function MenuSesion() {
  const { usuario, cargando } = useSesion();
  if (cargando) {
    return null;
  }
  return (
    <span className={styles.sesion}>
      {usuario ? (
        <>
          {/* guía: Los enlaces a las páginas protegidas (--protegido): solo se ven si alguien ingresó. */}
          {/* --- andamio:enlaces_sesion (no borrar esta línea) --- */}
          <span>{usuario.username}</span>
          <button type="button" onClick={salir}>
            Salir
          </button>
        </>
      ) : (
        <>
          <Link to="/ingresar">Ingresar</Link>
          @@enlace_registro@@
        </>
      )}
    </span>
  );
}
