/**
 * Errores de la API con el mismo formato que Django REST Framework:
 *   400 {"campo": ["mensaje"]}    datos inválidos
 *   404 {"detail": "No encontrado."}
 * Así los servicios y formularios de React y React Native funcionan igual.
 */

/** Datos inválidos: se responde 400 con los errores de cada campo. */
export class ErrorDeValidacion extends Error {
  /** @param {Record<string, string[]>} errores */
  constructor(errores) {
    super('Datos inválidos');
    this.errores = errores;
  }
}

/** El registro (o la ruta) no existe: se responde 404. */
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

/** Para las rutas que no existen. */
export function rutaNoEncontrada(req, res) {
  res.status(404).json({ detail: 'No encontrado.' });
}

/** Express llama a esta función cuando una ruta lanza un error (tiene que recibir 4 parámetros). */
export function manejarErrores(error, req, res, next) {
  if (error instanceof ErrorDeValidacion) {
    res.status(400).json(error.errores);
  } else if (error instanceof NoEncontrado) {
    res.status(404).json({ detail: 'No encontrado.' });
  } else if (error instanceof SyntaxError && 'body' in error) {
    // express.json() no pudo leer el JSON del pedido.
    res.status(400).json({ general: ['Los datos enviados no son un JSON válido.'] });
  } else {
    console.error(error);
    res.status(500).json({ detail: 'Error del servidor. Mirá la terminal donde corre la API.' });
  }
}
