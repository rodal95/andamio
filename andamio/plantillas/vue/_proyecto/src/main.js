import { createApp } from 'vue';
import App from './App.vue';
import { router } from './router';
import './estilos.css';

// Crea la aplicación, le agrega el router y la muestra en <div id="app"> (index.html).
createApp(App).use(router).mount('#app');
