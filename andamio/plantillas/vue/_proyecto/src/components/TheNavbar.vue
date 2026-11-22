<script setup>
// El menú de todas las páginas (lo muestra App.vue). andamio agrega acá un enlace por cada
// página que generes. "The" adelante: hay uno solo en la app (guía de estilo de Vue).
import { RouterLink } from 'vue-router';
// --- andamio:imports_navbar (no borrar esta línea) ---
</script>

<template>
  <header class="barra">
    <nav>
      <RouterLink to="/">Inicio</RouterLink>
      <!-- --- andamio:enlaces (no borrar esta línea) --- -->
    </nav>
  </header>
</template>
