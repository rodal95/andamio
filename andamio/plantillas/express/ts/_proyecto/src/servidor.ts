/**
 * Arranca la API:  npm run dev  (se reinicia sola cada vez que guardás un cambio)
 */
import { app } from './app.ts';
import { PUERTO } from './config.ts';

app.listen(PUERTO, () => {
  console.log(`API en http://localhost:${PUERTO}/api/`);
  console.log(`Documentación interactiva: http://localhost:${PUERTO}/docs`);
});
