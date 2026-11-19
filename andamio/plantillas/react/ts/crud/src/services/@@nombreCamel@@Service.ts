import { http } from './http';

/** @@nombreTitulo@@ tal como lo devuelve la API: /api/@@plural@@/ */
export interface @@Nombre@@ {
  id: number;
  @@campos_ts@@
  creado: string;
  actualizado: string;
}

/** Datos para crear o modificar: todo menos lo que completa el servidor. */
export type @@Nombre@@Datos = Omit<@@Nombre@@, 'id' | 'creado' | 'actualizado'>;

// Con barra al final: así son las rutas de las APIs que genera andamio.
const RUTA = '/@@plural@@/';

export const @@nombreCamel@@Service = {
  listar: () => http.get<@@Nombre@@[]>(RUTA),
  obtener: (id: number) => http.get<@@Nombre@@>(`${RUTA}${id}/`),
  crear: (datos: @@Nombre@@Datos) => http.post<@@Nombre@@>(RUTA, datos),
  /** Modifica solo los campos que mandes. */
  actualizar: (id: number, datos: Partial<@@Nombre@@Datos>) => http.patch<@@Nombre@@>(`${RUTA}${id}/`, datos),
  eliminar: (id: number) => http.delete(`${RUTA}${id}/`),
};
