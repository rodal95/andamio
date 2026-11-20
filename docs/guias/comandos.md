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
│     --simular            (--dry-run)              muestra qué crearía, sin tocar nada
│     --variante ts|js     (--variant)              lenguaje (Express, React, React Native, Next.js)
│     --js / --ts                                   atajos de --variante
│
├── nuevo <pieza> [nombre] [campos...]   (new, generate, g)   agrega una pieza al proyecto actual
│     --plural <plural>                             el plural, si el automático no sirve
│     --simular            (--dry-run)              muestra qué crearía o modificaría
│     --migrar             (--migrate)              crea y aplica la migración
│     --protegido          (--protected)            crear, modificar y eliminar piden login
│     --carpeta <carpeta>  (--folder)               subcarpeta de app/ (React Native)
│     --modo auto|claro|oscuro  (--mode)            modo del tema (pieza tema)
│
├── info                                            qué proyecto detectó y qué piezas acepta
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
| `--plural`, `--simular` | todas (`--plural` solo en las que usan plural) |

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
| `plantillas exportar` | `templates export` |
| `configurar` | `configure`, `setup` |
| `entidad`, `recurso`, `componente`, `pagina`, `pantalla`, `servicio`, `estado`, `tema`, `estilo` | `entity`, `resource`, `component`, `page`, `screen`, `service`, `state`, `theme`, `style` |
| `--simular`, `--variante`, `--migrar`, `--protegido`, `--carpeta`, `--modo` | `--dry-run`, `--variant`, `--migrate`, `--protected`, `--folder`, `--mode` |
| `--modo claro`, `--modo oscuro`, `--modo auto` | `--mode light`, `--mode dark`, `--mode auto` |

`crud`, `crud-api`, `login`, `hook`, `composable`, `ui` e `info` son iguales en los dos idiomas.

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
| `--migrar` | Después de generar, crea y aplica la migración (Django, Django con plantillas, Express, Next.js full stack, Reflex). |
| `--protegido` | Crear, modificar y eliminar piden login (Django y Django con plantillas). |
| `--carpeta productos` | Crea la pantalla dentro de una carpeta de `app/` (React Native). |
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

```python
from entidades import producto

nuevo_id = producto.crear("Yerba", 1500.0, 10)
for fila in producto.listar():
    print(fila["nombre"], fila["precio"])
```

Tipos: `str`, `int`, `float`.

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
| `hook` | `nuevo hook contador` | `src/hooks/useContador`. |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `src/services/productoService` (y `http`, si falta). |
| `crud` | `nuevo crud producto nombre:str precio:decimal stock:int` | Lista, detalle y formulario en `src/pages/productos/`, el componente `ProductoDetalle`, el hook `useConsulta`, el servicio y las 4 rutas con su enlace. |
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
| `componente` | `nuevo componente Tarjeta` | `components/Tarjeta` con su `StyleSheet`. |
| `hook` | `nuevo hook contador` | `hooks/useContador`. |
| `servicio` | `nuevo servicio producto nombre:str precio:decimal stock:int` | `services/productoService` (y `http`, que explica qué IP usar). |
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
| `python -m andamio comandos` | El árbol de todos los comandos, opciones y piezas (en inglés: `commands`). |
| `python -m andamio plantillas exportar [pieza]` | Copia las plantillas a `.andamio/plantillas/` para modificar el código que se genera. |
| `python -m andamio configurar` | Opcional: permite escribir solo `andamio` (agrega la carpeta al PATH). |
| `python -m andamio --version` | La versión instalada. |
