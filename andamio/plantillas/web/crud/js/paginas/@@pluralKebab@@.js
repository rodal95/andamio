// La página @@titulo@@ (@@pluralKebab@@.html): lista, agrega, edita y elimina usando la API.
import { ErrorApi } from '../http.js';
import { dibujarMenu } from '../menu.js';
import { @@nombreCamel@@Servicio } from '../servicios/@@nombreCamel@@Servicio.js';

dibujarMenu();

// Los campos y su tipo: se usan para leer el formulario y para mostrar la tabla.
const CAMPOS = {
  @@campos_tipos@@
};
// Los que se muestran como columnas de la tabla.
const COLUMNAS = [@@columnas@@];

const formulario = document.getElementById('formulario');
const filas = document.getElementById('filas');
const estado = document.getElementById('estado');
let editando = null; // id del registro que se está editando (null = agregando)

/** Lee el formulario y convierte cada valor a su tipo (número, sí/no...). */
function leerFormulario() {
  const datos = {};
  for (const [campo, tipo] of Object.entries(CAMPOS)) {
    const control = formulario.elements[campo];
    if (tipo === 'bool') datos[campo] = control.checked;
    else if (['int', 'decimal', 'float'].includes(tipo)) datos[campo] = control.value === '' ? null : Number(control.value);
    else datos[campo] = control.value;
  }
  return datos;
}

/** Llena el formulario con un registro (para editarlo) o lo deja vacío. */
function llenarFormulario(registro) {
  for (const [campo, tipo] of Object.entries(CAMPOS)) {
    const control = formulario.elements[campo];
    if (tipo === 'bool') control.checked = registro ? Boolean(registro[campo]) : false;
    // datetime-local espera "2025-03-15T10:30" (sin segundos ni zona horaria).
    else if (tipo === 'datetime') control.value = registro ? String(registro[campo]).slice(0, 16) : '';
    else control.value = registro ? registro[campo] : '';
  }
  editando = registro ? registro.id : null;
  document.getElementById('titulo-formulario').textContent = registro ? 'Editar' : 'Agregar';
  document.getElementById('cancelar').hidden = !registro;
  mostrarErrores({});
}

/** Muestra debajo de cada campo los errores que devolvió la API. */
function mostrarErrores(errores, general = '') {
  for (const campo of Object.keys(CAMPOS)) {
    document.getElementById(`error-${campo}`).textContent = (errores[campo] || []).join(' ');
  }
  document.getElementById('error-general').textContent = general;
}

/** Cómo se ve un valor en la tabla. */
function mostrar(valor, tipo) {
  if (valor === null || valor === undefined) return '';
  if (tipo === 'bool') return valor ? 'Sí' : 'No';
  if (tipo === 'date') return new Date(`${valor}T00:00`).toLocaleDateString();
  if (tipo === 'datetime') return new Date(valor).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
  return valor;
}

function boton(texto, clase, alHacerClic) {
  const b = document.createElement('button');
  b.type = 'button';
  b.className = `boton ${clase}`;
  b.textContent = texto;
  b.addEventListener('click', alHacerClic);
  return b;
}

async function cargar() {
  try {
    const registros = await @@nombreCamel@@Servicio.listar();
    filas.replaceChildren(
      ...registros.map((registro) => {
        const fila = document.createElement('tr');
        for (const campo of COLUMNAS) {
          const celda = document.createElement('td');
          celda.textContent = mostrar(registro[campo], CAMPOS[campo]);
          fila.append(celda);
        }
        const acciones = document.createElement('td');
        acciones.className = 'acciones';
        acciones.append(
          boton('Editar', 'boton--borde', () => llenarFormulario(registro)),
          boton('Eliminar', 'boton--peligro', () => eliminar(registro)),
        );
        fila.append(acciones);
        return fila;
      }),
    );
    estado.textContent = registros.length ? '' : 'Todavía no hay @@verbose_plural@@.';
    document.querySelector('.tabla').hidden = registros.length === 0;
  } catch (error) {
    estado.textContent = error.message;
  }
}

async function eliminar(registro) {
  if (!confirm('¿Eliminar este registro?')) return;
  try {
    await @@nombreCamel@@Servicio.eliminar(registro.id);
    if (editando === registro.id) llenarFormulario(null);
    await cargar();
  } catch (error) {
    alert(error.message);
  }
}

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault(); // que el navegador no recargue la página
  try {
    const datos = leerFormulario();
    if (editando === null) await @@nombreCamel@@Servicio.crear(datos);
    else await @@nombreCamel@@Servicio.actualizar(editando, datos);
    llenarFormulario(null);
    await cargar();
  } catch (error) {
    if (error instanceof ErrorApi && error.estado === 400) mostrarErrores(error.errores, 'Revisá los datos marcados.');
    else mostrarErrores({}, error.message);
  }
});

document.getElementById('cancelar').addEventListener('click', () => llenarFormulario(null));

cargar();
