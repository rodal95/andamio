/**
 * Ayuda para los tests: llama a las funciones de app/api/ (GET, POST, ...) como lo hace
 * Next.js, sin levantar el servidor, con otra base de datos (TEST_DATABASE_URL del .env, o test.db,
 * que npm test prepara antes de empezar). Así no toca tus datos.
 *
 *   const { api, prisma } = await abrir('productos');
 *   const respuesta = await api.get('/api/productos/');   // { status: 200, datos: [...] }
 */
// Los tests firman tokens: con el .env, o una clave solo para los tests si no está.
try {
  process.loadEnvFile();
} catch {
  // sin .env
}
process.env.SECRET_KEY ||= 'clave-solo-para-los-tests';
process.env.DATABASE_URL = process.env.TEST_DATABASE_URL || 'file:./test.db'; // antes de cargar la conexión
const { prisma } = await import('../lib/db.js');

// Con el login (recurso --protegido): el token que se manda en cada pedido.
/** @type {string | null} */
let token = null;

/**
 * Desde acá, cada pedido manda Authorization: Bearer <token> (null: sin token).
 * @param {string | null} nuevo
 */
export function usarToken(nuevo) {
  token = nuevo;
}

/** @param {string} recurso */
export async function abrir(recurso) {
  const lista = await import(`../app/api/${recurso}/route.js`);
  const detalle = await import(`../app/api/${recurso}/[id]/route.js`);

  async function pedir(metodo, ruta, datos) {
    // "/api/productos/" va a route.ts; "/api/productos/3/", a [id]/route.ts con id "3".
    const id = ruta.slice(`/api/${recurso}/`.length).replace(/\/$/, '');
    const funcion = (id ? detalle : lista)[metodo];
    if (!funcion) throw new Error(`No hay ${metodo} en app/api/${recurso}${id ? '/[id]' : ''}/route`);
    const request = new Request(`http://localhost${ruta}`, {
      method: metodo,
      headers: {
        ...(datos === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: datos === undefined ? undefined : JSON.stringify(datos),
    });
    const respuesta = await funcion(request, { params: Promise.resolve({ id }) });
    const texto = await respuesta.text();
    return { status: respuesta.status, datos: texto ? JSON.parse(texto) : null };
  }

  const api = {
    get: (ruta) => pedir('GET', ruta),
    post: (ruta, datos) => pedir('POST', ruta, datos),
    put: (ruta, datos) => pedir('PUT', ruta, datos),
    patch: (ruta, datos) => pedir('PATCH', ruta, datos),
    delete: (ruta) => pedir('DELETE', ruta),
  };
  return { api, prisma };
}
