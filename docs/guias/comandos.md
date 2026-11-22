# Todos los comandos, por tecnología

Cada sección tiene: cómo crear el proyecto, cómo ponerlo en marcha, y cada pieza con
su comando, qué genera y un ejemplo de uso. Los comandos empiezan con
`python -m andamio` (en Linux o Mac, `python3 -m andamio`).

## El árbol de comandos

`python -m andamio comandos` (o `commands`) muestra este árbol en la terminal, con las
piezas de cada tecnología. Entre paréntesis, el mismo comando en inglés.

```
python -m andamio                                   menú interactivo: te pregunta todo
python -m andamio --version                         la versión instalada
python -m andamio --help                            la ayuda (también: <comando> --help)
│
├── crear <tipo> <nombre>                (create)   crea un proyecto en una carpeta nueva
├── crear <tipo> .                                  crea el proyecto en la carpeta actual (vacía)
│     --simular            (--dry-run)              muestra qué crearía, sin tocar nada
│     --variante ts|js     (--variant)              lenguaje (Express, React, React Native, Next.js)
│     --js / --ts                                   atajos de --variante
│     --sin-guia           (--no-guide)             sin los comentarios que explican el código
│
├── nuevo <pieza> [nombre] [campos...]   (new, generate, g)   agrega una pieza al proyecto actual
│     --plural <plural>                             el plural, si el automático no sirve
│     --simular            (--dry-run)              muestra qué crearía o modificaría
│     --migrar             (--migrate)              crea y aplica la migración
│     --protegido          (--protected)            crear, modificar y eliminar piden login
│     --carpeta <carpeta>  (--folder)               subcarpeta de app/ (React Native)
│     --modo auto|claro|oscuro  (--mode)            modo del tema (pieza tema)
│     --datos <servicio>   (--data)                 la página o pantalla muestra datos de la API (React, React Native)
│     --uno                (--one)                  con --datos: muestra uno solo, con el id en la ruta
│     --form                                        con --datos: el formulario para crear y editar
│     --solo <funciones>   (--only)                 el servicio solo con esas funciones: --solo crear
│     --sin-menu           (--no-menu)              la entidad sin su menú de consola (Python + SQLite)
│     --solo-lectura       (--read-only)            la API solo lista y muestra (Django)
│     --sin-guia           (--no-guide)             sin los comentarios que explican el código
│
├── info                                            qué proyecto detectó y qué piezas acepta
├── init [tipo]                                     prepara un proyecto que ya existe (crea andamio.json)
│     --variante ts|js / --js / --ts                lenguaje, si no se detecta solo
│     --simular            (--dry-run)              muestra qué haría, sin crear nada
├── mapa                                 (map)      las piezas generadas y si siguen conectadas
├── pendientes                           (todo, pending)   dónde falta tu lógica (marcas TODO(logica))
├── comandos                             (commands) este árbol
├── plantillas exportar [pieza]          (templates export)   copia las plantillas para editarlas
└── configurar                           (configure, setup)   permite escribir solo "andamio"
      --simular            (--dry-run)
```

Qué opciones acepta cada pieza:

| Opción | Piezas |
|---|---|
| `--migrar` | `recurso` (Django, Express, Next.js full stack), `crud` (Django con plantillas, Reflex) |
| `--protegido` | `recurso` (Django), `crud` (Django con plantillas) |
| `--carpeta` | `pantalla` (React Native) |
| `--modo` | `tema` (web, Django con plantillas, Vue, React, Next.js, React Native, Reflex) |
| `--datos`, `--uno`, `--form` | `pagina` (React), `pantalla` (React Native) |
| `--solo` | `servicio` (React, Next.js, Vue, React Native, web) |
| `--sin-menu` | `entidad` (Python + SQLite) |
| `--solo-lectura` | `recurso` (Django) |
| `--plural`, `--simular`, `--sin-guia` | todas (`--plural` solo en las que usan plural) |

## La forma general de cada pieza

Los ejemplos de esta guía usan `producto`, `Contacto` o `Tarjeta`, pero **el nombre y
los campos son los tuyos**. Lo que va entre `< >` lo elegís vos:

```
nuevo recurso <nombre> <campo:tipo>...        nuevo crud <nombre> <campo:tipo>...
nuevo servicio <nombre> <campo:tipo>...       nuevo entidad <nombre> <campo:tipo>...
nuevo pagina <Nombre>                         nuevo componente <Nombre>
nuevo pantalla <nombre> [--carpeta <carpeta>] nuevo hook <nombre>   /   nuevo composable <nombre>
nuevo estado <nombre>                         nuevo crud-api <nombre> <campo:tipo>...
nuevo login                                   nuevo tema [<color>] [--modo auto|claro|oscuro]
nuevo ui <parte>                              nuevo estilo <nombre>
```

Por ejemplo, con otros nombres:

```
python -m andamio nuevo crud cliente nombre:str email:email telefono:str
python -m andamio nuevo pagina SobreNosotros
python -m andamio nuevo componente BotonFlotante
python -m andamio nuevo servicio pedido cliente:str total:decimal entregado:bool
python -m andamio nuevo estilo perfil-usuario
```

`python -m andamio comandos` muestra la forma general y un ejemplo de cada pieza del
proyecto en que estás.

## En inglés

Los comandos, las piezas y las opciones se pueden escribir en inglés: hacen exactamente
lo mismo. Los mensajes de andamio siguen en español.

| Español | Inglés |
|---|---|
| `crear` | `create` |
| `nuevo` | `new`, `generate`, `g` |
| `comandos` | `commands` |
| `mapa` | `map` |
| `pendientes` | `todo`, `pending` |
| `plantillas exportar` | `templates export` |
| `configurar` | `configure`, `setup` |
| `entidad`, `recurso`, `componente`, `pagina`, `pantalla`, `servicio`, `estado`, `tema`, `estilo`, `busqueda`, `accion` | `entity`, `resource`, `component`, `page`, `screen`, `service`, `state`, `theme`, `style`, `search`, `action` |
| `--simular`, `--variante`, `--migrar`, `--protegido`, `--carpeta`, `--modo`, `--datos`, `--uno`, `--solo`, `--sin-menu`, `--solo-lectura`, `--sin-guia` | `--dry-run`, `--variant`, `--migrate`, `--protected`, `--folder`, `--mode`, `--data`, `--one`, `--only`, `--no-menu`, `--read-only`, `--no-guide` |
| `--modo claro`, `--modo oscuro`, `--modo auto` | `--mode light`, `--mode dark`, `--mode auto` |

`crud`, `crud-api`, `login`, `hook`, `composable`, `ui`, `menu`, `info` y `--form` son iguales en los dos idiomas.

```
python -m andamio create django my-api
python -m andamio new resource product name:str price:decimal --plural products --migrate --protected
python -m andamio new page About
```

Los alias traducen los **comandos**, no tus nombres: el plural se arma con las reglas
del español (`product` → `productes`). Si nombrás en inglés, indicá el plural con
`--plural products`.

---

Opciones que sirven en todas las piezas:

| Opción | Qué hace |
|---|---|
| `--simular` | Muestra qué crearía o modificaría, sin tocar nada. |
| `--plural paises` | Indica el plural cuando el automático no sirve. |
| `--sin-guia` | Genera el código sin los comentarios que lo explican (para quien ya lo conoce). Las marcas `TODO(logica)`, que dicen dónde va tu lógica, quedan igual. |
| `--migrar` | Después de generar, crea y aplica la migración (Django, Django con plantillas, Express, Next.js full stack, Reflex). |
| `--protegido` | Crear, modificar y eliminar piden login (Django y Django con plantillas). |
| `--carpeta productos` | Crea la pantalla dentro de una carpeta de `app/` (React Native). |
| `--datos producto` | La página o pantalla muestra los datos de un servicio que ya generaste, con el hook `useConsulta` (React, React Native). |
| `--uno` | Con `--datos`: muestra uno solo; su ruta lleva el id (`/producto-detalle/:id` en React, `app/producto/[id]` en React Native). |
| `--form` | Con `--datos`: el formulario para crear y editar, con el hook `useFormulario` (React, React Native). Si el servicio solo tiene `crear` (`--solo crear`), el formulario solo envía: sin `useFormulario` y sin ruta para editar. |
| `--solo crear` | El servicio solo con esas funciones (`listar`, `obtener`, `crear`, `actualizar`, `eliminar`; separadas por coma). También en inglés o con el método HTTP: `--solo post`, `--only create`. Las páginas y pantallas controlan que el servicio tenga lo que usan. |
| `--js` | Al crear: el proyecto en JavaScript en lugar de TypeScript (Express, React, React Native, Next.js). |

---

## Python + SQLite (consola) — `python`

```
python -m andamio crear python mi-tienda
cd mi-tienda
python main.py
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `entidad` | `nuevo entidad producto nombre:str precio:float stock:int` | La tabla en `sql/schema.sql`, `entidades/producto.py` (crear, listar, obtener, actualizar, eliminar) y `menus/menu_producto.py`, con su opción en el menú principal. |
| `entidad --sin-menu` | `nuevo entidad producto nombre:str precio:float --sin-menu` | Solo la tabla y `entidades/producto.py`, sin el menú de consola (para usar las funciones desde tu código). |
| `menu` | `nuevo menu producto` | `menus/menu_producto.py` para una entidad que ya existe (con los campos con que se generó), y su opción en el menú principal. |
| `busqueda` | `nuevo busqueda producto nombre` | `buscar_por_nombre(valor)` al final de `entidades/producto.py` (`LIKE` en los textos: busca lo que contiene; `=` en los números) y su opción en el menú de la entidad. |
| `entidad` con relación | `nuevo entidad producto nombre:str categoria:fk` | Lo mismo, con la columna `categoria_id` (`REFERENCES categorias(id) ON DELETE SET NULL`). `listar()` hace un `LEFT JOIN` para mostrar el nombre de la categoría, y el menú muestra las categorías y pide un id que exista. Necesita la entidad `categoria`. |

```python
from entidades import producto

nuevo_id = producto.crear("Yerba", 1500.0, 10)
for fila in producto.listar():
    print(fila["nombre"], fila["precio"])
```

Tipos: `str`, `int`, `float` y `fk` (relación con otra entidad).

---

## Django REST (API) — `django`

```
python -m andamio crear django mi-api
cd mi-api
python -m venv .venv
.venv\Scripts\activate                 (Linux o Mac: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver             http://127.0.0.1:8000/api/docs/
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `recurso` | `nuevo recurso producto nombre:str precio:decimal stock:int` | La app `productos/`: modelo, serializer, ViewSet (CRUD con filtros, búsqueda y orden), rutas `/api/productos/`, admin y 5 tests. La registra en `LOCAL_APPS` y en `config/urls.py`. |
| `recurso` con relación | `nuevo recurso producto nombre:str categoria:fk` | Lo mismo, con `categoria = models.ForeignKey("categorias.Categoria", on_delete=models.SET_NULL, null=True, ...)`. La API recibe y devuelve el id, devuelve también `categoria_texto` y filtra con `?categoria=3`. Necesita el recurso `categoria`. |
| `recurso --solo-lectura` | `nuevo recurso pais nombre:str --plural paises --solo-lectura` | Un `ReadOnlyModelViewSet`: la API solo lista y muestra (crear, modificar y eliminar responden 405) y los datos se cargan desde `/admin/`. Para catálogos fijos. |
| `accion` | `nuevo accion producto destacar` | Una acción propia en el ViewSet que ya existe: `POST /api/productos/3/destacar/`, con la marca `TODO(logica)` para lo que hace, su test y su petición en el `.http`. Con varias: `nuevo accion producto destacar archivar`. |
| `recurso --protegido` | `nuevo recurso pedido cliente:str total:decimal --protegido` | Lo mismo, con `permission_classes = [IsAuthenticatedOrReadOnly]` y un test más (sin login no se puede crear). |
| `login` | `nuevo login` | La app `cuentas/` con SimpleJWT: `/api/token/`, `/api/token/refresh/`, `/api/token/verify/`, `/api/registro/` y `/api/yo/`, 6 tests, y la configuración en `settings.py` y `requirements.txt`. No lleva nombre. |

```
GET    /api/productos/                  lista            POST   /api/productos/      crea
GET    /api/productos/1/                ve uno           PATCH  /api/productos/1/    modifica
DELETE /api/productos/1/                elimina
GET    /api/productos/?search=yerba     busca            GET    /api/productos/?ordering=-precio   ordena
GET    /api/productos/?stock=10         filtra
```

Paso a paso completo: [API REST con Django + login JWT](django-api-jwt.md).

---

## Django con plantillas (sitio, monolito) — `django-web`

```
python -m andamio crear django-web mi-sitio
cd mi-sitio
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver             http://127.0.0.1:8000
```

Ya trae: inicio, menú, login (`/cuentas/login/`), registro (`/cuentas/registro/`),
salir, mensajes y `/admin/`.

| Pieza | Comando | Qué genera |
|---|---|---|
| `crud` | `nuevo crud producto nombre:str precio:decimal stock:int` | La app `productos/`: modelo, formulario (`forms.py`), 5 vistas (lista con búsqueda y páginas, detalle, crear, editar, eliminar), 4 plantillas HTML, rutas con nombre, admin y 6 tests. Registra la app, las rutas `/productos/` y el enlace en el menú. |
| `crud --protegido` | `nuevo crud pedido cliente:str total:decimal --protegido` | Lo mismo, con `LoginRequiredMixin` en crear, editar y eliminar. |
| `pagina` | `nuevo pagina Contacto` | `templates/paginas/contacto.html` (hereda de `base.html`), la ruta `/contacto/` y el enlace en el menú. |
| `tema` | `nuevo tema violeta --modo auto` | Las variables CSS del proyecto (colores, letra, bordes, sombras, modo oscuro) y estilos base, en `static/css/tema.css`, cargado en `templates/base.html`. |
| `ui` | `nuevo ui tarjetas` | Una parte lista en `static/css/ui/`: tarjetas, alertas, modal, navbar, badges, tabs, paginacion, cargando, responsive o accesible. |
| `estilo` | `nuevo estilo catalogo` | `static/css/estilos/catalogo.css` con la clase `.catalogo` armada con las variables del tema, para tu componente o página. |

```html
{% extends "base.html" %}
{% block contenido %}
  <a href="{% url 'productos:detalle' producto.pk %}">{{ producto.nombre }}</a>
{% endblock %}
```

Paso a paso completo: [Sitio con Django y plantillas](django-plantillas.md).

---

## FastAPI — `fastapi`

```
python -m andamio crear fastapi mi-api
cd mi-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload     http://127.0.0.1:8000/docs
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `recurso` | `nuevo recurso producto nombre:str precio:decimal stock:int` | `app/productos/` con el modelo (SQLModel, con validación) y el router (CRUD en `/api/productos/`), y 5 tests. Lo registra en `app/main.py`. La tabla se crea al arrancar. |

Responde igual que Django (mismas rutas, mismos errores en español): las interfaces
la usan sin cambios.

---

## Express + Prisma — `express`

```
python -m andamio crear express mi-api          (con --js, en JavaScript)
cd mi-api
npm install
npm run dev                                      http://localhost:8000/docs
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `recurso` | `nuevo recurso producto nombre:str precio:decimal stock:int --migrar` | El modelo en `prisma/schema.prisma`, la validación (Zod, mensajes en español), el router en `src/productos/` y 5 tests. Con `--migrar`, `npx prisma migrate dev`. |

---

## HTML + CSS + JavaScript — `web`

```
python -m andamio crear web mi-pagina
cd mi-pagina
python -m http.server 5173                       http://localhost:5173
```

No necesita Node ni npm. No abras el `.html` con doble clic: los `import` de
JavaScript necesitan un servidor.

| Pieza | Comando | Qué genera |
|---|---|---|
| `pagina` | `nuevo pagina Contacto` | `contacto.html` y `js/paginas/contacto.js`, con el enlace en el menú (`js/menu.js`). |
| `componente` | `nuevo componente Tarjeta` | `js/componentes/tarjeta.js` (la función `crearTarjeta`) y `css/componentes/tarjeta.css`, importado en `css/estilos.css`. |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `js/servicios/productoServicio.js`: `listar`, `obtener`, `crear`, `actualizar`, `eliminar`, usando `pedir()` de `js/http.js`. |
| `crud` | `nuevo crud producto nombre:str precio:decimal stock:int` | `productos.html` y `js/paginas/productos.js`: tabla, formulario para agregar y editar (con los errores de la API por campo) y eliminar. Usa el servicio (lo crea si falta). |
| `tema` | `nuevo tema violeta --modo auto` | Las variables CSS del proyecto (colores, letra, bordes, sombras, modo oscuro) y estilos base, en `css/tema.css`, cargado en `css/estilos.css`. |
| `ui` | `nuevo ui tarjetas` | Una parte lista en `css/ui/`: tarjetas, alertas, modal, navbar, badges, tabs, paginacion, cargando, responsive o accesible. |
| `estilo` | `nuevo estilo catalogo` | `css/estilos/catalogo.css` con la clase `.catalogo` armada con las variables del tema, para tu componente o página. |

```js
import { crearTarjeta } from '../componentes/tarjeta.js';
import { productoServicio } from '../servicios/productoServicio.js';

const productos = await productoServicio.listar();
contenido.replaceChildren(...productos.map((p) => crearTarjeta({ titulo: p.nombre, texto: `$ ${p.precio}` })));
```

La dirección de la API está en `js/config.js`. `js/http.js` manda el token del login
si lo guardaste en `localStorage` (ver [combinaciones](combinaciones.md#login-con-jwt-desde-la-web-html)).

---

## React + Vite — `react`

```
python -m andamio crear react mi-web             (con --js, en JavaScript)
cd mi-web
npm install
npm run dev                                      http://localhost:5173
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `componente` | `nuevo componente Tarjeta` | `src/components/Tarjeta/` con su `.module.css`, exportado en `src/components/index`. |
| `pagina` | `nuevo pagina Contacto` | `src/pages/ContactoPage/`, con su ruta `/contacto` y su enlace en `src/App`. |
| `pagina --datos` | `nuevo pagina ProductoLista --datos producto` | La página con la lista del servicio `productoService`: `useConsulta(productoService.listar)`, con cargando, error y lista vacía. Necesita el servicio (crea `useConsulta` si falta). |
| `pagina --datos --uno` | `nuevo pagina ProductoDetalle --datos producto --uno` | La página de uno solo: toma el id de la ruta (`/producto-detalle/:id`) y usa `obtener(id)`. Muestra los campos con que se generó el servicio. No va en el menú. |
| `pagina --datos --form` | `nuevo pagina ProductoEditar --datos producto --form` | El formulario para crear (`/producto-editar`) y editar (`/producto-editar/3`) con el hook `useFormulario`: carga el registro, guarda con `crear` o `actualizar` y muestra los errores de la API en cada campo. |
| `servicio --solo` | `nuevo servicio contacto nombre:str email:email mensaje:text --solo crear` | El servicio solo con `crear` (POST): para un formulario que solo envía, como el de contacto. No crea los hooks (no los usa). |
| `pagina --datos --form` (solo envía) | `nuevo pagina Contacto --datos contacto --form` | Con un servicio que solo tiene `crear`: el formulario con su propio estado (`useState`), el botón Enviar (deshabilitado mientras envía), los errores de la API en cada campo y «¡Listo! Se envió.». Sin ruta para editar. |
| `hook` | `nuevo hook contador` | `src/hooks/useContador`. |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `src/services/productoService` (y `http` y los hooks `useConsulta` y `useFormulario`, si faltan). |
| `crud` | `nuevo crud producto nombre:str precio:decimal stock:int` | Lista, detalle y formulario en `src/pages/productos/`, el componente `ProductoDetalle`, los hooks `useConsulta` y `useFormulario`, el servicio y las 4 rutas con su enlace. |
| `tema` | `nuevo tema violeta --modo auto` | Las variables CSS del proyecto (colores, letra, bordes, sombras, modo oscuro) y estilos base, en `src/tema.css`, cargado en `src/main`. |
| `ui` | `nuevo ui tarjetas` | Una parte lista en `src/ui/`: tarjetas, alertas, modal, navbar, badges, tabs, paginacion, cargando, responsive o accesible. |
| `estilo` | `nuevo estilo catalogo` | `src/estilos/catalogo.css` con la clase `.catalogo` armada con las variables del tema, para tu componente o página. |

---

## Vue + Vite — `vue`

```
python -m andamio crear vue mi-web
cd mi-web
npm install
npm run dev                                      http://localhost:5173
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `componente` | `nuevo componente Tarjeta` | `src/components/Tarjeta.vue` con props, slot y `<style scoped>`. |
| `pagina` | `nuevo pagina Contacto` | `src/pages/ContactoPage.vue`, su ruta en `src/router.js` y su enlace en `src/App.vue`. |
| `composable` | `nuevo composable contador` | `src/composables/useContador.js` (como un hook de React). |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `src/services/productoService.js` (y `http.js`, si falta). |
| `crud` | `nuevo crud producto nombre:str precio:decimal stock:int` | `ProductoListaPage`, `ProductoDetallePage` y `ProductoFormPage` (con `v-model` y los errores de la API) en `src/pages/productos/`, el servicio y las 4 rutas con su enlace. |
| `tema` | `nuevo tema violeta --modo auto` | Las variables CSS del proyecto (colores, letra, bordes, sombras, modo oscuro) y estilos base, en `src/tema.css`, cargado en `src/main.js`. |
| `ui` | `nuevo ui tarjetas` | Una parte lista en `src/ui/`: tarjetas, alertas, modal, navbar, badges, tabs, paginacion, cargando, responsive o accesible. |
| `estilo` | `nuevo estilo catalogo` | `src/estilos/catalogo.css` con la clase `.catalogo` armada con las variables del tema, para tu componente o página. |

```vue
<script setup>
import Tarjeta from '@/components/Tarjeta.vue';
import { useContador } from '@/composables/useContador';
const { valor, cambiar } = useContador(0);
</script>

<template>
  <Tarjeta titulo="Contador"><button @click="cambiar(valor + 1)">{{ valor }}</button></Tarjeta>
</template>
```

La dirección de la API está en `VITE_API_URL` (`.env`).

---

## React Native + Expo — `react-native`

```
python -m andamio crear react-native mi-app      (con --js, en JavaScript)
cd mi-app
npm install
npx expo start
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `pantalla` | `nuevo pantalla detalle-producto --carpeta productos` | `app/productos/detalle-producto` (Expo Router: el archivo es la ruta). |
| `pantalla --datos` | `nuevo pantalla productos --datos producto` | La pantalla con la lista del servicio `productoService`: `FlatList` con `useConsulta(productoService.listar)`, cargando y error. Necesita el servicio (crea `hooks/useConsulta` si falta). |
| `pantalla --datos --uno` | `nuevo pantalla producto --datos producto --uno` | `app/producto/[id]`: toma el id de la ruta con `useLocalSearchParams` y usa `obtener(id)`. Se abre con `router.push('/producto/3')`. |
| `pantalla --datos --form` | `nuevo pantalla editar-producto --datos producto --form` | El formulario (`TextInput`, `Switch`) con `useFormulario`: para crear, `router.push('/editar-producto')`; para editar, con `?id=3`. Al guardar vuelve atrás. Con un servicio `--solo crear`, solo envía: se queda en la pantalla y muestra «¡Listo! Se envió.». |
| `componente` | `nuevo componente Tarjeta` | `components/Tarjeta` con su `StyleSheet`. |
| `hook` | `nuevo hook contador` | `hooks/useContador`. |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `services/productoService` (y `http`, que explica qué IP usar, y los hooks `useConsulta` y `useFormulario`, si faltan). |
| `tema` | `nuevo tema violeta --modo auto` | `constants/tema`: los colores del modo claro y del oscuro y `useTema()`, que devuelve los del modo actual. |

---

## Next.js (frontend) — `next`

```
python -m andamio crear next mi-web              (con --js, en JavaScript)
cd mi-web
npm install
npm run dev                                      http://localhost:3000
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `componente` | `nuevo componente Tarjeta` | `components/Tarjeta/`. |
| `pagina` | `nuevo pagina Contacto` | `app/contacto/page` (la carpeta es la ruta) y el enlace en `app/layout`. |
| `hook` | `nuevo hook contador` | `hooks/useContador`. |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `services/productoService`. |
| `crud` | `nuevo crud producto nombre:str precio:decimal stock:int` | `app/productos/` (lista, `nuevo`, `[id]`, `[id]/editar`), el detalle, el hook y el servicio. |
| `tema` | `nuevo tema violeta --modo auto` | Las variables CSS del proyecto (colores, letra, bordes, sombras, modo oscuro) y estilos base, en `app/tema.css`, cargado en `app/layout`. |
| `ui` | `nuevo ui tarjetas` | Una parte lista en `app/ui/`: tarjetas, alertas, modal, navbar, badges, tabs, paginacion, cargando, responsive o accesible. |
| `estilo` | `nuevo estilo catalogo` | `app/estilos/catalogo.css` con la clase `.catalogo` armada con las variables del tema, para tu componente o página. |

## Next.js full stack — `next-fullstack`

Lo mismo que `next` (incluidos `tema`, `ui` y `estilo`), más la pieza `recurso`:

| Pieza | Comando | Qué genera |
|---|---|---|
| `recurso` | `nuevo recurso producto nombre:str precio:decimal stock:int --migrar` | La API en `app/api/productos/` (Route Handlers con Prisma y Zod), con el mismo contrato que las otras APIs, y 5 tests. |

---

## Reflex (web solo con Python) — `reflex`

```
python -m andamio crear reflex mi-app
cd mi-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
reflex run                                       http://localhost:3000
```

| Pieza | Comando | Qué genera |
|---|---|---|
| `crud` | `nuevo crud producto nombre:str precio:decimal stock:int --migrar` | El modelo (SQLModel) en su propia base y la página para listar, agregar, editar y eliminar. |
| `crud-api` | `nuevo crud-api cliente nombre:str email:email` | La misma página con los datos de una API de andamio. |
| `pagina` | `nuevo pagina Contacto` | `mi_app/paginas/contacto.py`, registrada con su ruta y su enlace. |
| `componente` | `nuevo componente Tarjeta` | `mi_app/componentes/tarjeta.py`. |
| `estado` | `nuevo estado contador` | `mi_app/estados/contador.py` (`ContadorState`). |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `mi_app/servicios/producto.py` (funciones async). |
| `tema` | `nuevo tema violeta --modo auto` | `mi_app/tema.py` con el tema de Radix (color de acento, claro u oscuro), conectado en `rxconfig.py` (`RadixThemesPlugin(theme=TEMA)`). |

---

## Otros comandos

| Comando | Qué hace |
|---|---|
| `python -m andamio` | Menú interactivo: te pregunta todo, paso a paso. |
| `python -m andamio info` | Qué proyecto detectó, qué piezas y qué tipos de campo hay. |
| `python -m andamio init [tipo]` | Prepara un proyecto que ya existe, aunque no lo haya creado andamio: muestra qué puntos de conexión (`andamio:rutas`, `andamio:imports`...) tiene y cuáles faltan, con la línea a pegar y dónde, y crea `andamio.json`. No modifica tu código. |
| `python -m andamio mapa` | Las piezas que se generaron en el proyecto (según `.andamio/historial.jsonl`), si sus archivos y sus conexiones siguen en su lugar, y si una API y su interfaz tienen campos distintos. En inglés: `map`. |
| `python -m andamio pendientes` | Lista las marcas `TODO(logica)` del proyecto: archivo, línea y qué falta. Son los lugares donde va tu lógica (validaciones, reglas, cálculos). En inglés: `todo`. |
| `python -m andamio comandos` | El árbol de todos los comandos, opciones y piezas (en inglés: `commands`). |
| `python -m andamio plantillas exportar [pieza]` | Copia las plantillas a `.andamio/plantillas/` para modificar el código que se genera. |
| `python -m andamio configurar` | Opcional: permite escribir solo `andamio` (agrega la carpeta al PATH). |
| `python -m andamio --version` | La versión instalada. |

---

## andamio.json: la configuración del proyecto (opcional)

Sin este archivo, andamio detecta el tipo de proyecto por sus archivos y funciona como
siempre. Se crea con `python -m andamio init` (o a mano) en la carpeta del proyecto:

```json
{
  "version": 1,
  "stack": "react",
  "variante": "ts",
  "guia": true,
  "plantillas": ".andamio/plantillas",
  "conexiones": { "rutas": "src/router/AppRouter.tsx", "imports": "src/router/AppRouter.tsx" }
}
```

| Clave | Qué hace |
|---|---|
| `stack` | El tipo de proyecto (como en `crear`). La carpeta de `andamio.json` pasa a ser la raíz del proyecto, aunque las carpetas no sean las de siempre. |
| `variante` | `ts` o `js` (Express, React, React Native, Next.js). |
| `guia` | `false`: genera sin los comentarios que explican el código, como `--sin-guia`. |
| `plantillas` | La carpeta de las plantillas propias (por defecto `.andamio/plantillas`), por ejemplo las de la cátedra. |
| `conexiones` | En qué archivo está cada punto de conexión, si no es el de siempre. La clave es la del marcador: `rutas` es `andamio:rutas`. `init` muestra cuáles usa cada pieza. |

Lo que indiques al ejecutar (por ejemplo `--sin-guia`) tiene prioridad sobre `andamio.json`.

## El código generado: guía, TODO(logica) y mapa de lectura

- **Guía:** los archivos principales empiezan con un comentario que explica qué hacen y
  con qué otros archivos se conectan. `--sin-guia` (o `"guia": false`) los omite.
- **`TODO(logica)`:** marca dónde va tu lógica (validaciones, reglas al guardar), con un
  ejemplo comentado. Al generar, andamio muestra dónde quedaron; después,
  `python -m andamio pendientes` las lista. Cuando escribas esa lógica, borrá la marca.
- **Mapa de lectura:** al generar, andamio muestra en qué orden conviene leer los archivos
  y qué hace cada uno.
- **Archivos `.http`:** las APIs traen `http/<plural>.http` con peticiones de ejemplo
  (listar, crear, ver, modificar y eliminar) para probarlas con la extensión REST Client
  de VS Code, sin programas aparte.
