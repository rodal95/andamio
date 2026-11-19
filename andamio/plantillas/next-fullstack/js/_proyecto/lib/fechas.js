/**
 * Cómo salen las fechas en el JSON, igual que en la API de Django:
 *   fecha:          "2026-11-19"
 *   fecha y hora:   "2026-11-19T10:30:00-03:00"  (hora local, con su zona)
 */

// Zona horaria de las fechas con hora (como TIME_ZONE en Django). Se configura en el .env.
export const ZONA_HORARIA = process.env.ZONA_HORARIA || 'America/Argentina/Salta';

const dos = (numero) => String(numero).padStart(2, '0');

/**
 * Cuántos minutos está corrida la zona horaria respecto de UTC en esa fecha (Argentina: -180).
 * @param {Date} fecha
 */
function minutosDeZona(fecha) {
  const zona = new Intl.DateTimeFormat('en-US', { timeZone: ZONA_HORARIA, timeZoneName: 'longOffset' })
    .formatToParts(fecha)
    .find((parte) => parte.type === 'timeZoneName')?.value; // "GMT-03:00" (o "GMT" si es UTC)
  const partes = zona?.match(/([+-])(\d{2}):(\d{2})/);
  return partes ? (partes[1] === '-' ? -1 : 1) * (Number(partes[2]) * 60 + Number(partes[3])) : 0;
}

/**
 * Fecha y hora en hora local, con su zona horaria: "2026-11-19T10:30:00-03:00".
 * @param {Date} fecha
 */
export function jsonFechaHora(fecha) {
  const minutos = minutosDeZona(fecha);
  const local = new Date(fecha.getTime() + minutos * 60_000).toISOString(); // "2026-11-19T10:30:00.000Z"
  const zona = `${minutos < 0 ? '-' : '+'}${dos(Math.floor(Math.abs(minutos) / 60))}:${dos(Math.abs(minutos) % 60)}`;
  return local.slice(0, 19) + (local.slice(19, 23) === '.000' ? '' : local.slice(19, 23)) + zona;
}

/**
 * Solo la fecha: "2026-11-19". Las fechas sin hora se guardan a las 00:00 UTC.
 * @param {Date} fecha
 */
export function jsonFecha(fecha) {
  return fecha.toISOString().slice(0, 10);
}

/**
 * Lee una fecha y hora. Sin zona horaria ("2026-11-19T10:30", como la manda un
 * <input type="datetime-local">) es hora local; con zona ("...Z", "...-03:00"), es esa.
 * @param {string} texto
 */
export function leerFechaHora(texto) {
  if (/(Z|[+-]\d{2}:?\d{2})$/i.test(texto)) return new Date(texto);
  const comoUtc = new Date(`${texto}Z`);
  return new Date(comoUtc.getTime() - minutosDeZona(comoUtc) * 60_000);
}
