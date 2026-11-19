# Cambios

Todos los cambios importantes de andamio. El proyecto usa
[versionado semántico](https://semver.org/lang/es/): MAYOR.MENOR.PARCHE.

## [Sin publicar]

## [1.3.0] - 2026-11-19

### Agregado
- React, Vue y Next.js: el `http` que generan `servicio` y `crud` manda el token del
  login JWT si hay uno guardado (`Authorization: Bearer <token>`), así el `crud`
  funciona con los recursos `--protegido` de Django. Trae `guardarToken()`,
  `borrarToken()` y `leerToken()` (la misma clave `token` en `localStorage` que la web
  HTML). Receta con la página de ingreso en `docs/guias/combinaciones.md`.

- Comandos, piezas y opciones en inglés: `create`, `new` (también `generate` y
  `g`), `commands`, `templates export`, `configure`; `entity`, `resource`,
  `component`, `page`, `screen`, `service`, `state`; `--dry-run`, `--variant`,
  `--migrate`, `--protected`, `--folder`. Hacen lo mismo que en español.
- `python -m andamio comandos` (`commands`): el árbol de todos los comandos con sus
  opciones y las piezas de cada tecnología, armado a partir del código.

### Cambiado
- Los errores de la API muestran su explicación (`detail`) en lugar de "La API
  respondió con el error 401": por ejemplo, "Las credenciales de autenticación no se
  proveyeron.".

## [1.2.0] - 2026-11-19

### Agregado
- Stack `web`: página con HTML, CSS y JavaScript, sin instalar nada (ni Node ni npm),
  con piezas `pagina` (un `.html` con su `.js` y el enlace en el menú), `componente`
  (una función que crea un elemento, con su CSS), `servicio` y `crud` (tabla y
  formulario contra una API de andamio, con los errores de validación por campo).
  `js/http.js` manda el token del login JWT si hay uno guardado. Se sirve con
  `python -m http.server 5173` (el puerto que las APIs ya aceptan).
- Stack `vue`: Vue 3 + Vite + Vue Router, con piezas `componente`, `pagina`,
  `composable`, `servicio` y `crud` (lista, detalle y formulario con `v-model` y sus
  cuatro rutas), compatible con las APIs de Django, FastAPI, Express y Next.js.
- Stack `django-web`: la otra forma de usar Django, un sitio con plantillas HTML
  (monolito) con login, registro, salir y admin. `crud` genera la app con modelo,
  `ModelForm`, cinco vistas genéricas (lista con búsqueda y páginas, detalle, crear,
  editar y eliminar), sus plantillas, rutas con nombre, admin y tests, y el enlace en
  el menú; `pagina` una plantilla con su ruta. Acepta `--migrar` y `--protegido`.
- Django REST: pieza `login` (`python -m andamio nuevo login`, sin nombre) con
  SimpleJWT: `/api/token/`, `/api/token/refresh/`, `/api/token/verify/`,
  `/api/registro/` y `/api/yo/`, 6 tests, mensajes en español y el botón Authorize en
  Swagger. Opción `--protegido` en `recurso`: leer es libre; crear, modificar y
  eliminar piden login (`IsAuthenticatedOrReadOnly`), con sus tests.
- Guías en `docs/guias/`: todos los comandos por tecnología, cómo combinar piezas y
  proyectos (página + servicio en HTML, Vue y React; login JWT desde la web), reglas
  para no romper nada, API REST con Django + JWT paso a paso y sitio con Django y
  plantillas paso a paso.
- Sitio: guías de HTML, Vue y Django con plantillas (con sus combinaciones probadas
  en los tests) y la lección del login en la de Django REST. El menú de la barra pasa
  a ser un desplegable agrupado (API, interfaz, todo en uno), que también funciona
  en el celular.

### Cambiado
- El menú interactivo pregunta "¿Proteger el recurso?" en las piezas que aceptan
  `--protegido`, y no pide nombre en las que no lo necesitan (`login`). Los números
  del menú para crear un proyecto cambiaron (se agregaron tres tipos).

## [1.1.0] - 2026-11-19

### Agregado
- Stack `fastapi`: API REST con FastAPI + SQLModel (`python -m andamio crear
  fastapi mi-api`) y pieza `recurso` con modelo, router y 5 tests. Cumple el
  mismo contrato que la API de Django (rutas `/api/productos/`, lista sin
  paginación, decimales como número, errores 400 en español por campo,
  `?search=`, `?ordering=` y filtros), así que los servicios y el `crud` de
  React y React Native funcionan igual con las dos. Las fechas con hora sin
  zona horaria se toman como hora local (`ZONA_HORARIA` en el `.env`), como
  en Django.
- Stack `express`: API REST con Express 5 + Prisma 7 (SQLite) + Zod, en
  TypeScript o JavaScript (`python -m andamio crear express mi-api --js`), y
  pieza `recurso` con el modelo en `prisma/schema.prisma`, la validación (con
  los mensajes en español de Django), las rutas y 5 tests (`npm test`, con su
  propia base `test.db`). Mismo contrato y mismo puerto (8000) que Django y
  FastAPI; Swagger en `/docs` sin internet. `--migrar` ejecuta
  `npx prisma migrate dev`.
- Stacks de Next.js 16 (App Router), en TypeScript o JavaScript:
  - `next`: frontend que usa una API hecha con andamio, con piezas `componente`,
    `pagina`, `hook`, `servicio` y `crud` (lista, detalle y formulario en sus
    carpetas de `app/`, y el enlace en el menú).
  - `next-fullstack`: lo mismo más su propia API y base de datos. La pieza
    `recurso` crea los Route Handlers en `app/api/<recurso>/` con Prisma y Zod,
    con el mismo contrato que las otras APIs (también la puede usar React
    Native), 5 tests (`npm test`) y `--migrar`. `proxy.ts` habilita CORS.
- Un stack puede extender a otro (`Stack.extiende`) y reutilizar sus plantillas.
- Sitio: cada guía tiene un índice lateral que sigue la línea (empezar, una lección
  por pieza con el router y las rutas explicadas, combinaciones y referencia), y
  termina con recetas para combinar piezas (un servicio en una página, un componente
  con datos, un hook propio, enlazar páginas) cuyo código se compila en los tests.
  La portada se ordenó: qué es, cómo funciona (proyecto y piezas), instalar y las
  tecnologías agrupadas según lo que se construye.
- Stack `reflex` (Reflex 0.11, web hecha solo con Python; pide Python 3.11+): piezas
  `crud` (tabla con SQLModel en su propia base, migraciones con `reflex db` y
  `--migrar`, y una página para listar, agregar, editar y eliminar con los errores
  de validación en español), `crud-api` (la misma página con los datos de una API
  de andamio), `pagina`, `componente`, `estado` y `servicio`. Los proyectos no
  envían datos de uso (telemetría) y dejan el puerto 8000 libre para las APIs.
- Pieza `crud` para React: `python -m andamio nuevo crud producto <campos>`
  genera la lista, el detalle (con eliminar) y el formulario para crear y
  editar (con los errores de validación de la API en cada campo), el
  componente `ProductoDetalle` (muestra y avisa, no llama a la API), el hook
  genérico `useConsulta` y el servicio, y registra las rutas y el enlace en
  `App`. Funciona en TypeScript y JavaScript.
- Los proyectos React traen `react-router` (7.x, compatible con Node 20):
  `App` tiene el menú y las rutas, y la página de inicio pasa a
  `src/pages/InicioPage/`. `nuevo pagina` registra también su ruta y su enlace.
- Se rechaza una página o un CRUD si su ruta ya existe en `App`. En proyectos
  sin router, andamio genera igual e indica el `npm install` y qué pegar.
- Test en el navegador (Playwright) del CRUD generado (React, Next.js y Reflex) contra
  las APIs de Django, FastAPI, Express y Next.js full stack.
- `python -m andamio configurar`: agrega la carpeta de andamio al PATH del
  usuario (sin permisos de administrador) para poder escribir solo `andamio`.
  En Linux y Mac explica qué línea agregar. Es opcional.

### Cambiado
- Las APIs (Django, FastAPI y Express) aceptan por defecto pedidos de
  `localhost:3000` (Next.js), además de Vite y Expo.
- Los servicios y el `crud` de React y React Native ya no hablan solo de
  Django: los comentarios y los `.env` explican cómo usarlos con cualquiera
  de las tres APIs.
- Todos los mensajes, la ayuda y los README de los proyectos generados
  muestran los comandos con Python adelante (`python -m andamio ...`, o
  `python andamio.pyz ...` si se usa el .pyz), que funciona en cualquier PC.
- La instalación se documenta con `python -m pip`, que funciona también con
  el Python de la Microsoft Store (que no trae `py`).

## [1.0.0] - 2026-11-19

Primera versión.

### Agregado
- Comandos `crear`, `nuevo`, `info`, `plantillas exportar` y `--version`, con
  `--simular` para ver los cambios sin escribir nada, y un menú interactivo
  (`andamio` solo) que pide cada dato, lo valida y confirma antes de escribir.
- Núcleo: detección del tipo de proyecto subiendo por las carpetas, nombres
  normalizados (tildes, ñ, snake/Pascal/camel/kebab) con plural en castellano,
  motor de plantillas `@@marcador@@` y escritura segura (valida todo antes,
  nunca sobrescribe, deshace los cambios si algo falla y explica qué pegar a
  mano si falta una línea marcador).
- Stack `python`: aplicación de consola con SQLite y pieza `entidad`.
- Stack `django`: API REST con Django 5.2 LTS + Django REST Framework, `.env`,
  CORS, Swagger en `/api/docs/` (sin internet) y pieza `recurso` con modelo,
  serializer, ViewSet, rutas, admin y 5 tests. Opción `--migrar`.
- Stack `react`: React 19 + Vite 8, con piezas `componente`, `pagina`, `hook`
  y `servicio` (CRUD contra la API de Django).
- Stack `react-native`: Expo SDK 58 + Expo Router, con piezas `pantalla`
  (opción `--carpeta`, admite grupos como `(tabs)`), `componente`, `hook` y
  `servicio`.
- Variantes TypeScript y JavaScript para React y React Native
  (`andamio crear react mi-web --js`). En proyectos existentes la variante se
  detecta sola (por `tsconfig.json` o la dependencia `typescript`); los
  servicios en JavaScript llevan tipos en comentarios JSDoc.
- Plantillas editables por proyecto en `.andamio/plantillas/`, con un
  `LEEME.md` por pieza que lista los marcadores y sus valores de ejemplo.
- Distribución: `.whl`, `andamio.pyz` (un solo archivo, sin instalar) y `.zip`
  en cada Release.
- Licencia MIT.

[Sin publicar]: https://github.com/rodal95/andamio/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/rodal95/andamio/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/rodal95/andamio/releases/tag/v1.0.0
