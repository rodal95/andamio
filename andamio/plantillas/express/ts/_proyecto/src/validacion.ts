/**
 * Validación de los datos que llegan a la API (con Zod), con los mismos mensajes en
 * español que Django REST Framework. Cada recurso arma su esquema con estas funciones:
 *
 *   const campos = { nombre: texto(), precio: decimal(), stock: entero() };
 */
import { z } from 'zod';

/** El mensaje cuando falta el campo, cuando llega null o cuando el dato no sirve. */
function mensajes(invalido: string) {
  return {
    error: (problema: { input?: unknown }) => {
      if (problema.input === undefined) return 'Este campo es requerido.';
      if (problema.input === null) return 'Este campo no puede ser nulo.';
      return invalido;
    },
  };
}

// Los números y los sí/no también se aceptan como texto ("10", "true"): así llegan
// en los filtros de la lista (?stock=10&activo=true).
const aNumero = (valor: unknown) =>
  typeof valor === 'string' && valor.trim() !== '' && !Number.isNaN(Number(valor)) ? Number(valor) : valor;
const aBooleano = (valor: unknown) => (valor === 'true' ? true : valor === 'false' ? false : valor);

/** Texto corto (hasta 200 caracteres), no vacío. */
export const texto = (maximo = 200) =>
  z
    .string(mensajes('Introduzca un texto válido.'))
    .trim()
    .min(1, 'Este campo no puede estar en blanco.')
    .max(maximo, `Asegúrese de que este campo no tenga más de ${maximo} caracteres.`);

/** Texto largo, no vacío. */
export const textoLargo = () =>
  z.string(mensajes('Introduzca un texto válido.')).trim().min(1, 'Este campo no puede estar en blanco.');

/** Correo electrónico. */
export const correo = () =>
  z
    .email(mensajes('Introduzca una dirección de correo electrónico válida.'))
    .max(254, 'Asegúrese de que este campo no tenga más de 254 caracteres.');

/** Número entero. */
export const entero = () =>
  z.preprocess(aNumero, z.int(mensajes('Introduzca un número entero válido.'))).meta({ type: 'integer' });

/** Número con decimales. */
export const numero = () => z.preprocess(aNumero, z.number(mensajes('Introduzca un número válido.'))).meta({ type: 'number' });

/** Número con decimales exactos (precios): hasta `digitos` cifras, `decimales` después de la coma. */
export const decimal = (digitos = 10, decimales = 2) =>
  z
    .preprocess(
      aNumero,
      z.number(mensajes('Introduzca un número válido.')).superRefine((valor, ctx) => {
        const [parteEntera, parteDecimal = ''] = Math.abs(valor).toString().split('.');
        const enteros = parteEntera === '0' ? 0 : parteEntera.length;
        if (enteros + parteDecimal.length > digitos) {
          ctx.addIssue({ code: 'custom', message: `Asegúrese de que no haya más de ${digitos} dígitos en total.` });
        } else if (parteDecimal.length > decimales) {
          ctx.addIssue({ code: 'custom', message: `Asegúrese de que no haya más de ${decimales} decimales.` });
        } else if (enteros > digitos - decimales) {
          ctx.addIssue({
            code: 'custom',
            message: `Asegúrese de que no haya más de ${digitos - decimales} dígitos antes del punto decimal.`,
          });
        }
      }),
    )
    .meta({ type: 'number' });

/** Verdadero o falso. */
export const booleano = () =>
  z.preprocess(aBooleano, z.boolean(mensajes('Tiene que ser verdadero o falso.'))).meta({ type: 'boolean' });

/** Fecha "2026-11-19" (se guarda a las 00:00 UTC). */
export const fecha = () =>
  z.iso.date(mensajes('Fecha con formato erróneo. Use AAAA-MM-DD.')).transform((valor) => new Date(valor));

/**
 * Fecha y hora: "2026-11-19T10:30:00-03:00", "2026-11-19T10:30:00Z" o "2026-11-19T10:30".
 * Sin zona horaria (como la manda un <input type="datetime-local">) es hora local.
 */
export const fechaHora = () =>
  z.iso
    .datetime({ local: true, offset: true, ...mensajes('Fecha y hora con formato erróneo.') })
    .transform((valor) => new Date(valor));
