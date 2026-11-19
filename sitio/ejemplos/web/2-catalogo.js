// js/paginas/catalogo.js: cada producto se muestra con el componente Tarjeta.
import { crearTarjeta } from '../componentes/tarjeta.js';
import { dibujarMenu } from '../menu.js';
import { productoServicio } from '../servicios/productoServicio.js';

dibujarMenu();

const contenido = document.getElementById('contenido');

async function cargar() {
  contenido.textContent = 'Cargando...';
  try {
    const productos = await productoServicio.listar();
    const tarjetas = productos.map((producto) =>
      crearTarjeta({ titulo: producto.nombre, texto: `$ ${producto.precio} (${producto.stock} en stock)` }),
    );
    contenido.replaceChildren(...tarjetas);
  } catch (error) {
    contenido.textContent = error.message;
  }
}

cargar();
