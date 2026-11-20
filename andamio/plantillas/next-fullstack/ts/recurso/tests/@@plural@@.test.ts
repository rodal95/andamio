/** Tests de la API de @@titulo@@. Ejecutalos con: npm test */
import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';
import { abrir } from './api';

const { api, prisma } = await abrir('@@plural@@');

const URL = '/api/@@plural@@/';

const DATOS = {
  @@datos_prueba@@
};

const DATOS_MODIFICADOS = {
  @@datos_modificados@@
};

// Cada test empieza con la tabla vacía.
beforeEach(async () => {
  await prisma.@@nombreCamel@@.deleteMany();
});

async function crear() {
  const res = await api.post(URL, DATOS);
  assert.equal(res.status, 201, JSON.stringify(res.datos));
  return res.datos;
}

test('listar', async () => {
  await crear();
  const res = await api.get(URL);
  assert.equal(res.status, 200);
  // Sin paginación, la res es directamente una lista.
  assert.equal(res.datos.length, 1);
});

test('crear', async () => {
  const creado = await crear();
  assert.equal(typeof creado.id, 'number');
});

test('obtener', async () => {
  const creado = await crear();
  const res = await api.get(`${URL}${creado.id}/`);
  assert.equal(res.status, 200);
  assert.equal(res.datos.id, creado.id);
});

test('actualizar', async () => {
  const creado = await crear();
  const res = await api.put(`${URL}${creado.id}/`, DATOS_MODIFICADOS);
  assert.equal(res.status, 200, JSON.stringify(res.datos));
  @@verificacion@@
});

test('eliminar', async () => {
  const creado = await crear();
  assert.equal((await api.delete(`${URL}${creado.id}/`)).status, 204);
  assert.equal((await api.get(`${URL}${creado.id}/`)).status, 404);
});
