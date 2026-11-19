"""La plantilla de todas las páginas: el menú arriba y el contenido abajo."""

import reflex as rx

# Las páginas del menú: (texto, dirección). andamio agrega una por cada página que generes.
ENLACES = [
    ("Inicio", "/"),
    # --- andamio:enlaces (no borrar esta línea) ---
]


def plantilla(*contenido: rx.Component) -> rx.Component:
    """Envuelve el contenido de una página con el menú. Uso: plantilla(rx.heading("Hola"))."""
    return rx.box(
        rx.hstack(
            *[rx.link(texto, href=ruta) for texto, ruta in ENLACES],
            spacing="5",
            padding="12px 16px",
            border_bottom="1px solid var(--gray-5)",
        ),
        rx.container(*contenido, padding_y="1rem"),
    )
