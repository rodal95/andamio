<script setup>
import { ref } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { ErrorApi } from '../services/http';
import { aDondeVolver, registrarse } from '../sesion/sesion';

const ruta = useRoute();
const router = useRouter();
// guía: repetir no va a la API: es para controlar acá que la contraseña se escribió bien.
const datos = ref({ username: '', email: '', password: '', repetir: '' });
/** @type {import('vue').Ref<Record<string, string[]>>} */
const errores = ref({});
const enviando = ref(false);

async function enviar() {
  // TODO(logica): más reglas antes de enviar (la API también valida: usuario repetido, contraseña corta o muy común).
  if (datos.value.password !== datos.value.repetir) {
    errores.value = { repetir: ['Las contraseñas no coinciden.'] };
    return;
  }
  errores.value = {};
  enviando.value = true;
  try {
    const { username, email, password } = datos.value;
    // guía: registrarse() crea el usuario y también ingresa.
    await registrarse({ username, email, password });
    router.replace(aDondeVolver(ruta.query.desde));
  } catch (e) {
    // guía: 400: la API dice qué está mal en cada campo (ej.: "Ya existe un usuario con este nombre.").
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
  <h1>Crear una cuenta</h1>
  <form class="formulario" @submit.prevent="enviar">
    <label class="campo">
      Usuario
      <input v-model="datos.username" autocomplete="username" required />
      <small v-if="errores.username" class="error">{{ errores.username.join(' ') }}</small>
    </label>
    <label class="campo">
      Email
      <input v-model="datos.email" type="email" autocomplete="email" />
      <small v-if="errores.email" class="error">{{ errores.email.join(' ') }}</small>
    </label>
    <label class="campo">
      Contraseña
      <input v-model="datos.password" type="password" autocomplete="new-password" required />
      <small v-if="errores.password" class="error">{{ errores.password.join(' ') }}</small>
    </label>
    <label class="campo">
      Repetí la contraseña
      <input v-model="datos.repetir" type="password" autocomplete="new-password" required />
      <small v-if="errores.repetir" class="error">{{ errores.repetir.join(' ') }}</small>
    </label>
    <p v-if="errores.general" class="error">{{ errores.general.join(' ') }}</p>
    <div>
      <button type="submit" class="boton" :disabled="enviando">{{ enviando ? 'Creando la cuenta…' : 'Crear la cuenta' }}</button>
    </div>
  </form>
  <p>¿Ya tenés cuenta? <RouterLink :to="{ path: '/ingresar', query: ruta.query }">Ingresá</RouterLink></p>
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
