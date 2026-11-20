"""Tests de las páginas de @@titulo@@. Ejecutalos con: python manage.py test @@plural@@"""

@@import_usuario@@
from django.test import TestCase

from .forms import @@Nombre@@Form
from .models import @@Nombre@@

URL = "/@@pluralKebab@@/"

# Lo que se envía en el formulario (como lo mandaría el navegador).
DATOS = {
    @@datos_prueba@@
}

DATOS_MODIFICADOS = {
    @@datos_modificados@@
}


class @@Nombre@@PaginasTest(TestCase):
    @@preparar_tests@@
    def crear(self):
        form = @@Nombre@@Form(DATOS)
        self.assertTrue(form.is_valid(), form.errors)
        return form.save()

    def test_lista(self):
        objeto = self.crear()
        res = self.client.get(URL)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, f"{URL}{objeto.pk}/")

    def test_crear(self):
        res = self.client.post(f"{URL}nuevo/", DATOS)
        # Si el formulario es válido, guarda y redirige a la lista (302).
        self.assertRedirects(res, URL)
        self.assertEqual(@@Nombre@@.objects.count(), 1)

    def test_crear_con_datos_incompletos(self):
        res = self.client.post(f"{URL}nuevo/", {})
        # Si no es válido, vuelve a mostrar el formulario (200) con los errores.
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context["form"].errors)
        self.assertEqual(@@Nombre@@.objects.count(), 0)

    def test_detalle(self):
        objeto = self.crear()
        res = self.client.get(f"{URL}{objeto.pk}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["@@nombre@@"], objeto)

    def test_editar(self):
        objeto = self.crear()
        res = self.client.post(f"{URL}{objeto.pk}/editar/", DATOS_MODIFICADOS)
        self.assertRedirects(res, URL)
        objeto.refresh_from_db()
        esperado = @@Nombre@@Form(DATOS_MODIFICADOS)
        self.assertTrue(esperado.is_valid(), esperado.errors)
        self.assertEqual(objeto.@@campo_verificado@@, esperado.cleaned_data["@@campo_verificado@@"])

    def test_eliminar(self):
        objeto = self.crear()
        res = self.client.post(f"{URL}{objeto.pk}/eliminar/")
        self.assertRedirects(res, URL)
        self.assertFalse(@@Nombre@@.objects.filter(pk=objeto.pk).exists())
