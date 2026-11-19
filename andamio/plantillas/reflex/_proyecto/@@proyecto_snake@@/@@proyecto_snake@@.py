"""@@proyectoTitulo@@: la aplicación de Reflex. Para ejecutarla:  reflex run

Cada página es una función de Python que devuelve componentes. Acá se registra cada
una con su dirección (andamio agrega las líneas solo).
"""

import reflex as rx

from @@proyecto_snake@@.paginas.inicio import inicio
# --- andamio:imports (no borrar esta línea) ---

app = rx.App(theme=rx.theme(accent_color="amber"))

app.add_page(inicio, route="/", title="Inicio")
# --- andamio:paginas (no borrar esta línea) ---
