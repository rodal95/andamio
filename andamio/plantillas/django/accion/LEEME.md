# Pieza accion

No tiene archivos propios: agrega a un recurso que ya existe.

- En `<plural>/views.py`: los import de `action` y `Response` (antes de la línea
  `andamio:imports`) y el `@action` al final del ViewSet (antes de `andamio:acciones`).
- En `<plural>/tests.py`: un test por acción (antes de `andamio:tests`).
- En `http/<plural>.http`: la petición para probarla, al final.

El código se arma en `andamio/stacks/django.py` (`_contexto_accion`).
