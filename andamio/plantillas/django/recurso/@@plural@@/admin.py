from django.contrib import admin

from .models import @@Nombre@@


@admin.register(@@Nombre@@)
class @@Nombre@@Admin(admin.ModelAdmin):
    list_display = [@@campos_admin@@]
    search_fields = [@@campos_busqueda@@]
    list_filter = [@@campos_admin_filtro@@]
