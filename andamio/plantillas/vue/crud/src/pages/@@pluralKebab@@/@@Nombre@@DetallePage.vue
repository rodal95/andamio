<script setup>
// Detalle de un registro (ruta /@@pluralKebab@@/:id), con Editar y Eliminar.
import { onMounted, ref } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';

const route = useRoute(); // la ruta actual: route.params.id es el :id de la dirección
const router = useRouter(); // para ir a otra página desde el código
const id = Number(route.params.id);
const @@nombreCamel@@ = ref(null);
const error = ref('');

onMounted(async () => {
  try {
    @@nombreCamel@@.value = await @@nombreCamel@@Service.obtener(id);
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  }
});

async function eliminar() {
  if (!confirm('¿Eliminar este registro?')) return;
  await @@nombreCamel@@Service.eliminar(id);
  router.push('/@@pluralKebab@@');
}
</script>

<template>
  <p v-if="error" class="error">{{ error }}</p>
  <template v-else-if="@@nombreCamel@@">
    <h1>@@nombreTitulo@@ {{ @@nombreCamel@@.id }}</h1>
    <dl>
      @@campos_detalle@@
    </dl>
    <div class="acciones">
      <RouterLink class="boton" :to="`/@@pluralKebab@@/${id}/editar`">Editar</RouterLink>
      <button type="button" class="boton boton--peligro" @click="eliminar">Eliminar</button>
      <RouterLink to="/@@pluralKebab@@">Volver a la lista</RouterLink>
    </div>
  </template>
  <p v-else>Cargando...</p>
</template>
