# Cambios

Todos los cambios importantes de andamio. El proyecto usa
[versionado semántico](https://semver.org/lang/es/): MAYOR.MENOR.PARCHE.

## [Sin publicar]

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
- Test en el navegador (Playwright) del CRUD generado (React y Next.js) contra las
  APIs de Django, FastAPI, Express y Next.js full stack.
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
