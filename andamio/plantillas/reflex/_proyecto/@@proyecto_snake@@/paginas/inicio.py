"""Página de inicio: la dirección "/"."""

import reflex as rx

from @@proyecto_snake@@.plantilla import plantilla


def inicio() -> rx.Component:
    return plantilla(
        rx.heading("@@proyectoTitulo@@", size="8"),
        rx.text("Editá ", rx.code("@@proyecto_snake@@/paginas/inicio.py"), " para empezar."),
    )
