# Pieza busqueda

No tiene archivos propios: agrega funciones a una entidad que ya existe.

- En `entidades/<nombre>.py`, al final: `buscar_por_<campo>(valor)`.
- En `menus/menu_<nombre>.py`: la opción del menú (antes de las líneas `andamio:opciones` y
  `andamio:acciones`) y la función que pide el valor y muestra los resultados (al final).

El código se arma en `andamio/stacks/python.py` (`_contexto_busqueda`).
