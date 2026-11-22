<script setup>
// El marco de la aplicación: el menú arriba, la página de la ruta en el medio y el pie abajo.
// Una ruta con meta: { sinMenu: true } se ve sola (ej.: /ingresar, si el login es obligatorio).
import { RouterView, useRoute } from 'vue-router';
import TheFooter from './components/TheFooter.vue';
import TheNavbar from './components/TheNavbar.vue';

const ruta = useRoute();
</script>

<template>
  <TheNavbar v-if="!ruta.meta.sinMenu" />
  <main class="contenido">
    <RouterView />
  </main>
  <TheFooter v-if="!ruta.meta.sinMenu" />
</template>
