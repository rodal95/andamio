# Cómo combinar piezas y proyectos

Las piezas se combinan de dos maneras:

1. **Dentro de un proyecto**: una página usa un servicio, un componente muestra
   datos, un hook (o composable) guarda la lógica, una página enlaza a otra.
2. **Entre proyectos**: una interfaz (web, Vue, React, Next.js, celular) usa una
   API (Django, FastAPI, Express o Next.js full stack).

El código de estas recetas es el mismo que muestra la [página de andamio](https://rodal95.github.io/andamio/)
(`sitio/ejemplos/`), y `tests/integracion/test_combinaciones.py` lo compila o lo
ejecuta en cada cambio: si una receta deja de funcionar, el test falla.

## Qué va con qué

Todas las APIs de andamio responden igual (mismas rutas `/api/<plural>/`, mismo
puerto 8000, mismos errores en español), así que **cualquier interfaz funciona con
cualquier API** sin cambiar nada:

| Interfaz ↓ / API → | Django | FastAPI | Express | Next.js full stack |
|---|---|---|---|---|
| `web` (HTML) | ✓ | ✓ | ✓ | ✓ (`API_URL` en `js/config.js`) |
| `react` | ✓ | ✓ | ✓ | ✓ (`VITE_API_URL`) |
| `vue` | ✓ | ✓ | ✓ | ✓ (`VITE_API_URL`) |
| `next` | ✓ | ✓ | ✓ | — (ya tiene la suya) |
| `react-native` | ✓ | ✓ | ✓ | ✓ (`EXPO_PUBLIC_API_URL`) |
| `reflex` (`crud-api`, `servicio`) | ✓ | ✓ | ✓ | ✓ (`API_URL`) |

`django-web`, `next-fullstack` y `reflex` (`crud`) no necesitan una API aparte:
tienen todo en el mismo proyecto.

## La regla de oro

**Generá el recurso de la API y el servicio (o el `crud`) de la interfaz con los
mismos campos.** Copiá y pegá la lista:

```
nombre:str precio:decimal stock:int
```

---

## Recorrido completo: una API y una web

Dos terminales, dos proyectos.

**Terminal 1, la API (Django):**

```
python -m andamio crear django mi-api
cd mi-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int --migrar
python manage.py runserver
```

**Terminal 2, la web** (elegí una):

```
python -m andamio crear web mi-pagina                     python -m andamio crear vue mi-web
cd mi-pagina                                              cd mi-web
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
python -m http.server 5173                                npm install && npm run dev
```

Abrí http://localhost:5173/productos.html (web) o http://localhost:5173/productos (Vue):
agregá un producto, editalo, borralo. Si dejás un campo mal, el error de la API
aparece debajo del campo.

---

## Una página que muestra los datos de un servicio

La combinación más común: una página propia que pide datos a la API.

### Web HTML

```
python -m andamio nuevo pagina Catalogo
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

`catalogo.html` ya tiene un `<div id="contenido">`. En `js/paginas/catalogo.js`:

```js
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
    contenido.textContent = error.message; // por ejemplo: la API no está andando
  }
}

cargar();
```

- `await productoServicio.listar()` espera la respuesta de la API (por eso `cargar` es `async`).
- `textContent` (no `innerHTML`): un dato nunca se ejecuta como HTML.
- Con un componente: `nuevo componente Tarjeta` y
  `contenido.replaceChildren(...productos.map((p) => crearTarjeta({ titulo: p.nombre, texto: `$ ${p.precio}` })))`.

### Vue

```
python -m andamio nuevo pagina Catalogo
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

`src/pages/CatalogoPage.vue`:

```vue
<script setup>
import { onMounted, ref } from 'vue';
import { productoService } from '@/services/productoService';

const productos = ref([]);
const error = ref('');

// onMounted se ejecuta una vez, cuando la página aparece: ahí se piden los datos.
onMounted(async () => {
  try {
    productos.value = await productoService.listar();
  } catch (e) {
    error.value = e.message;
  }
});
</script>

<template>
  <h1>Catálogo</h1>
  <p v-if="error" class="error">{{ error }}</p>
  <ul v-else>
    <li v-for="producto in productos" :key="producto.id">{{ producto.nombre }}: $ {{ producto.precio }}</li>
  </ul>
</template>
```

Siguiente paso: llevar la carga a un composable (`nuevo composable productos`) que
devuelva `{ productos, cargando, error }`, y enlazar cada producto a su detalle del
`crud` con `<RouterLink :to="`/productos/${producto.id}`">`.

### React

```
python -m andamio nuevo pagina Catalogo
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

`src/pages/CatalogoPage/CatalogoPage.jsx` (o `.tsx`):

```jsx
import { useEffect, useState } from 'react';
import { productoService } from '../../services/productoService';
import styles from './CatalogoPage.module.css';

export function CatalogoPage() {
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState('');

  // Al abrir la página, se piden los productos a la API (una sola vez: por eso el []).
  useEffect(() => {
    productoService
      .listar()
      .then(setProductos)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <main className={styles.root}>
      <h1>Catálogo</h1>
      {error && <p>No se pudo cargar: {error}</p>}
      <ul>
        {productos.map((producto) => (
          <li key={producto.id}>{producto.nombre}: $ {producto.precio}</li>
        ))}
      </ul>
    </main>
  );
}
```

### Django con plantillas (sin API)

En el monolito no hay servicio: la **vista** consulta el modelo y le pasa los datos a
la plantilla. Ver [Sitio con Django y plantillas → una página con datos](django-plantillas.md#5-una-página-que-muestra-datos-de-la-base).

---

## Login con JWT desde la web HTML

La API de Django tiene el login con `nuevo login`; la web guarda el token y lo manda
en cada pedido.

**En la API:**

```
python -m andamio nuevo login
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int --protegido --migrar
pip install -r requirements.txt
python manage.py createsuperuser
python manage.py runserver
```

**En la web:**

```
python -m andamio nuevo pagina Ingresar
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
```

En `ingresar.html`, un formulario con `username` y `password` (y un `<p id="sesion">`).
En `js/paginas/ingresar.js`:

```js
import { pedir } from '../http.js';
import { dibujarMenu } from '../menu.js';

dibujarMenu();

const formulario = document.getElementById('formulario');

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const tokens = await pedir('/token/', {
    method: 'POST',
    body: { username: formulario.elements.username.value, password: formulario.elements.password.value },
  });
  localStorage.setItem('token', tokens.access); // desde ahora, http.js lo manda solo
  const usuario = await pedir('/yo/');
  document.getElementById('sesion').textContent = `Sesión iniciada como ${usuario.username}.`;
});
```

La versión completa (con errores, "salir" y el token vencido) está en
`sitio/ejemplos/web/3-ingresar.html` y `3-ingresar.js`. Ahora `productos.html` puede
agregar, editar y eliminar; sin token, la API responde 401 ("Las credenciales de
autenticación no se proveyeron.").

---

## Login con JWT desde React, Vue o Next.js

El `http` que generan `servicio` y `crud` (en `services/http`) manda el token
guardado en cada pedido, así que el `crud` funciona con recursos `--protegido` en
cuanto iniciás sesión. Trae tres funciones: `guardarToken(token)`, `borrarToken()` y
`leerToken()`.

```
python -m andamio nuevo login                                                 (en la API de Django)
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int --protegido --migrar
python -m andamio nuevo pagina Ingresar                                       (en la web)
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
```

**Vue** (`src/pages/IngresarPage.vue`):

```vue
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { borrarToken, guardarToken, http } from '@/services/http';

const router = useRouter();
const usuario = ref('');
const clave = ref('');
const error = ref('');

async function ingresar() {
  try {
    const tokens = await http.post('/token/', { username: usuario.value, password: clave.value });
    guardarToken(tokens.access); // desde ahora, cada pedido lo manda solo
    router.push('/productos');
  } catch (e) {
    error.value = e.message; // "No se encontró una cuenta activa con las credenciales proporcionadas."
  }
}
</script>

<template>
  <h1>Ingresar</h1>
  <form class="formulario" @submit.prevent="ingresar">
    <label class="campo">Usuario <input v-model="usuario" autocomplete="username" required /></label>
    <label class="campo">Contraseña <input v-model="clave" type="password" autocomplete="current-password" required /></label>
    <p v-if="error" class="error">{{ error }}</p>
    <button type="submit" class="boton">Ingresar</button>
    <button type="button" class="boton boton--borde" @click="borrarToken()">Salir</button>
  </form>
</template>
```

**React** (`src/pages/IngresarPage/IngresarPage.jsx`; en Next.js, `app/ingresar/page`
con `'use client'` arriba y `useRouter` de `next/navigation`):

```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router';
import { guardarToken, http } from '../../services/http';

export function IngresarPage() {
  const navegar = useNavigate();
  const [usuario, setUsuario] = useState('');
  const [clave, setClave] = useState('');
  const [error, setError] = useState('');

  async function ingresar(evento) {
    evento.preventDefault();
    try {
      const tokens = await http.post('/token/', { username: usuario, password: clave });
      guardarToken(tokens.access);
      navegar('/productos');
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <form onSubmit={ingresar}>
      <input value={usuario} onChange={(e) => setUsuario(e.target.value)} placeholder="Usuario" />
      <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} placeholder="Contraseña" />
      {error && <p>{error}</p>}
      <button type="submit">Ingresar</button>
    </form>
  );
}
```

(En TypeScript: `http.post<{ access: string; refresh: string }>('/token/', ...)`.)

- Sin token, el formulario del `crud` muestra el mensaje de la API: "Las credenciales
  de autenticación no se proveyeron."
- El token dura 60 minutos. Cuando vence, la API responde 401 ("El token proporcionado
  no es válido..."): `borrarToken()` y volver a ingresar.
- El token queda en `localStorage` con la clave `token`, la misma que usa la web HTML.

---

## Una API y una app de celular (React Native)

```
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int    (en la app)
```

- En el emulador de Android tu PC es `10.0.2.2` (ya está en el `.env` de la app).
- En un celular real: `EXPO_PUBLIC_API_URL=http://IP-DE-TU-PC:8000/api` en el `.env`
  de la app, y la API escuchando en la red (`python manage.py runserver 0.0.0.0:8000`,
  con la IP en `ALLOWED_HOSTS` del `.env` de Django).

---

## Buscar, ordenar y filtrar

Todas las APIs aceptan parámetros en la lista; desde cualquier servicio:

```js
productoServicio.listar({ search: 'yerba', ordering: '-precio' })   // web HTML
```

```
http://localhost:8000/api/productos/?search=yerba          busca en los campos de texto
http://localhost:8000/api/productos/?ordering=-precio      ordena (con - de mayor a menor)
http://localhost:8000/api/productos/?stock=10              filtra por igualdad
```
