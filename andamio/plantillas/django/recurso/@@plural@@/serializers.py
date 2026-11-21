# guía: Traduce entre el modelo (models.py) y el JSON de la API, y valida lo que llega.
# guía: Lo usa views.py. Si un dato no sirve, la API responde 400 diciendo qué campo y por qué.
from rest_framework import serializers

from .models import @@Nombre@@


class @@Nombre@@Serializer(serializers.ModelSerializer):
    """Convierte un @@Nombre@@ a JSON y valida los datos que llegan a la API."""

    @@campos_relacion@@
    class Meta:
        model = @@Nombre@@
        # Lista explícita: si agregás un campo al modelo, sumalo acá para que la API lo muestre.
        fields = [@@campos_serializer@@]
        read_only_fields = ["id", "creado", "actualizado"]

    # TODO(logica): validaciones propias, además del tipo de cada campo. Ejemplo con un precio:
    # def validate_precio(self, valor):
    #     if valor <= 0:
    #         raise serializers.ValidationError("El precio tiene que ser mayor que cero.")
    #     return valor
