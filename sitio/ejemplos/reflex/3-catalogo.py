"""Página Catalogo: la dirección /catalogo. Muestra los productos de una API de andamio."""

import reflex as rx

import mi_app.servicios.producto as producto_api
from mi_app.componentes.tarjeta import tarjeta
from mi_app.plantilla import plantilla
from mi_app.servicios.http import ErrorApi


class CatalogoState(rx.State):
    productos: list[dict] = []
    error: str = ""

    @rx.event
    async def cargar(self):
        """Pide los productos a la API (con el servicio). Las acciones pueden ser async."""
        try:
            self.productos = await producto_api.listar()
        except ErrorApi as error:
            self.error = str(error)


def tarjeta_de(producto: dict) -> rx.Component:
    return tarjeta(rx.heading(producto["nombre"], size="4"), rx.text("$ ", producto["precio"]))


def catalogo() -> rx.Component:
    return plantilla(
        rx.heading("Catálogo", size="7"),
        rx.cond(CatalogoState.error != "", rx.callout(CatalogoState.error, color_scheme="red")),
        # rx.foreach arma una tarjeta por cada producto; on_mount pide los datos al abrir la página.
        rx.hstack(rx.foreach(CatalogoState.productos, tarjeta_de), spacing="4", wrap="wrap", on_mount=CatalogoState.cargar),
    )
