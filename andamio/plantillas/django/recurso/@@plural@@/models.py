# guía: El modelo: la tabla @@plural@@ de la base de datos (cada atributo es una columna).
# guía: Lo usan serializers.py (JSON y validación), views.py (la API) y admin.py.
# guía: Si cambiás un campo: python manage.py makemigrations @@plural@@ y después migrate.
from django.db import models


class @@Nombre@@(models.Model):
    @@campos_modelo@@
    # Fechas que Django completa solo: al crear y en cada modificación.
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "@@verbose@@"
        verbose_name_plural = "@@verbose_plural@@"
        ordering = ["id"]

    def __str__(self):
        return @@str_modelo@@
