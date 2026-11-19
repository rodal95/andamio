"""Tema de la aplicación (lo generó: python -m andamio nuevo tema @@nombre@@ --modo @@modo@@).

Reflex usa los temas de Radix: el color de acento tiñe botones, enlaces y campos, y
appearance elige claro, oscuro o "inherit" (el del sistema). Lo usa rxconfig.py
(RadixThemesPlugin(theme=TEMA)). Para cambiarlo: editá los valores de abajo.

Colores de acento: tomato, red, ruby, crimson, pink, plum, purple, violet, iris, indigo,
blue, cyan, teal, jade, green, grass, brown, orange, sky, mint, lime, yellow, amber,
gold, bronze, gray.
"""

import reflex as rx

TEMA = rx.theme(
    accent_color="@@acento_radix@@",
    appearance="@@apariencia@@",
    radius="medium",  # none, small, medium, large o full
    scaling="100%",
)
