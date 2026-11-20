"""@@titulo@@ (la dirección /@@pluralKebab@@): listar, agregar, editar y eliminar.

@@Nombre@@State guarda lo que muestra la página y tiene las acciones, que se ejecutan
en Python cuando tocás un botón. Los datos están en la base de este proyecto.
"""

import reflex as rx
from pydantic import ValidationError
from sqlmodel import select

from @@app@@.modelos.@@nombre@@ import @@Nombre@@, @@Nombre@@Datos, ahora
from @@app@@.plantilla import plantilla
from @@app@@.validacion import errores_de

# Lo que tiene el formulario vacío: todo es texto, salvo los sí/no.
VACIO = {
    @@valores_vacios@@
}


def a_formulario(@@nombre@@: @@Nombre@@) -> dict:
    """Pasa un elemento de la base a los valores del formulario (y de la tabla)."""
    return {
        @@campos_a_formulario@@
    }


class @@Nombre@@State(rx.State):
    tabla: list[dict] = []  # lo que muestra la tabla
    datos: dict = VACIO  # lo que está escrito en el formulario
    errores: dict[str, list[str]] = {}  # errores de validación, por campo
    editando: int = 0  # el id del elemento que se está editando (0: uno nuevo)

    def _leer(self):
        with rx.session() as bd:
            todos = bd.exec(select(@@Nombre@@).order_by(@@Nombre@@.id)).all()
            self.tabla = [{"id": elemento.id, **a_formulario(elemento)} for elemento in todos]

    def _limpiar(self):
        self.datos, self.errores, self.editando = dict(VACIO), {}, 0

    @rx.event
    def cargar(self):
        """Se ejecuta al abrir la página."""
        self._leer()

    @rx.event
    def cambiar(self, campo: str, valor: str | bool):
        self.datos[campo] = valor

    @rx.event
    def guardar(self):
        """Valida el formulario y guarda: crea uno nuevo o modifica el que se está editando."""
        try:
            validos = @@Nombre@@Datos.model_validate(self.datos)
        except ValidationError as error:
            self.errores = errores_de(error)
            return
        with rx.session() as bd:
            if self.editando:
                elemento = bd.get(@@Nombre@@, self.editando)
                elemento.sqlmodel_update(validos.model_dump())
                elemento.actualizado = ahora()
            else:
                elemento = @@Nombre@@.model_validate(validos)
            bd.add(elemento)
            bd.commit()
        self._limpiar()
        self._leer()

    @rx.event
    def editar(self, elemento: dict):
        """Pasa un elemento de la tabla al formulario."""
        self.editando = elemento["id"]
        self.datos = {campo: valor for campo, valor in elemento.items() if campo != "id"}
        self.errores = {}

    @rx.event
    def cancelar(self):
        self._limpiar()

    @rx.event
    def eliminar(self, id_registro: int):
        with rx.session() as bd:
            elemento = bd.get(@@Nombre@@, id_registro)
            if elemento is not None:
                bd.delete(elemento)
                bd.commit()
        self._limpiar()
        self._leer()


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
        rx.hstack(
            rx.button("Guardar", on_click=@@Nombre@@State.guardar),
            rx.button("Cancelar", variant="soft", on_click=@@Nombre@@State.cancelar),
        ),
        max_width="480px",
        width="100%",
    )


def fila(elemento: dict) -> rx.Component:
    return rx.table.row(
        @@celdas@@
        rx.table.cell(
            rx.hstack(
                rx.button("Editar", size="1", variant="soft", on_click=@@Nombre@@State.editar(elemento)),
                rx.button("Eliminar", size="1", color_scheme="red", on_click=@@Nombre@@State.eliminar(elemento["id"])),
            )
        ),
    )


def @@plural@@() -> rx.Component:
    return plantilla(
        rx.heading("@@titulo@@", size="7"),
        formulario(),
        rx.cond(
            @@Nombre@@State.tabla.length() == 0,
            rx.text("Todavía no hay registros."),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        @@encabezados@@
                        rx.table.column_header_cell(""),
                    )
                ),
                rx.table.body(rx.foreach(@@Nombre@@State.tabla, fila)),
                width="100%",
            ),
        ),
    )
