# guía: Las cinco páginas (lista, detalle, crear, editar y eliminar). Cada vista usa el modelo,
# guía: el formulario (forms.py) y una plantilla de templates/@@plural@@/; urls.py les da la ruta.
from django.contrib import messages
@@import_login@@
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import @@Nombre@@Form
from .models import @@Nombre@@

# Vistas genéricas de Django: cada una ya sabe listar, mostrar, crear, editar o eliminar.
# Solo hay que decirles qué modelo, qué formulario y qué plantilla usar.


class @@Nombre@@ListaView(ListView):
    """/@@pluralKebab@@/ : la lista, con búsqueda (?q=texto) y de a 10 por página."""

    model = @@Nombre@@
    template_name = "@@plural@@/@@nombre@@_lista.html"
    context_object_name = "@@plural@@"
    paginate_by = 10

    def get_queryset(self):
        consulta = super().get_queryset()
        texto = self.request.GET.get("q", "").strip()
        if texto:
            @@filtro_busqueda@@
        return consulta


class @@Nombre@@DetalleView(DetailView):
    """/@@pluralKebab@@/3/ : un registro."""

    model = @@Nombre@@
    template_name = "@@plural@@/@@nombre@@_detalle.html"
    context_object_name = "@@nombre@@"


class @@Nombre@@CrearView(@@mixin_login@@SuccessMessageMixin, CreateView):
    """/@@pluralKebab@@/nuevo/ : el formulario vacío; al guardar vuelve a la lista."""

    model = @@Nombre@@
    form_class = @@Nombre@@Form
    template_name = "@@plural@@/@@nombre@@_form.html"
    success_url = reverse_lazy("@@plural@@:lista")
    success_message = @@mensaje_creado@@


class @@Nombre@@EditarView(@@mixin_login@@SuccessMessageMixin, UpdateView):
    """/@@pluralKebab@@/3/editar/ : el formulario con los datos del registro."""

    model = @@Nombre@@
    form_class = @@Nombre@@Form
    template_name = "@@plural@@/@@nombre@@_form.html"
    success_url = reverse_lazy("@@plural@@:lista")
    success_message = "Se guardaron los cambios."


class @@Nombre@@EliminarView(@@mixin_login@@DeleteView):
    """/@@pluralKebab@@/3/eliminar/ : pide confirmación y elimina (con POST)."""

    model = @@Nombre@@
    template_name = "@@plural@@/@@nombre@@_confirmar_eliminar.html"
    context_object_name = "@@nombre@@"
    success_url = reverse_lazy("@@plural@@:lista")

    def form_valid(self, form):
        messages.success(self.request, f"Se eliminó «{self.object}».")
        return super().form_valid(form)
