'use client';

import { useParams, useRouter } from 'next/navigation';
import { @@Nombre@@Detalle } from '@/components/@@Nombre@@Detalle';
import { useConsulta } from '@/hooks/useConsulta';
import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';
import styles from '../@@pluralKebab@@.module.css';

/**
 * Detalle (ruta /@@pluralKebab@@/3, la carpeta [id]): pide uno a la API con obtener(id) y lo elimina con eliminar(id).
 * La página habla con el servicio; el componente @@Nombre@@Detalle solo muestra y avisa.
 */
export default function @@Nombre@@DetallePage() {
  const id = Number(useParams<{ id: string }>().id);
  const router = useRouter();
  const { datos, cargando, error } = useConsulta(() => @@nombreCamel@@Service.obtener(id), [id]);

  async function eliminar() {
    if (!window.confirm('¿Seguro que querés eliminarlo?')) return;
    try {
      await @@nombreCamel@@Service.eliminar(id);
      router.push('/@@pluralKebab@@');
    } catch (e) {
      window.alert(`No se pudo eliminar: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  return (
    <section>
      <h1>@@nombreTitulo@@ {id}</h1>
      {cargando && <p>Cargando…</p>}
      {error && <p className={styles.error}>No se pudo cargar: {error}</p>}
      {datos && (
        <@@Nombre@@Detalle
          @@nombreCamel@@={datos}
          onEditar={() => router.push(`/@@pluralKebab@@/${id}/editar`)}
          onEliminar={eliminar}
        />
      )}
    </section>
  );
}
