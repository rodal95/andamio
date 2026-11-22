<script setup>
import { ref } from 'vue';
import { @@router_ingresar@@ } from 'vue-router';
import { ErrorApi } from '../services/http';
import { ingresar } from '../sesion/sesion';

const ruta = useRoute();
const router = useRouter();
const datos = ref({ username: '', password: '' });
/** @type {import('vue').Ref<Record<string, string[]>>} */
const errores = ref({});
const enviando = ref(false);

async function enviar() {
  errores.value = {};
  enviando.value = true;
  try {
    await ingresar(datos.value);
    // guía: Si llegó desde una página protegida, vuelve ahí (la dirección está en ?desde=).
    const desde = ruta.query.desde;
    router.replace(typeof desde === 'string' ? desde : '/');
  } catch (e) {
    // guía: Usuario o contraseña incorrectos: la API responde 401 y lo explica (va en general).
    if (e instanceof ErrorApi && e.estado === 400) {
      errores.value = /** @type {Record<string, string[]>} */ (e.detalle);
    } else {
      errores.value = { general: [e instanceof Error ? e.message : String(e)] };
    }
  } finally {
    enviando.value = false;
  }
}
</script>

<template>
  <h1>Ingresar</h1>
  <form class="formulario" @submit.prevent="enviar">
    <label class="campo">
      Usuario
      <input v-model="datos.username" autocomplete="username" required />
      <small v-if="errores.username" class="error">{{ errores.username.join(' ') }}</small>
    </label>
    <label class="campo">
      Contraseña
      <input v-model="datos.password" type="password" autocomplete="current-password" required />
      <small v-if="errores.password" class="error">{{ errores.password.join(' ') }}</small>
    </label>
    <p v-if="errores.general" class="error">{{ errores.general.join(' ') }}</p>
    <div>
      <button type="submit" class="boton" :disabled="enviando">{{ enviando ? 'Ingresando…' : 'Ingresar' }}</button>
    </div>
  </form>
  @@pie_ingresar@@
</template>

<style scoped>
.formulario {
  display: grid;
  gap: 14px;
  max-width: 360px;
}

.campo {
  display: grid;
  gap: 4px;
  font-weight: 600;
}

.campo input {
  font: inherit;
  font-weight: normal;
  padding: 6px 8px;
}

.error {
  color: #b42318;
  font-weight: normal;
}
</style>
