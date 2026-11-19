<script setup>
// Cada producto se muestra con el componente Tarjeta.
import { onMounted, ref } from 'vue';
import Tarjeta from '@/components/Tarjeta.vue';
import { productoService } from '@/services/productoService';

const productos = ref([]);
const error = ref('');

onMounted(async () => {
  try {
    productos.value = await productoService.listar();
  } catch (e) {
    error.value = e.message;
  }
});
</script>

<template>
  <h1>Catálogo</h1>
  <p v-if="error" class="error">{{ error }}</p>
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
