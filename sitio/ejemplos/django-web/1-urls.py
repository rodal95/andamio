"""Rutas del sitio.

- /                  página de inicio (templates/inicio.html)
- /admin/            panel de administración de Django
- /cuentas/login/    iniciar sesión          /cuentas/logout/  salir
- /cuentas/registro/ crear un usuario
- andamio agrega una línea por cada crud y cada página que generes.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="inicio.html"), name="inicio"),
    path("admin/", admin.site.urls),
    path("cuentas/registro/", views.registro, name="registro"),
    # login/, logout/, password_change/, password_reset/... (vistas que trae Django)
    path("cuentas/", include("django.contrib.auth.urls")),
    path("productos/", include("productos.urls")),
    # Antes era un TemplateView (solo la plantilla); ahora la vista busca los datos.
    path("catalogo/", views.catalogo, name="catalogo"),
    # --- andamio:urls (no borrar esta línea) ---
]
