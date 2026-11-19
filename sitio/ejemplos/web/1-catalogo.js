// js/paginas/catalogo.js: la página pide los productos a la API y los muestra en una lista.
import { dibujarMenu } from '../menu.js';
import { productoServicio } from '../servicios/productoServicio.js';

dibujarMenu();

const contenido = document.getElementById('contenido');

async function cargar() {
  contenido.textContent = 'Cargando...';
  try {
    const productos = await productoServicio.listar();
    const lista = document.createElement('ul');
    for (const producto of productos) {
      const item = document.createElement('li');
      item.textContent = `${producto.nombre}: $ ${producto.precio}`;
      lista.append(item);
    }
    contenido.replaceChildren(lista);
  } catch (error) {
    // Si la API no está andando, el error lo dice.
    contenido.textContent = error.message;
  }
}

cargar();
