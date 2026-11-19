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
