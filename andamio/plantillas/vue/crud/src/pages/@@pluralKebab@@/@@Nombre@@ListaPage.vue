<script setup>
// Lista de @@titulo@@ (ruta /@@pluralKebab@@).
import { onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';

const lista = ref([]);
const cargando = ref(true);
const error = ref('');

// onMounted se ejecuta una vez, cuando la página aparece: ahí se piden los datos.
onMounted(async () => {
  try {
    lista.value = await @@nombreCamel@@Service.listar();
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    cargando.value = false;
  }
});
</script>

<template>
  <h1>@@titulo@@</h1>
  <RouterLink class="boton" to="/@@pluralKebab@@/nuevo">Agregar</RouterLink>

  <p v-if="cargando">Cargando...</p>
  <p v-else-if="error" class="error">{{ error }}</p>
  <p v-else-if="lista.length === 0">Todavía no hay @@verbose_plural@@.</p>
  <ul v-else>
    <li v-for="item in lista" :key="item.id">
      <RouterLink :to="`/@@pluralKebab@@/${item.id}`">{{ @@texto_item@@ }}</RouterLink>
    </li>
  </ul>
</template>
