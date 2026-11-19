<script setup>
// La página pide los productos a la API con el servicio y los muestra en una lista.
import { onMounted, ref } from 'vue';
import { productoService } from '@/services/productoService';

const productos = ref([]);
const error = ref('');

// onMounted se ejecuta una vez, cuando la página aparece: ahí se piden los datos.
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
  <ul v-else>
    <li v-for="producto in productos" :key="producto.id">{{ producto.nombre }}: $ {{ producto.precio }}</li>
  </ul>
</template>
