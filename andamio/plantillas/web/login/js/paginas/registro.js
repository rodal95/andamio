// Código de la página para crear una cuenta (registro.html).
import { ErrorApi } from '../http.js';
import { dibujarMenu } from '../menu.js';
import { aDondeVolver, registrarse } from '../sesion.js';

dibujarMenu();

const formulario = document.getElementById('formulario');
// guía: A dónde volver después de crear la cuenta (?desde=), solo si es de este sitio.
const desde = aDondeVolver();
// El enlace a ingresar.html conserva a dónde volver.
document.getElementById('ingresa').href = `ingresar.html${location.search}`;

function mostrarErrores(errores) {
  for (const [campo, mensajes] of Object.entries(errores)) {
    const lugar = document.getElementById(`error-${campo}`) || document.getElementById('error-general');
    lugar.textContent = [].concat(mensajes).join(' ');
  }
}

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  for (const error of formulario.querySelectorAll('.error')) error.textContent = '';
  // guía: repetir no va a la API: es para controlar acá que la contraseña se escribió bien.
  const { repetir, ...datos } = Object.fromEntries(new FormData(formulario));
  // TODO(logica): más reglas antes de enviar (la API también valida: usuario repetido, contraseña corta o muy común).
  if (datos.password !== repetir) {
    mostrarErrores({ repetir: ['Las contraseñas no coinciden.'] });
    return;
  }
  const boton = formulario.querySelector('button[type="submit"]');
  boton.disabled = true;
  try {
    // guía: registrarse() crea el usuario y también ingresa.
    await registrarse(datos);
    location.replace(desde);
  } catch (e) {
    mostrarErrores(e instanceof ErrorApi && e.estado === 400 ? e.errores : { general: [e.message] });
    boton.disabled = false;
  }
});
