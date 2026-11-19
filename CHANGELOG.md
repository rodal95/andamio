# Cambios

Este proyecto usa [versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado
- Núcleo: motor de plantillas `@@marcador@@`, detección del proyecto, normalización
  de nombres, inserción en archivos existentes con marcadores y escritura segura
  (valida antes de escribir, nunca sobrescribe, deshace si algo falla).
- Comandos `crear`, `nuevo`, `info`, `--simular`, `--version` y menú interactivo.
- Stack `python`: aplicación de consola con SQLite y pieza `entidad`.
