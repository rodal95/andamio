// js/paginas/ingresar.js: pide el token a la API (POST /api/token/) y lo guarda.
// Desde ese momento, js/http.js lo manda en cada pedido: Authorization: Bearer <token>.
import { pedir } from '../http.js';
import { dibujarMenu } from '../menu.js';

dibujarMenu();

const formulario = document.getElementById('formulario');
const sesion = document.getElementById('sesion');
const error = document.getElementById('error');

async function mostrarSesion() {
  if (!localStorage.getItem('token')) {
    sesion.textContent = 'No iniciaste sesión.';
    return;
  }
  try {
    const usuario = await pedir('/yo/'); // devuelve el usuario dueño del token
    sesion.textContent = `Sesión iniciada como ${usuario.username}.`;
  } catch {
    // El token venció (dura 60 minutos): se borra y hay que volver a ingresar.
    localStorage.removeItem('token');
    sesion.textContent = 'La sesión venció. Volvé a ingresar.';
  }
}

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  error.textContent = '';
  try {
    const tokens = await pedir('/token/', {
      method: 'POST',
      body: { username: formulario.elements.username.value, password: formulario.elements.password.value },
    });
    localStorage.setItem('token', tokens.access);
    formulario.reset();
    await mostrarSesion();
  } catch (e) {
    error.textContent = e.estado === 401 ? 'Usuario o contraseña incorrectos.' : e.message;
  }
});

document.getElementById('salir').addEventListener('click', () => {
  localStorage.removeItem('token');
  mostrarSesion();
});

mostrarSesion();
