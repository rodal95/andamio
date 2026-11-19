from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import RegistroView, YoView

# config/urls.py las incluye debajo de /api/:
#   POST /api/token/          {"username", "password"}  ->  {"access", "refresh"}
#   POST /api/token/refresh/  {"refresh"}               ->  {"access"}  (un token de acceso nuevo)
#   POST /api/token/verify/   {"token"}                 ->  200 si el token es válido
#   POST /api/registro/       crea un usuario
#   GET  /api/yo/             el usuario del token (Authorization: Bearer <access>)
urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("registro/", RegistroView.as_view(), name="registro"),
    path("yo/", YoView.as_view(), name="yo"),
]
