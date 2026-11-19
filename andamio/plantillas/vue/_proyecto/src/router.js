import { createRouter, createWebHistory } from 'vue-router';
import InicioPage from './pages/InicioPage.vue';
// --- andamio:imports (no borrar esta línea) ---

// Cada ruta asocia una dirección con una página. andamio agrega acá las que generes.
const routes = [
  { path: '/', component: InicioPage },
  // --- andamio:rutas (no borrar esta línea) ---
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
