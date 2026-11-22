<script setup>
// En el menú: Ingresar@@y_registrarse@@, o quién ingresó y Salir.
import { RouterLink, useRouter } from 'vue-router';
import { salir, sesion } from '../sesion/sesion';

const router = useRouter();

function cerrarSesion() {
  salir();
  // A la página de inicio: si la de ahora pedía ingresar, ya no se puede ver.
  router.push('/');
}
</script>

<template>
  <span v-if="!sesion.cargando" class="sesion">
    <template v-if="sesion.usuario">
      <!-- guía: Los enlaces a las páginas protegidas (--protegido): solo se ven si alguien ingresó. -->
      <!-- --- andamio:enlaces_sesion (no borrar esta línea) --- -->
      <span>{{ sesion.usuario.username }}</span>
      <button type="button" class="boton boton--borde" @click="cerrarSesion">Salir</button>
    </template>
    <template v-else>
      <RouterLink to="/ingresar">Ingresar</RouterLink>
      @@enlace_registro@@
    </template>
  </span>
</template>

<style scoped>
/* guía: Al final del menú (order: 1), a la derecha (margin-left: auto). */
.sesion {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-left: auto;
  order: 1;
}
</style>
