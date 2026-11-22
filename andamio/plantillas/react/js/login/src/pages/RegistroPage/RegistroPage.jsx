import { useState } from 'react';
import { Link, Navigate, useLocation } from 'react-router';
import { ErrorApi } from '../../services/http';
import { registrarse, useSesion } from '../../sesion';
import styles from './RegistroPage.module.css';

// guía: repetir no va a la API: es para controlar acá que la contraseña se escribió bien.
/** @typedef {import('../../services/authService').DatosRegistro & { repetir: string }} Formulario */

/** @type {Formulario} */
const VACIO = { username: '', email: '', password: '', repetir: '' };

export function RegistroPage() {
  const desde = useLocation().state?.desde ?? '/';
  const { usuario } = useSesion();
  const [datos, setDatos] = useState(VACIO);
  const [errores, setErrores] = useState(/** @type {Record<string, string[]>} */ ({}));
  const [enviando, setEnviando] = useState(false);

  // guía: registrarse() crea el usuario y también ingresa: useSesion() cambia y esto lleva a la página de antes.
  if (usuario) {
    return <Navigate to={desde} replace />;
  }

  /**
   * @param {keyof Formulario} campo
   * @param {string} valor
   */
  function cambiar(campo, valor) {
    setDatos((actual) => ({ ...actual, [campo]: valor }));
  }

  async function enviar() {
    // TODO(logica): más reglas antes de enviar (la API también valida: usuario repetido, contraseña corta o muy común).
    if (datos.password !== datos.repetir) {
      setErrores({ repetir: ['Las contraseñas no coinciden.'] });
      return;
    }
    setErrores({});
    setEnviando(true);
    try {
      await registrarse({ username: datos.username, email: datos.email, password: datos.password });
    } catch (e) {
      // guía: 400: la API dice qué está mal en cada campo (ej.: "Ya existe un usuario con este nombre.").
      if (e instanceof ErrorApi && e.estado === 400) {
        setErrores(/** @type {Record<string, string[]>} */ (e.detalle));
      } else {
        setErrores({ general: [e instanceof Error ? e.message : String(e)] });
      }
      setEnviando(false);
    }
  }

  return (
    <main className={styles.root}>
      <h1>Crear una cuenta</h1>
      <form
        className={styles.formulario}
        onSubmit={(evento) => {
          evento.preventDefault();
          void enviar();
        }}
      >
        <label className={styles.campo}>
          Usuario
          <input autoComplete="username" required value={datos.username} onChange={(e) => cambiar('username', e.target.value)} />
          {errores.username && <small className={styles.error}>{errores.username.join(' ')}</small>}
        </label>
        <label className={styles.campo}>
          Email
          <input type="email" autoComplete="email" value={datos.email} onChange={(e) => cambiar('email', e.target.value)} />
          {errores.email && <small className={styles.error}>{errores.email.join(' ')}</small>}
        </label>
        <label className={styles.campo}>
          Contraseña
          <input
            type="password"
            autoComplete="new-password"
            required
            value={datos.password}
            onChange={(e) => cambiar('password', e.target.value)}
          />
          {errores.password && <small className={styles.error}>{errores.password.join(' ')}</small>}
        </label>
        <label className={styles.campo}>
          Repetí la contraseña
          <input
            type="password"
            autoComplete="new-password"
            required
            value={datos.repetir}
            onChange={(e) => cambiar('repetir', e.target.value)}
          />
          {errores.repetir && <small className={styles.error}>{errores.repetir.join(' ')}</small>}
        </label>
        {errores.general && <p className={styles.error}>{errores.general.join(' ')}</p>}
        <div>
          <button type="submit" disabled={enviando}>
            {enviando ? 'Creando la cuenta…' : 'Crear la cuenta'}
          </button>
        </div>
      </form>
      <p>
        ¿Ya tenés cuenta?{' '}
        <Link to="/ingresar" state={{ desde }}>
          Ingresá
        </Link>
      </p>
    </main>
  );
}
