/**
 * Errores de la API con el mismo formato que Django REST Framework:
 *   400 {"campo": ["mensaje"]}    datos inválidos
 *   404 {"detail": "No encontrado."}
 * Así los servicios y formularios funcionan igual con cualquiera de las APIs.
 */
/** Datos inválidos: se responde 400 con los errores de cada campo. */
export class ErrorDeValidacion extends Error {
  /** @param {Record<string, string[]>} errores */
  constructor(errores) {
    super('Datos inválidos');
    this.errores = errores;
  }
}

/** El registro no existe: se responde 404. */
export class NoEncontrado extends Error {
  constructor() {
    super('No encontrado.');
  }
}

/**
 * Valida los datos con un esquema de Zod. Si no sirven, lanza ErrorDeValidacion.
 * @param {import('zod').ZodType} esquema
 * @param {unknown} datos
 */
export function validar(esquema, datos) {
  if (datos !== undefined && (typeof datos !== 'object' || datos === null || Array.isArray(datos))) {
    throw new ErrorDeValidacion({ general: ['Los datos tienen que ser un objeto JSON: {"campo": valor}.'] });
  }
  const resultado = esquema.safeParse(datos ?? {});
  if (resultado.success) return resultado.data;
  /** @type {Record<string, string[]>} */
  const errores = {};
  for (const problema of resultado.error.issues) {
    const campo = typeof problema.path[0] === 'string' ? problema.path[0] : 'general';
    (errores[campo] ??= []).push(problema.message);
  }
  throw new ErrorDeValidacion(errores);
}

/**
 * Lee el JSON del pedido (POST, PUT, PATCH). Sin cuerpo, devuelve undefined.
 * @param {Request} request
 */
export async function leerJson(request) {
  const texto = await request.text();
  if (!texto.trim()) return undefined;
  try {
    return JSON.parse(texto);
  } catch {
    throw new ErrorDeValidacion({ general: ['Los datos enviados no son un JSON válido.'] });
  }
}

/**
 * Ejecuta lo que hace una ruta y, si lanza un error, lo convierte en la respuesta que
 * corresponde (400, 404 o 500). Se usa en cada Route Handler:
 *   export async function GET(request) {
 *     return responder(async () => Response.json(...));
 *   }
 *
 * @param {() => Promise<Response>} accion
 */
export async function responder(accion) {
  try {
    return await accion();
  } catch (error) {
    if (error instanceof ErrorDeValidacion) return Response.json(error.errores, { status: 400 });
    if (error instanceof NoEncontrado) return Response.json({ detail: 'No encontrado.' }, { status: 404 });
    console.error(error);
    return Response.json({ detail: 'Error del servidor. Mirá la terminal donde corre npm run dev.' }, { status: 500 });
  }
}
