"""Configuración de Reflex (https://reflex.dev/docs/getting-started/configuration/)."""

import reflex as rx

config = rx.Config(
    app_name="@@proyecto_snake@@",
    # Base de datos SQLite: el archivo datos.db en la carpeta del proyecto.
    db_url="sqlite:///datos.db",
    # La parte de Python de Reflex escucha en el 8001: el 8000 queda libre para las APIs
    # hechas con andamio (Django, FastAPI o Express) que esta aplicación puede usar.
    backend_port=8001,
    api_url="http://localhost:8001",
    # Lee el archivo .env (por ejemplo, API_URL).
    env_file=".env",
    # No enviar datos de uso a los creadores de Reflex.
    telemetry_enabled=False,
    plugins=[rx.plugins.SitemapPlugin(), rx.plugins.RadixThemesPlugin()],
)
