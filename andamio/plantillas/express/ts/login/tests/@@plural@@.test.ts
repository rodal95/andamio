/** Tests del login con JWT. Ejecutalos con: npm test */
import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';
import { api, prisma, usarToken } from './api.ts';

const USUARIO = { username: 'ana', email: 'ana@ejemplo.com', password: 'una-clave-larga-123' };

beforeEach(async () => {
  usarToken(null);
  await prisma.usuario.deleteMany({ where: { username: 'ana' } });
});

async function registrar() {
  const res = await api.post('/api/registro/', USUARIO);
  assert.equal(res.status, 201, JSON.stringify(res.datos));
  return res.datos;
}

const tokens = (password = USUARIO.password) => api.post('/api/token/', { username: 'ana', password });

test('registro', async () => {
  const usuario = await registrar();
  assert.equal(usuario.username, 'ana');
  assert.equal('password' in usuario || 'passwordHash' in usuario, false);
});

test('el registro rechaza una clave débil y un usuario repetido', async () => {
  const debil = await api.post('/api/registro/', { ...USUARIO, password: '123' });
  assert.equal(debil.status, 400);
  assert.ok('password' in debil.datos);
  await registrar();
  const repetido = await api.post('/api/registro/', USUARIO);
  assert.equal(repetido.status, 400);
  assert.ok('username' in repetido.datos);
});

test('el login devuelve los tokens', async () => {
  await registrar();
  const res = await tokens();
  assert.equal(res.status, 200);
  assert.ok(res.datos.access && res.datos.refresh);
});

test('login con clave incorrecta', async () => {
  await registrar();
  assert.equal((await tokens('otra')).status, 401);
});

test('yo, con y sin token', async () => {
  await registrar();
  assert.equal((await api.get('/api/yo/')).status, 401);
  usarToken((await tokens()).datos.access);
  const res = await api.get('/api/yo/');
  assert.equal(res.status, 200);
  assert.equal(res.datos.username, 'ana');
  usarToken('no-es-un-token');
  assert.equal((await api.get('/api/yo/')).status, 401);
});

test('renovar el token', async () => {
  await registrar();
  const { access, refresh } = (await tokens()).datos;
  const res = await api.post('/api/token/refresh/', { refresh });
  assert.equal(res.status, 200);
  assert.ok(res.datos.access);
  // El de acceso no sirve para renovar.
  assert.equal((await api.post('/api/token/refresh/', { refresh: access })).status, 401);
});
