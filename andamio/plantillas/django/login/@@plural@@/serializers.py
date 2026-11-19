from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    """Los datos públicos de un usuario (nunca la contraseña)."""

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = fields


class RegistroSerializer(serializers.ModelSerializer):
    """Valida los datos para crear un usuario: la contraseña se guarda encriptada."""

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "password", "first_name", "last_name"]
        read_only_fields = ["id"]

    def validate_password(self, valor):
        # Las mismas reglas que AUTH_PASSWORD_VALIDATORS (largo mínimo, no muy común, etc.).
        validate_password(valor)
        return valor

    def create(self, datos):
        # create_user encripta la contraseña; Usuario.objects.create la guardaría tal cual.
        return Usuario.objects.create_user(**datos)
