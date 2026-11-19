"""Página @@nombreTitulo@@: la dirección /@@nombreKebab@@."""

import reflex as rx

from @@app@@.plantilla import plantilla


def @@nombre@@() -> rx.Component:
    return plantilla(
        rx.heading("@@nombreTitulo@@", size="7"),
    )
