# Cambios

Este proyecto usa [versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado
- Núcleo: motor de plantillas `@@marcador@@`, detección del proyecto, normalización
  de nombres, inserción en archivos existentes con marcadores y escritura segura
  (valida antes de escribir, nunca sobrescribe, deshace si algo falla).
- Comandos `crear`, `nuevo`, `info`, `--simular`, `--version` y menú interactivo.
- Stack `python`: aplicación de consola con SQLite y pieza `entidad`.
- Stack `django`: API REST con Django 5.2 LTS + DRF, configuración por `.env`,
  Swagger en `/api/docs/` (funciona sin internet) y pieza `recurso` con modelo,
  serializer, ViewSet, rutas, admin y 5 tests. Opción `--migrar`.
- Stack `react`: React 19 + Vite 8 + TypeScript, con piezas `componente`,
  `pagina`, `hook` y `servicio` (CRUD tipado contra la API de Django).
- Stack `react-native`: Expo SDK 58 + Expo Router + TypeScript, con piezas
  `pantalla` (opción `--carpeta`, admite grupos como `(tabs)`), `componente`,
  `hook` y `servicio`.
- Tests `--lento`: instalan y compilan los proyectos generados y prueban los
  servicios de React y React Native contra la API generada en Django.
