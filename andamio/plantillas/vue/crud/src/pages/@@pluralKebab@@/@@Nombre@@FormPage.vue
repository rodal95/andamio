<script setup>
// Formulario para crear (ruta /@@pluralKebab@@/nuevo) o editar (ruta /@@pluralKebab@@/:id/editar).
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ErrorApi } from '@/services/http';
import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';

const route = useRoute();
const router = useRouter();
const editando = route.params.id !== undefined;
const id = Number(route.params.id);

// Los datos del formulario: v-model los mantiene sincronizados con cada campo.
const datos = ref({
  @@valores_vacios@@
});
// Errores de validación que devuelve la API, por campo: { nombre: ['Este campo...'] }
const errores = ref({});

onMounted(async () => {
  if (editando) {
    const registro = await @@nombreCamel@@Service.obtener(id);
    datos.value = {
      @@campos_copiar@@
    };
  }
});

async function guardar() {
  try {
    const guardado = editando
      ? await @@nombreCamel@@Service.actualizar(id, datos.value)
      : await @@nombreCamel@@Service.crear(datos.value);
    router.push(`/@@pluralKebab@@/${guardado.id}`);
  } catch (e) {
    if (e instanceof ErrorApi && e.estado === 400) errores.value = e.detalle;
    else errores.value = { general: [e instanceof Error ? e.message : String(e)] };
  }
}
</script>

<template>
  <h1>{{ editando ? 'Editar' : 'Agregar' }}: @@nombreTitulo@@</h1>
  <!-- .prevent: que el navegador no recargue la página al enviar -->
  <form class="formulario" @submit.prevent="guardar">
    @@campos_formulario@@
    <p v-if="errores.general" class="error">{{ errores.general.join(' ') }}</p>
    <div class="acciones">
      <button type="submit" class="boton">Guardar</button>
      <button type="button" class="boton boton--borde" @click="router.back()">Cancelar</button>
    </div>
  </form>
</template>
