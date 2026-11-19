<script setup>
// Cada tarjeta lleva al detalle del producto: una página del crud (/productos/3).
import { RouterLink } from 'vue-router';
import Tarjeta from '@/components/Tarjeta.vue';
import { useProductos } from '@/composables/useProductos';

const { productos, cargando, error } = useProductos();
</script>

<template>
  <h1>Catálogo</h1>
  <p v-if="cargando">Cargando...</p>
  <p v-else-if="error" class="error">{{ error }}</p>
  <div v-else class="tarjetas">
    <RouterLink v-for="producto in productos" :key="producto.id" :to="`/productos/${producto.id}`">
      <Tarjeta :titulo="producto.nombre">$ {{ producto.precio }}</Tarjeta>
    </RouterLink>
  </div>
</template>

<style scoped>
.tarjetas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

a {
  color: inherit;
  text-decoration: none;
}
</style>
