/** Tests de la API de @@titulo@@. Ejecutalos con: npm test */
import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';
import { api, prisma } from './api.js';

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
  const respuesta = await api.post(URL, DATOS);
  assert.equal(respuesta.status, 201, JSON.stringify(respuesta.datos));
  return respuesta.datos;
}

test('listar', async () => {
  await crear();
  const respuesta = await api.get(URL);
  assert.equal(respuesta.status, 200);
  // Sin paginación, la respuesta es directamente una lista.
  assert.equal(respuesta.datos.length, 1);
});

test('crear', async () => {
  const creado = await crear();
  assert.equal(typeof creado.id, 'number');
});

test('obtener', async () => {
  const creado = await crear();
  const respuesta = await api.get(`${URL}${creado.id}/`);
  assert.equal(respuesta.status, 200);
  assert.equal(respuesta.datos.id, creado.id);
});

test('actualizar', async () => {
  const creado = await crear();
  const respuesta = await api.put(`${URL}${creado.id}/`, DATOS_MODIFICADOS);
  assert.equal(respuesta.status, 200, JSON.stringify(respuesta.datos));
  @@verificacion@@
});

test('eliminar', async () => {
  const creado = await crear();
  assert.equal((await api.delete(`${URL}${creado.id}/`)).status, 204);
  assert.equal((await api.get(`${URL}${creado.id}/`)).status, 404);
});
