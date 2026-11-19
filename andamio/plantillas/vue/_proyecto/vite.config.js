import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';

// Configuración de Vite: https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    // '@/components/Tarjeta.vue' es lo mismo que 'src/components/Tarjeta.vue', desde cualquier carpeta.
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
});
