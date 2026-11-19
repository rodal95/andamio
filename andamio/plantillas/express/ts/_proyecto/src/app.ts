/**
 * La API de @@proyectoTitulo@@ con Express.
 *
 * Para ejecutarla:            npm run dev
 * Documentación interactiva:  http://localhost:8000/docs
 */
import cors from 'cors';
import express from 'express';
import swaggerUi from 'swagger-ui-express';
import { CORS_ALLOWED_ORIGINS } from './config.ts';
import { crearDocumentacion, type DocsRecurso } from './docs.ts';
import { manejarErrores, rutaNoEncontrada } from './errores.ts';
// Cada recurso tiene su router. andamio agrega los import solo.
// --- andamio:imports (no borrar esta línea) ---

export const app = express();
app.disable('x-powered-by'); // no anunciar en cada respuesta que la API usa Express

// Qué páginas web pueden usar la API (React con Vite, Next.js, Expo web). Se configura en el .env.
app.use(cors({ origin: CORS_ALLOWED_ORIGINS }));
// Lee el JSON que llega en los pedidos (POST, PUT, PATCH) y lo deja en req.body.
app.use(express.json());

// Rutas de cada recurso (andamio agrega una línea por cada uno):
// --- andamio:rutas (no borrar esta línea) ---

// Documentación interactiva (Swagger) en /docs, con los recursos de esta lista:
const recursos: DocsRecurso[] = [
  // --- andamio:docs (no borrar esta línea) ---
];
app.use('/docs', swaggerUi.serve, swaggerUi.setup(crearDocumentacion('API de @@proyectoTitulo@@', recursos)));
app.get('/api/', (req, res) => res.redirect('/docs'));

// Al final: rutas que no existen y errores (con el formato de Django REST Framework).
app.use(rutaNoEncontrada);
app.use(manejarErrores);
