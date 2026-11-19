import { ref } from 'vue';

/**
 * Composable use@@Nombre@@: estado y lógica para reutilizar en varios componentes.
 * Uso (dentro de <script setup>):
 *   const { valor, cambiar } = use@@Nombre@@(0);
 * @param {unknown} [inicial]
 */
export function use@@Nombre@@(inicial = null) {
  // ref() guarda un valor reactivo: cuando cambia, la página se actualiza sola.
  const valor = ref(inicial);

  function cambiar(nuevo) {
    valor.value = nuevo;
  }

  return { valor, cambiar };
}
