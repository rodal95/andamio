// guía: Qué datos aceptan el registro y el login (con Zod), y cómo se ve un usuario en el JSON.
/**
 * Usuarios del login: qué datos acepta la API y cómo se ve un usuario en el JSON.
 */
import { z } from 'zod';

/** Lo que hay que enviar para crear un usuario (POST /api/registro/). */
export const Registro = z.object({
  username: z.string('Este campo es requerido.').min(1, 'Este campo no puede estar en blanco.').max(150),
  password: z.string('Este campo es requerido.').min(1, 'Este campo no puede estar en blanco.'),
  // El email es opcional: vacío o una dirección válida.
  email: z.union([z.literal(''), z.email('Introduzca una dirección de correo electrónico válida.')]).default(''),
  first_name: z.string().max(150).default(''),
  last_name: z.string().max(150).default(''),
});

/** Lo que hay que enviar para pedir el token (POST /api/token/). */
export const Credenciales = z.object({
  username: z.string('Este campo es requerido.'),
  password: z.string('Este campo es requerido.'),
});

/** Lo que hay que enviar para renovar el token de acceso (POST /api/token/refresh/). */
export const Refresco = z.object({ refresh: z.string('Este campo es requerido.') });

/**
 * Un usuario en el JSON: nunca la contraseña. Igual que la API de Django.
 * @param {import('../generated/prisma/client.js').Usuario} usuario
 */
export function aJson(usuario) {
  const { id, username, email, first_name, last_name } = usuario;
  return { id, username, email, first_name, last_name };
}
