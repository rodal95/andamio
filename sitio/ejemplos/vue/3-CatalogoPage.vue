<script setup>
// La lógica de pedir los datos quedó en el composable: la página solo muestra.
import Tarjeta from '@/components/Tarjeta.vue';
import { useProductos } from '@/composables/useProductos';

const { productos, cargando, error } = useProductos();
</script>

<template>
  <h1>Catálogo</h1>
  <p v-if="cargando">Cargando...</p>
  <p v-else-if="error" class="error">{{ error }}</p>
  <div v-else class="tarjetas">
    <Tarjeta v-for="producto in productos" :key="producto.id" :titulo="producto.nombre">
      $ {{ producto.precio }} ({{ producto.stock }} en stock)
    </Tarjeta>
  </div>
</template>

<style scoped>
.tarjetas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
</style>
