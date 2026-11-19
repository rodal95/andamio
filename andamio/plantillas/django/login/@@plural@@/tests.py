"""Tests del login con JWT. Ejecutalos con: python manage.py test @@plural@@"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

USUARIO = {"username": "ana", "email": "ana@ejemplo.com", "password": "una-clave-larga-123"}


class LoginTest(APITestCase):
    def test_registro(self):
        respuesta = self.client.post("/api/registro/", USUARIO, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.json())
        self.assertNotIn("password", respuesta.json())
        # La contraseña se guarda encriptada, no como texto.
        self.assertTrue(get_user_model().objects.get(username="ana").check_password(USUARIO["password"]))

    def test_registro_rechaza_una_clave_debil(self):
        respuesta = self.client.post("/api/registro/", {**USUARIO, "password": "123"}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", respuesta.json())

    def test_login_devuelve_los_tokens(self):
        get_user_model().objects.create_user(**USUARIO)
        respuesta = self.client.post("/api/token/", {"username": "ana", "password": USUARIO["password"]}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.json())
        self.assertIn("refresh", respuesta.json())

    def test_login_con_clave_incorrecta(self):
        get_user_model().objects.create_user(**USUARIO)
        respuesta = self.client.post("/api/token/", {"username": "ana", "password": "otra"}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_yo_con_y_sin_token(self):
        get_user_model().objects.create_user(**USUARIO)
        self.assertEqual(self.client.get("/api/yo/").status_code, status.HTTP_401_UNAUTHORIZED)
        tokens = self.client.post("/api/token/", {"username": "ana", "password": USUARIO["password"]}, format="json").json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        respuesta = self.client.get("/api/yo/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["username"], "ana")

    def test_refresh_da_un_token_nuevo(self):
        get_user_model().objects.create_user(**USUARIO)
        tokens = self.client.post("/api/token/", {"username": "ana", "password": USUARIO["password"]}, format="json").json()
        respuesta = self.client.post("/api/token/refresh/", {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.json())
