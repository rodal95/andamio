<script setup>
// Props: los datos que recibe de quien lo usa.  <@@Nombre@@ titulo="Yerba">$ 1500</@@Nombre@@>
defineProps({
  titulo: { type: String, default: '' },
});
</script>

<template>
  <article class="@@nombreKebab@@">
    <h3 v-if="titulo">{{ titulo }}</h3>
    <!-- Lo que se escribe entre <@@Nombre@@> y </@@Nombre@@> aparece en el slot. -->
    <slot />
  </article>
</template>

<!-- scoped: estos estilos solo afectan a este componente. -->
<style scoped>
.@@nombreKebab@@ {
  padding: 1rem;
  border: 1px solid var(--borde);
  border-radius: 8px;
  background: #fff;
}

h3 {
  margin: 0 0 0.25rem;
}
</style>
