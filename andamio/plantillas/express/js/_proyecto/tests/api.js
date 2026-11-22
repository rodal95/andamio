/**
 * Ayuda para los tests: arranca la API en un puerto libre, con otra base de datos
 * (TEST_DATABASE_URL del .env, o test.db, que npm test prepara antes de empezar).
 * Así no toca tus datos.
 */
import { after } from 'node:test';

try {
  process.loadEnvFile(); // TEST_DATABASE_URL: la base de los tests
} catch {
  // sin .env
}
process.env.DATABASE_URL = process.env.TEST_DATABASE_URL || 'file:./test.db'; // antes de cargar la app
process.env.SECRET_KEY ||= 'clave-solo-para-los-tests'; // los tests no necesitan la del .env
const { DATABASE_URL } = await import('../src/config.js');
if (DATABASE_URL !== (process.env.TEST_DATABASE_URL || 'file:./test.db')) {
  // Por seguridad: los tests borran los datos de las tablas.
  throw new Error(`Los tests tienen que usar su propia base (TEST_DATABASE_URL o test.db), no ${DATABASE_URL}`);
}
const { app } = await import('../src/app.js');
export const { prisma } = await import('../src/db.js');

const servidor = app.listen(0);
await new Promise((listo) => servidor.once('listening', listo));
const base = `http://127.0.0.1:${servidor.address().port}`;

after(async () => {
  servidor.close();
  await prisma.$disconnect();
});

/** @type {string | null} */
let token = null;

/**
 * Desde acá, cada pedido manda este token (Authorization: Bearer ...); null: sin token. Para el login.
 * @param {string | null} nuevo
 */
export function usarToken(nuevo) {
  token = nuevo;
}

async function pedir(metodo, ruta, datos) {
  /** @type {Record<string, string>} */
  const encabezados = {};
  if (datos !== undefined) encabezados['Content-Type'] = 'application/json';
  if (token) encabezados.Authorization = `Bearer ${token}`;
  const respuesta = await fetch(base + ruta, {
    method: metodo,
    headers: encabezados,
    body: datos === undefined ? undefined : JSON.stringify(datos),
  });
  const texto = await respuesta.text();
  return { status: respuesta.status, datos: texto ? JSON.parse(texto) : null };
}

/** api.get('/api/productos/') -> { status: 200, datos: [...] } */
export const api = {
  get: (ruta) => pedir('GET', ruta),
  post: (ruta, datos) => pedir('POST', ruta, datos),
  put: (ruta, datos) => pedir('PUT', ruta, datos),
  patch: (ruta, datos) => pedir('PATCH', ruta, datos),
  delete: (ruta) => pedir('DELETE', ruta),
};
