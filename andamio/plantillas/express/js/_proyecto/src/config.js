/**
 * Configuración del proyecto, leída del archivo .env (como settings.py en Django).
 */

try {
  process.loadEnvFile(); // carga las variables del .env en process.env
} catch {
  // Sin .env: se usan los valores por defecto de abajo.
}

/**
 * Lee una variable con valores separados por coma: "a,b,c" -> ["a", "b", "c"].
 * @param {string} nombre
 * @param {string} defecto
 * @returns {string[]}
 */
function leerLista(nombre, defecto) {
  return (process.env[nombre] ?? defecto)
    .split(',')
    .map((valor) => valor.trim())
    .filter(Boolean);
}

// Puerto de la API: 8000, como Django y FastAPI.
export const PUERTO = Number(process.env.PORT || 8000);

// Base de datos: por defecto, el archivo datos.db.
export const DATABASE_URL = process.env.DATABASE_URL || 'file:./datos.db';

// Páginas web que pueden usar la API (React con Vite, Expo web).
export const CORS_ALLOWED_ORIGINS = leerLista(
  'CORS_ALLOWED_ORIGINS',
  'http://localhost:5173,http://127.0.0.1:5173,http://localhost:8081',
);

// Zona horaria de las fechas con hora (como TIME_ZONE en Django). Se aplica a todo
// el programa: "2026-11-19T10:30" es hora de acá, y las fechas salen en hora de acá.
export const ZONA_HORARIA = process.env.ZONA_HORARIA || 'America/Argentina/Salta';
process.env.TZ = ZONA_HORARIA;
