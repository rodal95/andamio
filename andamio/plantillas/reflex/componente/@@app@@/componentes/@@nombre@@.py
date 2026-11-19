"""Componente @@nombreTitulo@@: una parte de la interfaz que se puede reutilizar."""

import reflex as rx


def @@nombre@@(*contenido: rx.Component, **props) -> rx.Component:
    """Uso: @@nombre@@(rx.text("Hola"), width="300px")."""
    return rx.box(
        *contenido,
        padding="16px",
        border="1px solid var(--gray-6)",
        border_radius="10px",
        **props,
    )
