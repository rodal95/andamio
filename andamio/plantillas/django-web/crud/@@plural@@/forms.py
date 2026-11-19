from django import forms

from .models import @@Nombre@@


class @@Nombre@@Form(forms.ModelForm):
    """El formulario para crear y editar: Django lo arma a partir del modelo y valida los datos."""

    class Meta:
        model = @@Nombre@@
        # Lista explícita: si agregás un campo al modelo, sumalo acá para que aparezca en el formulario.
        fields = [@@campos_form@@]
        @@widgets@@
