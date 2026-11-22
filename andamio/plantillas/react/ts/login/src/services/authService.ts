import { borrarToken, guardarToken, http } from './http';

// guía: El login de la API (Django con: python -m andamio nuevo login):
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
  /** Pide el token, lo guarda (desde ahí cada pedido lo manda solo) y devuelve el usuario. */
  async ingresar(credenciales: Credenciales): Promise<Usuario> {
    borrarToken(); // si quedó uno viejo, la API lo rechazaría
    const tokens = await http.post<Tokens>('/token/', credenciales);
    guardarToken(tokens.access);
    return http.get<Usuario>('/yo/');
  },
  /** Crea el usuario (no ingresa: para eso, ingresar). */
  registrarse(datos: DatosRegistro): Promise<Usuario> {
    borrarToken();
    return http.post<Usuario>('/registro/', datos);
  },
  /** El usuario del token guardado. Si venció, la API responde 401. */
  yo: () => http.get<Usuario>('/yo/'),
  /** Cierra la sesión: borra el token. */
  salir: () => borrarToken(),
};
