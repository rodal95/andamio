from rest_framework import serializers

from .models import @@Nombre@@


class @@Nombre@@Serializer(serializers.ModelSerializer):
    """Convierte un @@Nombre@@ a JSON y valida los datos que llegan a la API."""

    class Meta:
        model = @@Nombre@@
        # Lista explícita: si agregás un campo al modelo, sumalo acá para que la API lo muestre.
        fields = [@@campos_serializer@@]
        read_only_fields = ["id", "creado", "actualizado"]
