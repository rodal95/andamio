// guía: La API del login: registrarse, pedir el token, renovarlo y saber quién es el usuario.
/**
 * Login con JWT: /api/token/, /api/token/refresh/, /api/registro/ y /api/yo/.
 *
 * Responde igual que la API de Django con nuevo login: el login de React, Vue o React Native
 * generado con andamio funciona con las dos.
 */
import { Router } from 'express';
import { prisma } from '../db.ts';
import { ErrorDeValidacion, validar } from '../errores.ts';
import { aJson, Credenciales, Refresco, Registro } from './esquema.ts';
import { crearToken, hashDe, puedeIngresar, requiereSesion, usuarioDelToken } from './seguridad.ts';

export const @@pluralCamel@@Router = Router();

const CREDENCIALES_INCORRECTAS = 'No se encontró una cuenta de usuario activa para las credenciales dadas';

/** Reglas para una contraseña (las mismas ideas que Django). */
function problemasDeLaPassword(password: string, username: string): string[] {
  // TODO(logica): más reglas si las necesitás (ej.: que tenga una mayúscula).
  const problemas = [];
  if (password.length < 8) problemas.push('La contraseña es demasiado corta. Debe contener al menos 8 caracteres.');
  if (/^\d+$/.test(password)) problemas.push('La contraseña está completamente en numérico.');
  if (username && password.toLowerCase().includes(username.toLowerCase())) {
    problemas.push('La contraseña es demasiado similar al nombre de usuario.');
  }
  return problemas;
}

@@pluralCamel@@Router.post('/registro/', async (req, res) => {
  const { password, ...datos } = validar(Registro, req.body);
  const errores: Record<string, string[]> = {};
  if (await prisma.usuario.findUnique({ where: { username: datos.username } })) {
    errores.username = ['Ya existe un usuario con este nombre.'];
  }
  const problemas = problemasDeLaPassword(password, datos.username);
  if (problemas.length) errores.password = problemas;
  // El mismo formato que los demás errores: {"campo": ["mensaje"]}.
  if (Object.keys(errores).length) throw new ErrorDeValidacion(errores);
  const usuario = await prisma.usuario
    .create({ data: { ...datos, passwordHash: hashDe(password) } })
    .catch((error: { code?: string }) => {
      // Dos registros con el mismo nombre al mismo tiempo: los dos pasaron la búsqueda de
      // arriba, pero la base (username es único) acepta solo el primero (P2002).
      if (error?.code === 'P2002') throw new ErrorDeValidacion({ username: ['Ya existe un usuario con este nombre.'] });
      throw error;
    });
  res.status(201).json(aJson(usuario));
});

// Con usuario y contraseña, devuelve el token de acceso y el de refresco.
@@pluralCamel@@Router.post('/token/', async (req, res) => {
  const { username, password } = validar(Credenciales, req.body);
  const usuario = await prisma.usuario.findUnique({ where: { username } });
  if (!puedeIngresar(usuario, password)) {
    res.status(401).json({ detail: CREDENCIALES_INCORRECTAS });
    return;
  }
  res.json({ access: await crearToken(usuario, 'access'), refresh: await crearToken(usuario, 'refresh') });
});

// Con el token de refresco, devuelve un token de acceso nuevo.
@@pluralCamel@@Router.post('/token/refresh/', async (req, res) => {
  const { refresh } = validar(Refresco, req.body);
  const usuario = await usuarioDelToken(refresh, 'refresh');
  if (!usuario) {
    res.status(401).json({ detail: 'El token no es válido o expiró.' });
    return;
  }
  res.json({ access: await crearToken(usuario, 'access') });
});

// El usuario dueño del token (sin token: 401).
@@pluralCamel@@Router.get('/yo/', requiereSesion, (req, res) => {
  res.json(aJson(res.locals.usuario));
});
