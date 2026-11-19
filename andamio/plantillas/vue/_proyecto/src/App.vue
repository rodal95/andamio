<script setup>
// El marco de la aplicación: el menú arriba y, abajo, la página de la ruta actual.
import { RouterLink, RouterView } from 'vue-router';
</script>

<template>
  <header class="barra">
    <nav>
      <RouterLink to="/">Inicio</RouterLink>
      <!-- --- andamio:enlaces (no borrar esta línea) --- -->
    </nav>
  </header>
  <main class="contenido">
    <RouterView />
  </main>
</template>
