"""Tests de la API de @@titulo@@. Ejecutalos con: python manage.py test @@plural@@"""

@@imports_tests@@
@@import_usuario@@
from rest_framework import status
from rest_framework.test import APITestCase

from .models import @@Nombre@@

URL = "/api/@@plural@@/"

DATOS = {
    @@datos_prueba@@
}

DATOS_MODIFICADOS = {
    @@datos_modificados@@
}


class @@Nombre@@APITest(APITestCase):
    @@preparar_tests@@
    def crear(self):
        return @@Nombre@@.objects.create(**DATOS)

    def test_listar(self):
        self.crear()
        respuesta = self.client.get(URL)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        # Sin paginación, la respuesta es directamente una lista.
        self.assertEqual(len(respuesta.json()), 1)

    def test_obtener(self):
        objeto = self.crear()
        respuesta = self.client.get(f"{URL}{objeto.pk}/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["id"], objeto.pk)

    @@tests_escritura@@

    # --- andamio:tests (no borrar esta línea) ---
