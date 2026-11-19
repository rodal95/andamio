from django.urls import path

from . import views

# app_name permite nombrar las rutas sin que choquen con las de otras apps:
# en las plantillas, {% url '@@plural@@:detalle' @@nombre@@.pk %}.
# config/urls.py las incluye debajo de /@@pluralKebab@@/.
app_name = "@@plural@@"

urlpatterns = [
    path("", views.@@Nombre@@ListaView.as_view(), name="lista"),
    path("nuevo/", views.@@Nombre@@CrearView.as_view(), name="crear"),
    path("<int:pk>/", views.@@Nombre@@DetalleView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.@@Nombre@@EditarView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.@@Nombre@@EliminarView.as_view(), name="eliminar"),
]
