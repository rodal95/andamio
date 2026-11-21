// guía: El formulario para crear y editar. useFormulario (src/hooks) carga el registro al editar,
// guía: lo guarda con el servicio (src/services) y deja los errores de la API por campo.
import { useNavigate, useParams } from 'react-router';
import { useFormulario } from '../../hooks/useFormulario';
import { @@nombreCamel@@Service, type @@Nombre@@, type @@Nombre@@Datos } from '../../services/@@nombreCamel@@Service';
@@imports_relaciones@@
import styles from './@@pluralKebab@@.module.css';

// Valores del formulario al crear uno nuevo.
const VACIO: @@Nombre@@Datos = {
  @@valores_vacios@@
};

/** Pasa un registro de la API a los datos del formulario. */
function aDatos(registro: @@Nombre@@): @@Nombre@@Datos {
  return {
    @@campos_copiar@@
  };
}

/** Formulario para crear (ruta /@@pluralKebab@@/nuevo) o editar (ruta /@@pluralKebab@@/:id/editar). */
export function @@Nombre@@FormPage() {
  const { id } = useParams();
  const navegar = useNavigate();
  const { datos, cambiar, errores, guardar, editando } = useFormulario(
    @@nombreCamel@@Service,
    id === undefined ? undefined : Number(id),
    VACIO,
    aDatos,
  );
  @@consultas_relaciones@@

  async function enviar() {
    // TODO(logica): validaciones del formulario antes de enviar (la API también valida).
    // Ejemplo (sumá setErrores a lo que tomás de useFormulario):
    // if (Number(datos.precio) <= 0) { setErrores({ precio: ['Tiene que ser mayor que cero.'] }); return; }
    const guardado = await guardar();
    if (guardado) navegar(`/@@pluralKebab@@/${guardado.id}`);
  }

  return (
    <main className={styles.pagina}>
      <h1>{editando ? 'Editar' : 'Agregar'}: @@nombreTitulo@@</h1>
      <form
        className={styles.formulario}
        onSubmit={(evento) => {
          evento.preventDefault();
          void enviar();
        }}
      >
        @@campos_formulario@@
        {errores.general && <p className={styles.error}>{errores.general.join(' ')}</p>}
        <div className={styles.acciones}>
          <button type="submit">Guardar</button>
          <button type="button" onClick={() => navegar(-1)}>
            Cancelar
          </button>
        </div>
      </form>
    </main>
  );
}
