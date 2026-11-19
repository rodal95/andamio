"""@@titulo@@ (la dirección /@@pluralKebab@@): listar, agregar, editar y eliminar.

@@Nombre@@State guarda lo que muestra la página y tiene las acciones, que se ejecutan
en Python cuando tocás un botón. Los datos están en una API hecha con andamio (Django,
FastAPI o Express): se piden con el servicio y la API valida lo que se manda.
"""

import reflex as rx

import @@app@@.servicios.@@nombre@@ as @@nombre@@_api
from @@app@@.plantilla import plantilla
from @@app@@.servicios.http import ErrorApi

# Lo que tiene el formulario vacío: todo es texto, salvo los sí/no.
VACIO = {
    @@valores_vacios@@
}


def a_formulario(@@nombre@@: dict) -> dict:
    """Pasa un registro de la API a los valores del formulario (y de la tabla)."""
    return {
        @@campos_a_formulario@@
    }


class @@Nombre@@State(rx.State):
    registros: list[dict] = []  # lo que muestra la tabla
    datos: dict = VACIO  # lo que está escrito en el formulario
    errores: dict[str, list[str]] = {}  # errores de validación, por campo
    editando: int = 0  # el id del registro que se está editando (0: uno nuevo)
    error: str = ""  # si la API no responde

    async def _leer(self):
        try:
            todos = await @@nombre@@_api.listar()
            self.registros = [{"id": registro["id"], **a_formulario(registro)} for registro in todos]
            self.error = ""
        except ErrorApi as error:
            self.error = str(error)

    def _limpiar(self):
        self.datos, self.errores, self.editando = dict(VACIO), {}, 0

    @rx.event
    async def cargar(self):
        """Se ejecuta al abrir la página."""
        await self._leer()

    @rx.event
    def cambiar(self, campo: str, valor: str | bool):
        self.datos[campo] = valor

    @rx.event
    async def guardar(self):
        """Manda el formulario a la API: crea uno nuevo o modifica el que se está editando."""
        try:
            if self.editando:
                await @@nombre@@_api.actualizar(self.editando, self.datos)
            else:
                await @@nombre@@_api.crear(self.datos)
        except ErrorApi as error:
            # 400: la API dice qué campo está mal, con el mismo formato en las tres APIs.
            self.errores = error.detalle if error.estado == 400 else {"general": [str(error)]}
            return
        self._limpiar()
        await self._leer()

    @rx.event
    def editar(self, registro: dict):
        """Pasa un registro de la tabla al formulario."""
        self.editando = registro["id"]
        self.datos = {campo: valor for campo, valor in registro.items() if campo != "id"}
        self.errores = {}

    @rx.event
    def cancelar(self):
        self._limpiar()

    @rx.event
    async def eliminar(self, id_registro: int):
        try:
            await @@nombre@@_api.eliminar(id_registro)
        except ErrorApi as error:
            self.error = str(error)
            return
        self._limpiar()
        await self._leer()


def campo(etiqueta: str, nombre: str, control: rx.Component) -> rx.Component:
    """Un campo del formulario: la etiqueta, el control y su error (si hay)."""
    return rx.vstack(
        rx.el.label(etiqueta, html_for=nombre, font_weight="bold"),
        control,
        rx.cond(
            @@Nombre@@State.errores.contains(nombre),
            rx.text(@@Nombre@@State.errores[nombre].join(" "), color_scheme="red", size="2"),
        ),
        spacing="1",
        width="100%",
    )


def formulario() -> rx.Component:
    return rx.vstack(
        rx.heading(rx.cond(@@Nombre@@State.editando, "Editar", "Agregar"), size="5"),
        @@campos_formulario@@
        rx.cond(
            @@Nombre@@State.errores.contains("general"),
            rx.text(@@Nombre@@State.errores["general"].join(" "), color_scheme="red", size="2"),
        ),
        rx.hstack(
            rx.button("Guardar", on_click=@@Nombre@@State.guardar),
            rx.button("Cancelar", variant="soft", on_click=@@Nombre@@State.cancelar),
        ),
        max_width="480px",
        width="100%",
    )


def fila(registro: dict) -> rx.Component:
    return rx.table.row(
        @@celdas@@
        rx.table.cell(
            rx.hstack(
                rx.button("Editar", size="1", variant="soft", on_click=@@Nombre@@State.editar(registro)),
                rx.button("Eliminar", size="1", color_scheme="red", on_click=@@Nombre@@State.eliminar(registro["id"])),
            )
        ),
    )


def @@plural@@() -> rx.Component:
    return plantilla(
        rx.heading("@@titulo@@", size="7"),
        rx.cond(@@Nombre@@State.error != "", rx.callout(@@Nombre@@State.error, color_scheme="red")),
        formulario(),
        rx.cond(
            @@Nombre@@State.registros.length() == 0,
            rx.text("Todavía no hay registros."),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        @@encabezados@@
                        rx.table.column_header_cell(""),
                    )
                ),
                rx.table.body(rx.foreach(@@Nombre@@State.registros, fila)),
                width="100%",
            ),
        ),
    )
