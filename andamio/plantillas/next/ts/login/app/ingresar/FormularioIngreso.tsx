'use client';

@@importar_link@@
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import type { Credenciales } from '@/services/authService';
import { ErrorApi } from '@/services/http';
import { aDondeVolver, ingresar, useSesion } from '@/sesion';
import styles from './ingresar.module.css';

const VACIO: Credenciales = { username: '', password: '' };

/** El formulario para ingresar. desde: la página que lo pidió (?desde=). */
export function FormularioIngreso({ desde }: { desde?: string | string[] }) {
  // guía: Si llegó desde una página protegida, después de ingresar vuelve ahí (si es de esta app).
  const destino = aDondeVolver(desde);
  const router = useRouter();
  const { usuario } = useSesion();
  const [datos, setDatos] = useState<Credenciales>(VACIO);
  const [errores, setErrores] = useState<Record<string, string[]>>({});
  const [enviando, setEnviando] = useState(false);

  // guía: Cuando ingresar() termina bien, useSesion() cambia y esto lleva a la página de antes.
  useEffect(() => {
    if (usuario) {
      router.replace(destino);
    }
  }, [usuario, destino, router]);

  function cambiar<K extends keyof Credenciales>(campo: K, valor: Credenciales[K]) {
    setDatos((actual) => ({ ...actual, [campo]: valor }));
  }

  async function enviar() {
    setErrores({});
    setEnviando(true);
    try {
      await ingresar(datos);
    } catch (e) {
      // guía: Usuario o contraseña incorrectos: la API responde 401 y lo explica (va en general).
      if (e instanceof ErrorApi && e.estado === 400) {
        setErrores(e.detalle as Record<string, string[]>);
      } else {
        setErrores({ general: [e instanceof Error ? e.message : String(e)] });
      }
      setEnviando(false);
    }
  }

  return (
    <section className={styles.root}>
      <h1>Ingresar</h1>
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
          Contraseña
          <input
            type="password"
            autoComplete="current-password"
            required
            value={datos.password}
            onChange={(e) => cambiar('password', e.target.value)}
          />
          {errores.password && <small className={styles.error}>{errores.password.join(' ')}</small>}
        </label>
        {errores.general && <p className={styles.error}>{errores.general.join(' ')}</p>}
        <div>
          <button type="submit" disabled={enviando}>
            {enviando ? 'Ingresando…' : 'Ingresar'}
          </button>
        </div>
      </form>
      @@pie_ingresar@@
    </section>
  );
}
