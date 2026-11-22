// guía: La sesión del login (nuevo login): quién ingresó, ingresar, registrarse y salir.
// guía: Usa el login de la API (Django, FastAPI o Express con nuevo login):
// guía:   POST /api/token/ (el token), POST /api/registro/ (crear un usuario), GET /api/yo/ (quién soy).
import { pedir } from './http.js';

/** @type {object | null | undefined} undefined: todavía no se le preguntó a la API. */
let usuario;

/** El usuario que ingresó, o null. La primera vez se lo pregunta a la API (/api/yo/). */
export async function usuarioActual() {
  if (usuario !== undefined) return usuario;
  if (!localStorage.getItem('token')) {
    usuario = null;
    return usuario;
  }
  try {
    usuario = await pedir('/yo/');
  } catch {
    localStorage.removeItem('token'); // venció o no es válido
    usuario = null;
  }
  return usuario;
}

/**
 * Pide el token, lo guarda (desde ahí, http.js lo manda en cada pedido) y devuelve el usuario.
 * @param {{ username: string, password: string }} credenciales
 */
export async function ingresar(credenciales) {
  localStorage.removeItem('token'); // si quedó uno viejo, la API lo rechazaría
  const tokens = await pedir('/token/', { method: 'POST', body: credenciales });
  localStorage.setItem('token', tokens.access);
  usuario = await pedir('/yo/');
  return usuario;
}

/**
 * Crea el usuario y entra con esos mismos datos.
 * @param {{ username: string, email: string, password: string }} datos
 */
export async function registrarse(datos) {
  localStorage.removeItem('token');
  await pedir('/registro/', { method: 'POST', body: datos });
  return ingresar({ username: datos.username, password: datos.password });
}

export function salir() {
  localStorage.removeItem('token');
  usuario = null;
}

const PAGINAS_DEL_LOGIN = ['ingresar.html', 'registro.html'];

/**
 * Para una página que pide ingresar: si nadie ingresó, lleva a ingresar.html (y después
 * vuelve). Devuelve el usuario. Uso, al principio del .js de la página:  await pedirIngreso();
 * Ojo: esto es para que se vea bien, no es seguridad: lo que protege los datos es la API.
 */
export async function pedirIngreso() {
  const actual = location.pathname.split('/').pop() || 'index.html';
  if (PAGINAS_DEL_LOGIN.includes(actual)) return null;
  const quien = await usuarioActual();
  if (!quien) location.replace(`ingresar.html?desde=${encodeURIComponent(actual + location.search)}`);
  return quien;
}

/**
 * En el menú: Ingresar@@y_registrarse@@, o los enlaces que piden sesión, quién ingresó y Salir.
 * @param {HTMLElement} nav el <nav> del menú
 * @param {{ href: string, texto: string, soloConSesion?: boolean }[]} enlaces los del menú
 */
export async function dibujarSesion(nav, enlaces) {
  const zona = document.createElement('span');
  zona.className = 'sesion';
  nav.append(zona);
  const quien = await usuarioActual();
  if (!quien) {
    zona.append(enlace('ingresar.html', 'Ingresar'));
    @@enlace_registro@@
    return;
  }
  for (const e of enlaces.filter((e) => e.soloConSesion)) zona.append(enlace(e.href, e.texto));
  const nombre = document.createElement('span');
  nombre.textContent = quien.username;
  const boton = document.createElement('button');
  boton.type = 'button';
  boton.className = 'boton boton--borde';
  boton.textContent = 'Salir';
  boton.addEventListener('click', () => {
    salir();
    location.href = 'index.html';
  });
  zona.append(nombre, boton);
}

function enlace(href, texto) {
  const a = document.createElement('a');
  a.href = href;
  a.textContent = texto;
  return a;
}

/**
 * A dónde volver después de ingresar (?desde=): solo una página de este mismo sitio. Si no,
 * alguien podría mandar un enlace a ingresar.html?desde=https://sitio-falso.com (o con
 * javascript:) y, después de ingresar, la persona terminaría ahí (redirección abierta).
 */
export function aDondeVolver() {
  const desde = new URLSearchParams(location.search).get('desde');
  try {
    const destino = new URL(desde || 'index.html', location.href);
    return destino.origin === location.origin ? destino.href : 'index.html';
  } catch {
    return 'index.html';
  }
}
