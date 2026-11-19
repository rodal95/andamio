"""Página Catalogo: la dirección /catalogo."""

import reflex as rx

from mi_app.componentes.tarjeta import tarjeta
from mi_app.plantilla import plantilla


def catalogo() -> rx.Component:
    return plantilla(
        rx.heading("Catálogo", size="7"),
        # El componente tarjeta recibe lo que va adentro, igual que cualquier componente de Reflex.
        rx.hstack(
            tarjeta(rx.heading("Yerba mate", size="4"), rx.text("$ 4850.50")),
            tarjeta(rx.heading("Mate de calabaza", size="4"), rx.text("$ 12500.00")),
            spacing="4",
        ),
    )
