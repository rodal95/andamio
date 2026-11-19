# Cambios

Todos los cambios importantes de andamio. El proyecto usa
[versionado semántico](https://semver.org/lang/es/): MAYOR.MENOR.PARCHE.

## [Sin publicar]

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

[Sin publicar]: https://github.com/rodal95/andamio/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/rodal95/andamio/releases/tag/v1.0.0
