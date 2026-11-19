from rest_framework import viewsets
@@import_permisos@@

from .models import @@Nombre@@
from .serializers import @@Nombre@@Serializer


class @@Nombre@@ViewSet(viewsets.ModelViewSet):
    """Listar, crear, ver, modificar y eliminar: /api/@@plural@@/

    La lista acepta estos parámetros:
        ?search=texto       busca en los campos de search_fields
        ?ordering=-creado   ordena por un campo (con "-" es de mayor a menor)
        ?campo=valor        filtra por los campos de filterset_fields
    """

    @@permisos@@
    queryset = @@Nombre@@.objects.all()
    serializer_class = @@Nombre@@Serializer
    filterset_fields = [@@campos_filtro@@]
    search_fields = [@@campos_busqueda@@]
    ordering_fields = [@@campos_orden@@]
