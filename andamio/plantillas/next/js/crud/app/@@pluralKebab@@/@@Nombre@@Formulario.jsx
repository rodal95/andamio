'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ErrorApi } from '@/services/http';
import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';
import styles from './@@pluralKebab@@.module.css';

/** @typedef {import('@/services/@@nombreCamel@@Service').@@Nombre@@Datos} @@Nombre@@Datos */

/**
 * Valores del formulario al crear uno nuevo.
 * @type {@@Nombre@@Datos}
 */
const VACIO = {
  @@valores_vacios@@
};

/**
 * Pasa un registro de la API a los datos del formulario.
 * @param {import('@/services/@@nombreCamel@@Service').@@Nombre@@} registro
 * @returns {@@Nombre@@Datos}
 */
function aDatos(registro) {
  return {
    @@campos_copiar@@
  };
}

/**
 * Formulario para crear (ruta /@@pluralKebab@@/nuevo) o editar (ruta /@@pluralKebab@@/3/editar).
 * Lo usan las dos páginas: si la dirección tiene un id, está editando.
 */
export function @@Nombre@@Formulario() {
  const { id } = useParams();
  const editando = id !== undefined;
  const router = useRouter();
  const [datos, setDatos] = useState(VACIO);
  // Errores de validación que devuelve la API, por campo: { nombre: ['Este campo...'] }
  const [errores, setErrores] = useState(/** @type {Record<string, string[]>} */ ({}));

  // Al editar, primero se cargan los datos actuales.
  useEffect(() => {
    if (editando) {
      @@nombreCamel@@Service.obtener(Number(id)).then((registro) => setDatos(aDatos(registro)));
    }
  }, [editando, id]);

  /**
   * @param {keyof @@Nombre@@Datos} campo
   * @param {unknown} valor
   */
  function cambiar(campo, valor) {
    setDatos((actual) => ({ ...actual, [campo]: valor }));
  }

  async function guardar() {
    try {
      const guardado = editando
        ? await @@nombreCamel@@Service.actualizar(Number(id), datos)
        : await @@nombreCamel@@Service.crear(datos);
      router.push(`/@@pluralKebab@@/${guardado.id}`);
    } catch (e) {
      if (e instanceof ErrorApi && e.estado === 400) {
        setErrores(/** @type {Record<string, string[]>} */ (e.detalle));
      } else {
        setErrores({ general: [e instanceof Error ? e.message : String(e)] });
      }
    }
  }

  return (
    <section>
      <h1>{editando ? 'Editar' : 'Agregar'}: @@nombreTitulo@@</h1>
      <form
        className={styles.formulario}
        onSubmit={(evento) => {
          evento.preventDefault();
          void guardar();
        }}
      >
        @@campos_formulario@@
        {errores.general && <p className={styles.error}>{errores.general.join(' ')}</p>}
        <div className={styles.acciones}>
          <button type="submit">Guardar</button>
          <button type="button" onClick={() => router.back()}>
            Cancelar
          </button>
        </div>
      </form>
    </section>
  );
}
