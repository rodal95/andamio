# guía: La API: el ViewSet arma listar, crear, ver, modificar y eliminar.
# guía: Usa el modelo (models.py) y el serializer (serializers.py); urls.py le da la ruta /api/@@plural@@/.
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
    queryset = @@queryset@@
    serializer_class = @@Nombre@@Serializer
    filterset_fields = [@@campos_filtro@@]
    search_fields = [@@campos_busqueda@@]
    ordering_fields = [@@campos_orden@@]

    # TODO(logica): reglas al guardar (lo que no manda el cliente). Ejemplo:
    # def perform_create(self, serializer):
    #     serializer.save(codigo=generar_codigo())
