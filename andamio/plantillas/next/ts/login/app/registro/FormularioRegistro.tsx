'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import type { DatosRegistro } from '@/services/authService';
import { ErrorApi } from '@/services/http';
import { aDondeVolver, registrarse, useSesion } from '@/sesion';
import styles from './registro.module.css';

// guía: repetir no va a la API: es para controlar acá que la contraseña se escribió bien.
interface Formulario extends DatosRegistro {
  repetir: string;
}

const VACIO: Formulario = { username: '', email: '', password: '', repetir: '' };

/** El formulario para crear una cuenta. desde: la página que pidió ingresar (?desde=). */
export function FormularioRegistro({ desde }: { desde?: string | string[] }) {
  const destino = aDondeVolver(desde);
  const router = useRouter();
  const { usuario } = useSesion();
  const [datos, setDatos] = useState<Formulario>(VACIO);
  const [errores, setErrores] = useState<Record<string, string[]>>({});
  const [enviando, setEnviando] = useState(false);

  // guía: registrarse() crea el usuario y también ingresa: useSesion() cambia y esto lleva a la página de antes.
  useEffect(() => {
    if (usuario) {
      router.replace(destino);
    }
  }, [usuario, destino, router]);

  function cambiar<K extends keyof Formulario>(campo: K, valor: Formulario[K]) {
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
        setErrores(e.detalle as Record<string, string[]>);
      } else {
        setErrores({ general: [e instanceof Error ? e.message : String(e)] });
      }
      setEnviando(false);
    }
  }

  return (
    <section className={styles.root}>
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
        ¿Ya tenés cuenta? <Link href={{ pathname: '/ingresar', query: { desde: destino } }}>Ingresá</Link>
      </p>
    </section>
  );
}
