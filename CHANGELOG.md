# Cambios

Todos los cambios importantes de andamio. El proyecto usa
[versionado semántico](https://semver.org/lang/es/): MAYOR.MENOR.PARCHE.

## [Sin publicar]

### Agregado
- `andamio-guia.html` en cada proyecto: una página para abrir en el navegador con el tipo
  de proyecto, cómo ponerlo en marcha, lo que ya se generó (con sus archivos y si sigue
  conectado), dónde va la lógica propia (`TODO(logica)`), cada pieza que se puede generar
  (forma general, ejemplo, opciones y qué archivos crea) y los puntos de conexión. Se crea
  con `crear`, se actualiza sola con cada `nuevo` (no con `--simular`) y va en `.gitignore`.
  En los proyectos creados antes, `init` la crea (y la suma al `.gitignore`).
- Sitio: pestaña "Paso a paso" en React, React Native, Django y Python + SQLite: todos los
  comandos en su forma general y con un ejemplo, y un proyecto armado comando por comando,
  con la consola animada, el proyecto que crece, el código nuevo resaltado y una
  demostración que se puede usar (la app, la API o la consola).
- `crear <tipo> .`: crea el proyecto en la carpeta actual, sin crear otra ni tener que
  entrar después (`cd`). El nombre del proyecto es el de la carpeta. La carpeta tiene que
  estar vacía (se permiten `.git`, `.vscode` y `LICENSE`). En el menú, `.` como nombre.
- Instalación en Linux: si pip responde `externally-managed-environment` (Ubuntu, Debian),
  el README y la página explican cómo instalarlo con pipx.
- React: `nuevo pagina <Nombre> --datos <servicio>` genera una página que muestra los datos
  de un servicio que ya existe: `useConsulta(productoService.listar)`, con cargando, error y
  lista vacía. Con `--uno`, muestra uno solo: la ruta lleva el id (`/producto-detalle/:id`),
  usa `obtener(id)`, muestra los campos con que se generó el servicio y no va en el menú.
  En el menú interactivo, la pieza `pagina` lo pregunta. Así, una página con datos no
  necesita un `crud` entero ni escribir el `useEffect` a mano.
- React: `nuevo servicio` también crea el hook `useConsulta` (si falta), que antes venía
  solo con el `crud`.
- React Native: lo mismo con `nuevo pantalla <nombre> --datos <servicio>`: una `FlatList`
  con `useConsulta`, cargando y error. Con `--uno` crea `app/<nombre>/[id]` y toma el id con
  `useLocalSearchParams`. `nuevo servicio` también crea `hooks/useConsulta` (si falta).
- React y React Native: `--form` (con `--datos`) genera el formulario para crear y editar,
  con el hook nuevo `useFormulario`: carga el registro si hay un id, guarda con `crear` o
  `actualizar` y deja los errores de la API por campo. En React la página queda en
  `/producto-editar` (crear) y `/producto-editar/:id` (editar); en React Native, la pantalla
  edita si se abre con `?id=3` y al guardar vuelve atrás. Necesita los campos del servicio
  (del historial). `servicio` también crea `useFormulario` (si falta).

- Relaciones: el tipo de campo `fk` (`categoria:fk`) relaciona la pieza con otra que ya
  existe y se llama igual que el campo. Es opcional: si se borra la categoría, el producto
  queda sin categoría.
  - Django (`recurso`): `ForeignKey` con `SET_NULL`; la API devuelve además
    `categoria_texto`, filtra con `?categoria=3` y usa `select_related`.
  - Python + SQLite (`entidad`): la columna `categoria_id` con `REFERENCES ... ON DELETE SET
    NULL`; `listar()` hace un `LEFT JOIN` para mostrar el nombre, y el menú muestra las
    categorías y pide un id que exista.
  - React y React Native: el servicio tiene `categoria: number | null` (y `categoria_texto`);
    el formulario (`crud` o `--form`) la elige de la lista de `categoriaService` (un
    `<select>` en React, opciones para tocar en React Native) y el detalle muestra su texto.

- Python + SQLite:
  - `entidad --sin-menu` (`--no-menu`): solo la tabla y las funciones, sin el menú de
    consola.
  - `nuevo menu <entidad>`: el menú de consola de una entidad que ya existe (con los campos
    con que se generó) y su opción en el menú principal.
  - `nuevo busqueda <entidad> <campo>...` (`search`): `buscar_por_<campo>(valor)` en la
    entidad (`LIKE` en los textos, `=` en los números) y su opción en el menú. Repetirla no
    duplica nada.
  - El menú de cada entidad tiene dos líneas nuevas (`andamio:opciones` y `andamio:acciones`)
    donde `busqueda` agrega sus opciones. En los menús generados antes, andamio muestra qué
    pegar y dónde.
- Django:
  - `nuevo accion <recurso> <acción>...` (`action`): un `@action` en el ViewSet que ya
    existe (`POST /api/productos/3/destacar/`) con la marca `TODO(logica)`, su test y su
    petición en el `.http`. Repetirla no duplica nada.
  - `recurso --solo-lectura` (`--read-only`): un `ReadOnlyModelViewSet` (listar y ver; los
    datos se cargan desde `/admin/`), con un test que controla el 405.
  - Las vistas y los tests del recurso tienen líneas `andamio:imports`, `andamio:acciones` y
    `andamio:tests`, donde `accion` agrega lo suyo. En los recursos generados antes, andamio
    muestra qué pegar y dónde.
- Piezas: `preparar` (lo que el ejemplo de una pieza necesita que exista antes, para los
  tests y el sitio), `define_campos` (`mapa` no compara los campos de una búsqueda o de una
  acción) y `usa_existente` (la pieza agrega a una que ya existe: no se controla que el
  nombre esté libre). En el menú, `busqueda` y `accion` piden solo nombres, sin tipo.

### Cambiado
- React: el formulario del `crud` usa `useFormulario` (la lógica de cargar, guardar y
  mostrar los errores está en el hook, no repetida en cada formulario).

### Corregido
- React: `nuevo pagina ProductoLista` después de `nuevo crud producto` (o un `crud` después
  de una página con el mismo componente) generaba dos `ProductoListaPage` en `src/App` y el
  proyecto no compilaba. Ahora andamio lo rechaza y explica por qué.

## [1.5.0] - 2026-11-20

### Agregado
- Archivos `.http` para probar las APIs a mano, sin programas aparte (extensión REST Client
  de VS Code, o el cliente HTTP de PyCharm y WebStorm): `recurso` genera
  `http/<plural>.http` (Django, FastAPI, Express y Next.js full stack) con listar, buscar,
  crear, ver, reemplazar, modificar y eliminar, y datos de ejemplo según los campos. Con
  `--protegido`, primero pide el token. `nuevo login` genera `http/login.http`
  (registrarse, pedir el token, usuario actual y renovar el token).
- Mapa de lectura: después de generar una pieza, andamio muestra en qué orden leer los
  archivos y qué hace cada uno (en los recursos, crud, páginas, servicios y entidades).
- Código guiado: los archivos principales empiezan con una explicación de qué hacen y con
  qué se conectan, y marcan con `TODO(logica)` dónde va la lógica propia (validaciones y
  reglas al guardar), con un ejemplo comentado. Al generar, andamio muestra esas marcas.
  `--sin-guia` (`--no-guide`), en `crear` y `nuevo`, genera sin las explicaciones (las
  marcas quedan). En las plantillas, una guía es una línea de comentario que empieza con
  `guía:`.
- `python -m andamio pendientes` (`todo`): lista las marcas `TODO(logica)` del proyecto,
  con archivo, línea y qué falta.
- `andamio.json` (opcional): fija el tipo de proyecto y su raíz (útil si las carpetas no
  son las de siempre o hay varios proyectos juntos), la variante, si se genera con guía, la
  carpeta de las plantillas propias y `conexiones`: en qué archivo está cada punto de
  conexión (ej.: las rutas de React en `src/router.tsx`). Sin el archivo, todo funciona
  como antes. `crear --sin-guia` lo crea con `"guia": false`.
- `python -m andamio init [tipo]`: prepara un proyecto que ya existe, aunque no lo haya
  creado andamio. Muestra qué puntos de conexión tiene y cuáles faltan (con la línea a
  pegar y dónde) y crea `andamio.json`. No modifica el código del proyecto.
- `python -m andamio mapa` (`map`): las piezas que se generaron en el proyecto, si sus
  archivos y sus conexiones (rutas, imports, menú) siguen en su lugar, y si una API y su
  interfaz tienen campos distintos. Cada `nuevo` anota lo que generó en
  `.andamio/historial.jsonl` (en el mismo paso que la pieza: si algo falla, se deshace).

### Corregido
- Nombres que generaban código que no compilaba o no funcionaba. Ahora andamio los
  rechaza y explica por qué, o los acepta porque las plantillas ya no chocan con ellos:
  - Cualquier pieza: si el nombre es una variable, una función o un import que el código
    generado ya usa en el mismo archivo (ej.: `nuevo recurso filtro` en Express, `nuevo crud
    error` en Vue, `nuevo pagina app` o `plantilla` en Reflex). Se controla solo, también con
    las plantillas que exportó el docente.
  - `None`, `True` y `False` (palabras reservadas de Python) y los nombres que Windows no
    deja usar en archivos y carpetas (`con`, `aux`, `nul`...).
  - Reflex: un proyecto con el nombre de un módulo de Python (`email`, `random`...).
  - Web: campos que repetían un `id` de la página del crud (`estado`, `filas`...).
  - Django con plantillas: un crud cuya ruta ya usaba una página (`/productos/`).
- Nombres comunes que antes chocaban con variables internas y ahora se pueden usar:
  `sesion` (FastAPI y Reflex), `orden` y `respuesta` (Express y Next.js), `registro`
  (Reflex) y `respuesta` (Django con plantillas).
- Django: si ya hay una app `cuentas` (ej.: un recurso `cuenta`), `nuevo login` sugiere
  otro nombre (`nuevo login acceso`) en lugar de un `--plural` que no acepta, y el menú
  pregunta el nombre del login.
- `plantillas exportar` ya no vuelve a crear los archivos que se borraron a propósito de una
  pieza exportada (las piezas ya exportadas no se tocan).
- Next.js full stack: la pista del `crud` incluye el `--plural` cuando no es el automático.
- `configurar` dentro de un entorno virtual ya no agrega la carpeta del venv al PATH.
- `theme`, `style` y `--mode light|dark` en inglés.
- El workflow de releases instala SimpleJWT, así los tests del login no se saltean.

### Agregado (tests)
- Barrido de nombres (`tests/integracion/test_barrido.py`, con `--lento`): prueba cada
  identificador de las plantillas como nombre y como campo de cada pieza, y compila lo
  generado (Python con `ast`; JavaScript, TypeScript y Vue con el compilador de TypeScript).
- `test_python_generado.py`: el Python que genera cada pieza no usa nombres sin definir
  (compila igual pero falla al ejecutar) ni define dos veces el mismo, con y sin guía.

## [1.4.1] - 2026-11-19

### Cambiado
- Sitio: cada guía está en pestañas (Empezar, Comandos, Estilos, Proyecto completo,
  Combinaciones, Todos los comandos, Problemas). En Comandos y Estilos, una sub-pestaña
  por pieza con la forma general, el comando con lo que muestra la consola, el código
  que arma (archivo por archivo) y todas sus variantes. Proyecto completo arma un
  proyecto entero con los comandos, ejecutados de verdad. La dirección recuerda la
  pestaña (`vue.html#comandos/crud`) y los enlaces viejos siguen andando.
- Sitio, buscadores y redes: descripciones nuevas de cada guía (y sus imágenes para
  compartir), datos estructurados de artículo técnico y ruta de navegación en cada guía,
  y el título del navegador según la pestaña (`CRUD · andamio con Vue`).

## [1.4.0] - 2026-11-19

### Agregado
- Piezas de estilos en web, Django con plantillas, Vue, React y Next.js:
  - `nuevo tema [<color>] [--modo auto|claro|oscuro]`: variables CSS (colores, letra,
    bordes, sombras) con modo oscuro y estilos base de botones, formularios y tablas,
    cargadas en todo el proyecto. Lo generado por `crud` y `pagina` cambia de look sin
    tocarlo. Nueve colores; `--modo` (`--mode`) elige claro, oscuro o el del sistema.
  - `nuevo ui <parte>`: tarjetas, alertas, modal, navbar, badges, tabs, paginacion,
    cargando, responsive y accesible, en CSS sin librerías, con el ejemplo de uso en el
    archivo.
  - `nuevo estilo <nombre>`: el CSS de tu componente o página, con las variables del
    tema y ya conectado.
- `tema` también en React Native (colores claro y oscuro y `useTema()`) y en Reflex
  (`rx.theme` con el color y el modo).
- Reflex: el tema del proyecto pasa a `rxconfig.py` (`RadixThemesPlugin(theme=TEMA)`)
  en lugar de `rx.App(theme=...)`, que Reflex marca como obsoleto desde la 0.9.
- `andamio comandos` muestra la forma general de cada pieza (`nuevo crud <nombre>
  <campo:tipo>...`) además del ejemplo. Guía nueva: `docs/guias/estilos.md`.

### Cambiado
- El CSS base de la web HTML, Django con plantillas y Vue usa las variables del tema
  (`--superficie`, `--acento-texto`), así el modo oscuro también cambia botones y fondos.
- Las líneas marcador `andamio:estilos` en `templates/base.html` (Django con
  plantillas), `src/main` (React y Vue) y `app/layout` (Next.js). En proyectos creados
  antes, andamio indica qué línea pegar.

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
- Sitio: al compartir un enlace (WhatsApp, Facebook, LinkedIn, X, Discord, Slack) se ve
  una vista previa con el logo, el título y comandos de la guía. Cada página tiene su
  imagen (1200x630), etiquetas Open Graph y Twitter Card, dirección canónica, íconos
  PNG del logo (también para la pantalla de inicio del celular), `site.webmanifest`,
  `sitemap.xml` y, en la portada, datos estructurados para buscadores. Los genera
  `scripts/compartir_sitio.py`.

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
