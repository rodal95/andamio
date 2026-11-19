"""Estado @@Nombre@@State: datos que guarda la aplicación y las acciones que los cambian.

En Reflex, el estado vive en Python. Cada acción (un método con @rx.event) se ejecuta
cuando pasa algo en la página, por ejemplo al tocar un botón:

    rx.button("Sumar", on_click=@@Nombre@@State.sumar)
    rx.text(@@Nombre@@State.valor)
"""

import reflex as rx


class @@Nombre@@State(rx.State):
    valor: int = 0

    @rx.event
    def sumar(self):
        self.valor += 1

    @rx.event
    def reiniciar(self):
        self.valor = 0
