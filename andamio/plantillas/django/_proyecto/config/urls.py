"""Rutas del proyecto.

- /admin/      panel de administración de Django
- /api/docs/   documentación interactiva de la API (Swagger)
- /api/...     un recurso por app (andamio agrega una línea por cada uno)
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/", RedirectView.as_view(url="/api/docs/", permanent=False)),
    # --- andamio:urls (no borrar esta línea) ---
]
