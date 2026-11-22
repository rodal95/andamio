import { http } from './http';

// guía: El login de la API (Django, FastAPI o Express con: python -m andamio nuevo login):
// guía:   POST /api/token/     {"username", "password"}  ->  {"access", "refresh"}
// guía:   POST /api/registro/  crea un usuario: {"username", "email", "password"}
// guía:   GET  /api/yo/        el usuario dueño del token

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

interface Tokens {
  access: string; // el que se manda en cada pedido; dura 60 minutos
  refresh: string; // sirve para pedir otro access sin volver a ingresar (acá no se usa)
}

export const authService = {
  /** Pide los tokens con usuario y contraseña. */
  pedirTokens: (credenciales: Credenciales) => http.post<Tokens>('/token/', credenciales),
  /** Crea el usuario (no ingresa: para eso, pedirTokens). */
  registrarse: (datos: DatosRegistro) => http.post<Usuario>('/registro/', datos),
  /** El usuario del token que se está usando. Si venció, la API responde 401. */
  yo: () => http.get<Usuario>('/yo/'),
};
