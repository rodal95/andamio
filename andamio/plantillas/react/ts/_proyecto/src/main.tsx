import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
// --- andamio:estilos (no borrar esta línea) ---
import App from './App';

// Punto de entrada: monta el componente App dentro de <div id="root"> (index.html).
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
