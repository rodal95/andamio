# guía: El formulario de crear y editar. Lo usan las vistas (views.py) y la plantilla @@nombre@@_form.html.
from django import forms

from .models import @@Nombre@@


class @@Nombre@@Form(forms.ModelForm):
    """El formulario para crear y editar: Django lo arma a partir del modelo y valida los datos."""

    class Meta:
        model = @@Nombre@@
        # Lista explícita: si agregás un campo al modelo, sumalo acá para que aparezca en el formulario.
        fields = [@@campos_form@@]
        @@widgets@@

    # TODO(logica): validaciones propias de un campo. Ejemplo con un precio:
    # def clean_precio(self):
    #     precio = self.cleaned_data["precio"]
    #     if precio <= 0:
    #         raise forms.ValidationError("El precio tiene que ser mayor que cero.")
    #     return precio
