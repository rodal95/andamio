"""Página Catalogo: la dirección /catalogo."""

import reflex as rx

from mi_app.componentes.tarjeta import tarjeta
from mi_app.estados.contador import ContadorState
from mi_app.plantilla import plantilla


def catalogo() -> rx.Component:
    return plantilla(
        rx.heading("Catálogo", size="7"),
        rx.hstack(
            tarjeta(rx.heading("Yerba mate", size="4"), rx.text("$ 4850.50")),
            tarjeta(rx.heading("Mate de calabaza", size="4"), rx.text("$ 12500.00")),
            spacing="4",
        ),
        # El botón llama a una acción del estado; el texto se actualiza solo cuando cambia el valor.
        rx.hstack(
            rx.button("Me gusta", on_click=ContadorState.sumar),
            rx.text(ContadorState.valor, " me gusta"),
            align="center",
            margin_top="16px",
        ),
    )
