/**
 * Cómo salen las fechas en el JSON, igual que en la API de Django:
 *   fecha:          "2026-11-19"
 *   fecha y hora:   "2026-11-19T10:30:00-03:00"  (hora local, con su zona)
 */
import './config.ts'; // define la zona horaria (ZONA_HORARIA)

const dos = (numero: number) => String(numero).padStart(2, '0');

/** Fecha y hora en hora local, con su zona horaria: "2026-11-19T10:30:00-03:00". */
export function jsonFechaHora(fecha: Date): string {
  const minutos = -fecha.getTimezoneOffset();
  const zona = `${minutos < 0 ? '-' : '+'}${dos(Math.floor(Math.abs(minutos) / 60))}:${dos(Math.abs(minutos) % 60)}`;
  const milisegundos = fecha.getMilliseconds() ? `.${String(fecha.getMilliseconds()).padStart(3, '0')}` : '';
  return (
    `${fecha.getFullYear()}-${dos(fecha.getMonth() + 1)}-${dos(fecha.getDate())}` +
    `T${dos(fecha.getHours())}:${dos(fecha.getMinutes())}:${dos(fecha.getSeconds())}${milisegundos}${zona}`
  );
}

/** Solo la fecha: "2026-11-19". Las fechas sin hora se guardan a las 00:00 UTC. */
export function jsonFecha(fecha: Date): string {
  return fecha.toISOString().slice(0, 10);
}
