import { http } from './http';

// guía: El login de la API de este proyecto (app/api/):
// guía:   POST /api/token/     {"username", "password"}  ->  deja la cookie de la sesión
// guía:   POST /api/registro/  crea un usuario: {"username", "email", "password"}
// guía:   GET  /api/yo/        el usuario de la sesión
// guía:   POST /api/salir/     borra la cookie
// guía: El token no se guarda acá: queda en una cookie httpOnly que el navegador manda sola.

/** Un usuario, como lo devuelve la API (nunca trae la contraseña). */
export interface Usuario {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

/** Lo que pide el ingreso. */
export interface Credenciales {
  username: string;
  password: string;
}

/** Lo que pide el registro. */
export interface DatosRegistro extends Credenciales {
  email: string;
}

export const authService = {
  /** Ingresa (la API deja la cookie de la sesión) y devuelve el usuario. */
  async ingresar(credenciales: Credenciales): Promise<Usuario> {
    await http.post('/token/', credenciales);
    return http.get<Usuario>('/yo/');
  },
  /** Crea el usuario (no ingresa: para eso, ingresar). */
  registrarse: (datos: DatosRegistro) => http.post<Usuario>('/registro/', datos),
  /** El usuario de la sesión. Sin sesión (o si venció), la API responde 401. */
  yo: () => http.get<Usuario>('/yo/'),
  /** Sale: la API borra la cookie (la página no puede: es httpOnly). */
  salir: () => http.post<void>('/salir/', {}),
};
