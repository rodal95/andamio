import { onMounted, ref } from 'vue';
import { productoService } from '@/services/productoService';

/** Pide los productos a la API al montar el componente. Devuelve { productos, cargando, error }. */
export function useProductos() {
  const productos = ref([]);
  const cargando = ref(true);
  const error = ref('');

  onMounted(async () => {
    try {
      productos.value = await productoService.listar();
    } catch (e) {
      error.value = e.message;
    } finally {
      cargando.value = false;
    }
  });

  return { productos, cargando, error };
}
