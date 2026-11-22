/** Tests del login (app/api/token, registro, yo y salir). Ejecutalos con: npm test */
import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';

// Los tests firman tokens: con el .env, o una clave solo para los tests si no está.
try {
  process.loadEnvFile();
} catch {
  // sin .env
}
process.env.SECRET_KEY ||= 'clave-solo-para-los-tests';
process.env.DATABASE_URL = process.env.TEST_DATABASE_URL || 'file:./test.db'; // antes de cargar la conexión (como en tests/api)
const { prisma } = await import('../lib/db');
const RUTAS = {
  '/api/registro/': await import('../app/api/registro/route'),
  '/api/token/': await import('../app/api/token/route'),
  '/api/token/refresh/': await import('../app/api/token/refresh/route'),
  '/api/yo/': await import('../app/api/yo/route'),
  '/api/salir/': await import('../app/api/salir/route'),
};

type Ruta = keyof typeof RUTAS;
type Opciones = { datos?: unknown; token?: string; cookie?: string };

/** Llama a la función de la ruta (GET o POST) como lo hace Next.js, sin levantar el servidor. */
async function pedir(metodo: 'GET' | 'POST', ruta: Ruta, { datos, token, cookie }: Opciones = {}) {
  const funcion = (RUTAS[ruta] as Record<string, (request: Request) => Promise<Response>>)[metodo];
  const headers: Record<string, string> = {};
  if (datos !== undefined) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;
  if (cookie) headers.Cookie = cookie;
  const body = datos === undefined ? undefined : JSON.stringify(datos);
  const respuesta = await funcion(new Request(`http://localhost${ruta}`, { method: metodo, headers, body }));
  const texto = await respuesta.text();
  return { status: respuesta.status, datos: texto ? JSON.parse(texto) : null, cookie: respuesta.headers.get('set-cookie') ?? '' };
}

const USUARIO = { username: 'ana', email: 'ana@ejemplo.com', password: 'una-clave-larga-123' };

beforeEach(async () => {
  await prisma.usuario.deleteMany({ where: { username: 'ana' } });
});

async function registrar() {
  const res = await pedir('POST', '/api/registro/', { datos: USUARIO });
  assert.equal(res.status, 201, JSON.stringify(res.datos));
  return res.datos;
}

const ingresar = (password = USUARIO.password) => pedir('POST', '/api/token/', { datos: { username: 'ana', password } });

test('registro', async () => {
  const usuario = await registrar();
  assert.equal(usuario.username, 'ana');
  assert.equal('password' in usuario || 'passwordHash' in usuario, false);
});

test('el registro rechaza una clave débil y un usuario repetido', async () => {
  const debil = await pedir('POST', '/api/registro/', { datos: { ...USUARIO, password: '123' } });
  assert.equal(debil.status, 400);
  assert.ok('password' in debil.datos);
  await registrar();
  const repetido = await pedir('POST', '/api/registro/', { datos: USUARIO });
  assert.equal(repetido.status, 400);
  assert.ok('username' in repetido.datos);
});

test('ingresar devuelve los tokens y deja la cookie httpOnly', async () => {
  await registrar();
  const res = await ingresar();
  assert.equal(res.status, 200);
  assert.ok(res.datos.access && res.datos.refresh);
  assert.match(res.cookie, /^sesion=[^;]+; .*HttpOnly/);
});

test('ingresar con la clave incorrecta', async () => {
  await registrar();
  const res = await ingresar('otra');
  assert.equal(res.status, 401);
  assert.equal(res.cookie, '');
});

test('un usuario que no existe o desactivado no ingresa', async () => {
  // guía: Las dos respuestas son iguales (y tardan lo mismo): no dan pistas de qué usuarios existen.
  assert.equal((await ingresar()).status, 401);
  await registrar();
  await prisma.usuario.update({ where: { username: 'ana' }, data: { activo: false } });
  assert.equal((await ingresar()).status, 401);
});

test('yo, con el token, con la cookie y sin sesión', async () => {
  await registrar();
  assert.equal((await pedir('GET', '/api/yo/')).status, 401);
  const { datos, cookie } = await ingresar();
  assert.equal((await pedir('GET', '/api/yo/', { token: datos.access })).datos.username, 'ana');
  assert.equal((await pedir('GET', '/api/yo/', { cookie: cookie.split(';')[0] })).datos.username, 'ana');
  assert.equal((await pedir('GET', '/api/yo/', { token: 'no-es-un-token' })).status, 401);
});

test('renovar el token', async () => {
  await registrar();
  const { access, refresh } = (await ingresar()).datos;
  const res = await pedir('POST', '/api/token/refresh/', { datos: { refresh } });
  assert.equal(res.status, 200);
  assert.ok(res.datos.access);
  // El de acceso no sirve para renovar.
  assert.equal((await pedir('POST', '/api/token/refresh/', { datos: { refresh: access } })).status, 401);
});

test('salir borra la cookie', async () => {
  const res = await pedir('POST', '/api/salir/');
  assert.equal(res.status, 204);
  assert.match(res.cookie, /^sesion=; .*Max-Age=0/);
});
