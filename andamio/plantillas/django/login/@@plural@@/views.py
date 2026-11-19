from rest_framework import generics, permissions

from .serializers import RegistroSerializer, UsuarioSerializer


class RegistroView(generics.CreateAPIView):
    """POST /api/registro/ crea un usuario: {"username", "email", "password"}."""

    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]


class YoView(generics.RetrieveAPIView):
    """GET /api/yo/ devuelve el usuario dueño del token (sin token: 401)."""

    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
