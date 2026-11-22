<script setup>
// El pie de todas las páginas (lo muestra App.vue).
const anio = new Date().getFullYear();
</script>

<template>
  <footer class="pie">
    <small>© {{ anio }} @@proyectoTitulo@@</small>
  </footer>
</template>
