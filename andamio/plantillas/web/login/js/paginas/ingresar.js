// Código de la página para ingresar (ingresar.html).
import { ErrorApi } from '../http.js';
import { dibujarMenu } from '../menu.js';
import { ingresar } from '../sesion.js';

dibujarMenu();

const formulario = document.getElementById('formulario');
// guía: Si llegó desde una página que pide ingresar, vuelve ahí (la dirección está en ?desde=).
const desde = new URLSearchParams(location.search).get('desde') || 'index.html';
// El enlace a registro.html (si está) conserva a dónde volver.
const registrate = document.getElementById('registrate');
if (registrate) registrate.href = `registro.html${location.search}`;

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  for (const error of formulario.querySelectorAll('.error')) error.textContent = '';
  const datos = Object.fromEntries(new FormData(formulario));
  const boton = formulario.querySelector('button[type="submit"]');
  boton.disabled = true;
  try {
    await ingresar(datos);
    location.replace(desde);
  } catch (e) {
    // guía: Usuario o contraseña incorrectos: la API responde 401 y lo explica (va en general).
    const errores = e instanceof ErrorApi && e.estado === 400 ? e.errores : { general: [e.message] };
    for (const [campo, mensajes] of Object.entries(errores)) {
      const lugar = document.getElementById(`error-${campo}`) || document.getElementById('error-general');
      lugar.textContent = [].concat(mensajes).join(' ');
    }
    boton.disabled = false;
  }
});
