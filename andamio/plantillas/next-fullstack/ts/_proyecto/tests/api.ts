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
const { prisma } = await import('../lib/db');

type Contexto = { params: Promise<{ id: string }> };
type Rutas = Record<string, ((request: Request, contexto: Contexto) => Promise<Response>) | undefined>;

// Con el login (recurso --protegido): el token que se manda en cada pedido.
let token: string | null = null;

/** Desde acá, cada pedido manda Authorization: Bearer <token> (null: sin token). */
export function usarToken(nuevo: string | null) {
  token = nuevo;
}

export async function abrir(recurso: string) {
  const lista: Rutas = await import(`../app/api/${recurso}/route`);
  const detalle: Rutas = await import(`../app/api/${recurso}/[id]/route`);

  async function pedir(metodo: string, ruta: string, datos?: unknown) {
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
    const cuerpo: any = texto ? JSON.parse(texto) : null;
    return { status: respuesta.status, datos: cuerpo };
  }

  const api = {
    get: (ruta: string) => pedir('GET', ruta),
    post: (ruta: string, datos: unknown) => pedir('POST', ruta, datos),
    put: (ruta: string, datos: unknown) => pedir('PUT', ruta, datos),
    patch: (ruta: string, datos: unknown) => pedir('PATCH', ruta, datos),
    delete: (ruta: string) => pedir('DELETE', ruta),
  };
  return { api, prisma };
}
