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

    def test_crear(self):
        respuesta = self.client.post(URL, DATOS, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.json())
        self.assertEqual(@@Nombre@@.objects.count(), 1)

    def test_obtener(self):
        objeto = self.crear()
        respuesta = self.client.get(f"{URL}{objeto.pk}/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["id"], objeto.pk)

    def test_actualizar(self):
        objeto = self.crear()
        respuesta = self.client.put(f"{URL}{objeto.pk}/", DATOS_MODIFICADOS, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.json())
        objeto.refresh_from_db()
        self.assertEqual(objeto.@@campo_verificado@@, @@valor_verificado@@)

    def test_eliminar(self):
        objeto = self.crear()
        respuesta = self.client.delete(f"{URL}{objeto.pk}/")
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(@@Nombre@@.objects.filter(pk=objeto.pk).exists())
