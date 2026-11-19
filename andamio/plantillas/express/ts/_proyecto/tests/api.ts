/**
 * Ayuda para los tests: arranca la API en un puerto libre, con otra base de datos
 * (test.db, que npm test crea vacía antes de empezar). Así no toca tus datos.
 */
import type { AddressInfo } from 'node:net';
import { after } from 'node:test';

process.env.DATABASE_URL = 'file:./test.db'; // antes de cargar la app
const { DATABASE_URL } = await import('../src/config.ts');
if (DATABASE_URL !== 'file:./test.db') {
  // Por seguridad: los tests borran los datos de las tablas.
  throw new Error(`Los tests tienen que usar test.db, no ${DATABASE_URL}`);
}
const { app } = await import('../src/app.ts');
export const { prisma } = await import('../src/db.ts');

const servidor = app.listen(0);
await new Promise((listo) => servidor.once('listening', listo));
const base = `http://127.0.0.1:${(servidor.address() as AddressInfo).port}`;

after(async () => {
  servidor.close();
  await prisma.$disconnect();
});

async function pedir(metodo: string, ruta: string, datos?: unknown) {
  const respuesta = await fetch(base + ruta, {
    method: metodo,
    headers: datos === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: datos === undefined ? undefined : JSON.stringify(datos),
  });
  const texto = await respuesta.text();
  const cuerpo: any = texto ? JSON.parse(texto) : null;
  return { status: respuesta.status, datos: cuerpo };
}

/** api.get('/api/productos/') -> { status: 200, datos: [...] } */
export const api = {
  get: (ruta: string) => pedir('GET', ruta),
  post: (ruta: string, datos: unknown) => pedir('POST', ruta, datos),
  put: (ruta: string, datos: unknown) => pedir('PUT', ruta, datos),
  patch: (ruta: string, datos: unknown) => pedir('PATCH', ruta, datos),
  delete: (ruta: string) => pedir('DELETE', ruta),
};
