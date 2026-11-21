"""Stack django: crear el proyecto, generar recursos y ejecutar check, migraciones y tests."""

import importlib.util
import os
import py_compile
import subprocess
import sys

import pytest

from andamio.cli import main
from andamio.stacks.django import python_del_proyecto

DEPENDENCIAS = [
    "django",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "dotenv",
    "dj_database_url",
]
FALTANTES = [m for m in DEPENDENCIAS if importlib.util.find_spec(m) is None]
requiere_django = pytest.mark.skipif(
    bool(FALTANTES),
    reason="faltan dependencias de Django: pip install -r andamio/plantillas/django/_proyecto/requirements.txt",
)

TODOS_LOS_TIPOS = [
    "nombre:str",
    "descripcion:text",
    "precio:decimal",
    "stock:int",
    "peso:float",
    "activo:bool",
    "vence:date",
    "publicado:datetime",
    "contacto:email",
]


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def manage(raiz, *argumentos):
    return subprocess.run(
        [sys.executable, "manage.py", *argumentos],
        cwd=raiz,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "django", "Mi API"]) == 0
    raiz = en_carpeta / "mi-api"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_recursos(proyecto):
    assert main(["nuevo", "recurso", "producto", *TODOS_LOS_TIPOS]) == 0
    assert main(["nuevo", "recurso", "cliente", "nombre", "email:email"]) == 0
    return proyecto


# --- Sin necesidad de Django instalado ----------------------------------------


def test_estructura_del_proyecto(proyecto):
    for archivo in ["manage.py", "config/settings.py", "config/urls.py", "requirements.txt", ".env", ".env.example", ".gitignore", "README.md"]:
        assert (proyecto / archivo).is_file(), archivo
    env, ejemplo = leer(proyecto / ".env"), leer(proyecto / ".env.example")
    assert "SECRET_KEY=cambiar-por-una-clave-larga-y-secreta" in ejemplo
    assert "SECRET_KEY=cambiar" not in env
    assert "10.0.2.2" in env
    settings = leer(proyecto / "config/settings.py")
    assert "AllowAny" in settings and "ATENCIÓN" in settings
    assert '"COERCE_DECIMAL_TO_STRING": False' in settings
    assert '"DEFAULT_PAGINATION_CLASS": None' in settings


def test_dos_veces_el_mismo_proyecto(proyecto, en_carpeta, monkeypatch, capsys):
    monkeypatch.chdir(en_carpeta)
    capsys.readouterr()
    assert main(["crear", "django", "mi-api"]) == 1
    assert "no está vacía" in capsys.readouterr().err


def test_recurso_genera_la_app_y_la_registra(con_recursos):
    raiz = con_recursos
    for archivo in ["__init__.py", "apps.py", "models.py", "serializers.py", "views.py", "urls.py", "admin.py", "tests.py", "migrations/__init__.py"]:
        assert (raiz / "productos" / archivo).is_file(), archivo
    settings, urls = leer(raiz / "config/settings.py"), leer(raiz / "config/urls.py")
    assert '    "productos",\n    "clientes",\n    # --- andamio:apps' in settings
    assert 'path("api/", include("productos.urls")),\n    path("api/", include("clientes.urls")),' in urls
    for archivo in raiz.rglob("*.py"):
        py_compile.compile(str(archivo), doraise=True)


def test_tipos_de_campo_del_modelo(con_recursos):
    modelo = leer(con_recursos / "productos/models.py")
    for esperado in [
        'nombre = models.CharField("Nombre", max_length=200)',
        'descripcion = models.TextField("Descripcion")',
        'precio = models.DecimalField("Precio", max_digits=10, decimal_places=2)',
        'stock = models.IntegerField("Stock")',
        'peso = models.FloatField("Peso")',
        'activo = models.BooleanField("Activo", default=False)',
        'vence = models.DateField("Vence")',
        'publicado = models.DateTimeField("Publicado")',
        'contacto = models.EmailField("Contacto")',
        "creado = models.DateTimeField(auto_now_add=True)",
        "return self.nombre",
    ]:
        assert esperado in modelo
    vista = leer(con_recursos / "productos/views.py")
    assert 'search_fields = ["nombre", "descripcion", "contacto"]' in vista
    assert '"descripcion"' not in vista.split("filterset_fields")[1].split("\n")[0]
    assert 'fields = ["id", "nombre",' in leer(con_recursos / "productos/serializers.py")
    assert 'router.register("productos", ProductoViewSet, basename="producto")' in leer(con_recursos / "productos/urls.py")


def test_str_sin_campos_de_texto(proyecto):
    assert main(["nuevo", "recurso", "medicion", "valor:float", "fecha:date"]) == 0
    modelo = leer(proyecto / "mediciones/models.py")
    assert 'return f"Medicion {self.pk}"' in modelo
    assert "from decimal import Decimal" not in leer(proyecto / "mediciones/tests.py")


def test_nombre_compuesto(proyecto):
    assert main(["nuevo", "recurso", "Línea Venta", "cantidad:int"]) == 0
    assert (proyecto / "lineas_venta/models.py").is_file()
    assert "class LineaVenta(models.Model):" in leer(proyecto / "lineas_venta/models.py")
    assert 'URL = "/api/lineas_venta/"' in leer(proyecto / "lineas_venta/tests.py")


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        (["recurso", "doc", "nombre", "--plural", "docs"], "/api/docs/"),
        (["recurso", "type", "nombre"], "módulo de Python"),
        (["recurso", "producto", "objects"], "Django usa"),
        (["recurso", "producto", "search"], "?search="),
        (["recurso", "producto", "precio:money"], "Tipos válidos: str, text, int, decimal"),
        (["recurso", "productos", "nombre"], "parece estar en plural"),
    ],
)
def test_nombres_que_no_se_pueden_usar(proyecto, capsys, argumentos, esperado):
    assert main(["nuevo", *argumentos]) == 1
    assert esperado in capsys.readouterr().err


def test_recurso_repetido_no_toca_nada(con_recursos, capsys):
    antes = {p: p.read_bytes() for p in con_recursos.rglob("*") if p.is_file()}
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 1
    assert "productos" in capsys.readouterr().err
    assert antes == {p: p.read_bytes() for p in con_recursos.rglob("*") if p.is_file()}


def test_app_registrada_pero_borrada(con_recursos, capsys):
    import shutil

    shutil.rmtree(con_recursos / "clientes")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "cliente", "nombre"]) == 1
    assert "ya está registrada en LOCAL_APPS" in capsys.readouterr().err


def test_marcadores_borrados(proyecto, capsys):
    settings = proyecto / "config/settings.py"
    settings.write_text(leer(settings).replace("    # --- andamio:apps (no borrar esta línea) ---\n", ""), encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 0
    salida = capsys.readouterr().out
    assert "No se pudo modificar config" in salida
    assert '"productos",' in salida
    assert "dentro de la lista LOCAL_APPS" in salida
    assert 'include("productos.urls")' in leer(proyecto / "config/urls.py")


def test_detecta_django_antes_que_python(proyecto):
    from andamio.nucleo.deteccion import buscar_proyecto

    (proyecto / "main.py").touch()
    (proyecto / "db.py").touch()
    assert buscar_proyecto(proyecto / "config")[0].clave == "django"


def test_python_del_proyecto_prefiere_el_entorno_virtual(tmp_path, monkeypatch):
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    assert python_del_proyecto(tmp_path) == sys.executable
    ejecutable = tmp_path / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
    ejecutable.parent.mkdir(parents=True)
    ejecutable.touch()
    assert python_del_proyecto(tmp_path) == str(ejecutable)


def test_menu_interactivo(proyecto, respuestas, capsys):
    preguntas = respuestas(["1", "producto", "", "n", "n", "nombre", "1", "precio", "4", "", "s", "n"])
    capsys.readouterr()
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto Django REST detectado." in salida
    assert "python manage.py makemigrations productos" in salida
    assert any("migraciones" in p for p in preguntas)
    assert 'precio = models.DecimalField("Precio"' in leer(proyecto / "productos/models.py")


# --- Con Django instalado ----------------------------------------------------


@pytest.mark.django
@requiere_django
def test_check_migraciones_y_tests_generados(con_recursos):
    raiz = con_recursos
    for argumentos in (["check"], ["makemigrations"], ["test", "-v", "2"], ["spectacular", "--validate", "--fail-on-warn", "--file", "schema.yml"]):
        resultado = manage(raiz, *argumentos)
        assert resultado.returncode == 0, f"manage.py {' '.join(argumentos)}\n{resultado.stdout}\n{resultado.stderr}"
        if argumentos[0] == "test":
            assert "Ran 10 tests" in resultado.stderr
    assert (raiz / "productos/migrations/0001_initial.py").is_file()


@pytest.mark.django
@requiere_django
def test_opcion_migrar(proyecto, capsys):
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre", "precio:decimal", "--migrar"]) == 0
    salida = capsys.readouterr().out
    assert "Ejecutando: python manage.py makemigrations productos" in salida
    assert "python manage.py runserver" in salida
    assert "makemigrations productos\n" not in salida.split("Siguientes pasos")[-1]
    assert (proyecto / "productos/migrations/0001_initial.py").is_file()
    assert (proyecto / "db.sqlite3").is_file()


# --- Login con JWT y recursos protegidos ------------------------------------------------


def test_login_genera_la_app_y_configura_jwt(proyecto, capsys):
    assert main(["nuevo", "login"]) == 0
    for archivo in ["__init__.py", "apps.py", "serializers.py", "views.py", "urls.py", "tests.py"]:
        assert (proyecto / "cuentas" / archivo).is_file(), archivo
    settings = leer(proyecto / "config/settings.py")
    assert '"cuentas",\n    # --- andamio:apps' in settings
    assert "rest_framework_simplejwt.authentication.JWTAuthentication" in settings
    assert "ACCESS_TOKEN_LIFETIME" in settings
    assert 'path("api/", include("cuentas.urls")),' in leer(proyecto / "config/urls.py")
    assert "djangorestframework-simplejwt~=" in leer(proyecto / "requirements.txt")
    for archivo in proyecto.rglob("*.py"):
        py_compile.compile(str(archivo), doraise=True)
    capsys.readouterr()
    assert main(["nuevo", "login"]) == 1
    assert "ya tiene el login con JWT" in capsys.readouterr().err


def test_login_en_el_menu_usa_cuenta_con_enter(proyecto, respuestas):
    preguntas = respuestas(["3", "", "s"])
    assert main([]) == 0
    assert any("Nombre de la app del login" in p for p in preguntas)
    assert (proyecto / "cuentas/urls.py").is_file()


def test_login_con_otro_nombre_si_ya_hay_una_app_cuentas(proyecto, capsys):
    # Un banco: el recurso "cuenta" ocupa la app "cuentas", que es la del login por defecto.
    assert main(["nuevo", "recurso", "cuenta", "numero:str", "saldo:decimal"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "login"]) == 1
    error = capsys.readouterr().err
    assert "Ya hay una app 'cuentas'" in error and "nuevo login acceso" in error
    assert "--plural" not in error  # login no acepta --plural: no se puede sugerir
    assert main(["nuevo", "login", "acceso"]) == 0
    assert 'path("api/", include("accesos.urls")),' in leer(proyecto / "config/urls.py")


def test_recurso_protegido(proyecto):
    assert main(["nuevo", "recurso", "pedido", "cliente:str", "total:decimal", "--protegido"]) == 0
    vista, tests = leer(proyecto / "pedidos/views.py"), leer(proyecto / "pedidos/tests.py")
    assert "from rest_framework.permissions import IsAuthenticatedOrReadOnly" in vista
    assert "permission_classes = [IsAuthenticatedOrReadOnly]" in vista
    assert "force_authenticate(usuario)" in tests and "def test_sin_login_no_se_puede_crear" in tests
    py_compile.compile(str(proyecto / "pedidos/tests.py"), doraise=True)
    # Sin --protegido no queda rastro de los permisos.
    assert main(["nuevo", "recurso", "cliente", "nombre"]) == 0
    assert "permission" not in leer(proyecto / "clientes/views.py")
    assert "get_user_model" not in leer(proyecto / "clientes/tests.py")


def test_protegido_no_existe_en_otras_piezas(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "fastapi", "api"]) == 0
    monkeypatch.chdir(en_carpeta / "api")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre", "--protegido"]) == 1
    assert "no acepta la opción --protegido" in capsys.readouterr().err


SIMPLEJWT = importlib.util.find_spec("rest_framework_simplejwt") is not None


@pytest.mark.django
@requiere_django
@pytest.mark.skipif(not SIMPLEJWT, reason="falta djangorestframework-simplejwt")
def test_login_y_protegido_funcionan(proyecto):
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "recurso", "pedido", "cliente:str", "total:decimal", "entregado:bool", "--protegido"]) == 0
    for argumentos in (["check"], ["makemigrations"], ["test", "-v", "2"], ["spectacular", "--validate", "--fail-on-warn", "--file", "schema.yml"]):
        resultado = manage(proyecto, *argumentos)
        assert resultado.returncode == 0, f"manage.py {' '.join(argumentos)}\n{resultado.stdout}\n{resultado.stderr}"
        if argumentos[0] == "test":
            # 6 del login y 6 del recurso protegido (los 5 de siempre + sin login).
            assert "Ran 12 tests" in resultado.stderr
    # Swagger tiene el botón Authorize para el token.
    assert "bearerFormat: JWT" in leer(proyecto / "schema.yml")


# --- Relaciones (campo:fk) -----------------------------------------------------------

PRUEBA_RELACION = '''\
from rest_framework.test import APITestCase

from categorias.models import Categoria


class RelacionTest(APITestCase):
    def test_la_relacion_funciona(self):
        yerbas = Categoria.objects.create(nombre="Yerbas")
        respuesta = self.client.post("/api/productos/", {"nombre": "Mate", "categoria": yerbas.pk}, format="json")
        self.assertEqual(respuesta.status_code, 201, respuesta.json())
        self.assertEqual(respuesta.json()["categoria_texto"], "Yerbas")
        self.assertEqual(self.client.get(f"/api/productos/?categoria={yerbas.pk}").json()[0]["nombre"], "Mate")
        # Un id que no existe: 400 con el error en el campo.
        respuesta = self.client.post("/api/productos/", {"nombre": "Otro", "categoria": 999}, format="json")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("categoria", respuesta.json())
        # Si se borra la categoría, el producto queda sin categoría.
        yerbas.delete()
        self.assertIsNone(self.client.get("/api/productos/").json()[0]["categoria"])
'''


def test_relacion_genera_la_foreign_key(proyecto, capsys):
    assert main(["nuevo", "recurso", "producto", "nombre", "categoria:fk"]) == 1
    assert "python -m andamio nuevo recurso categoria" in capsys.readouterr().err
    assert main(["nuevo", "recurso", "categoria", "nombre"]) == 0
    assert main(["nuevo", "recurso", "producto", "nombre", "precio:decimal", "categoria:fk"]) == 0
    modelo = leer(proyecto / "productos/models.py")
    assert 'categoria = models.ForeignKey("categorias.Categoria", on_delete=models.SET_NULL, null=True, blank=True, related_name="productos"' in modelo
    serializer = leer(proyecto / "productos/serializers.py")
    assert 'categoria_texto = serializers.StringRelatedField(source="categoria", read_only=True)' in serializer
    assert '"categoria", "categoria_texto"' in serializer
    assert 'queryset = Producto.objects.select_related("categoria")' in leer(proyecto / "productos/views.py")
    assert 'list_filter = ["categoria"]' in leer(proyecto / "productos/admin.py")
    assert '"categoria": null' in leer(proyecto / "http/productos.http")
    # Sin relaciones, el ViewSet queda como siempre.
    assert "queryset = Categoria.objects.all()" in leer(proyecto / "categorias/views.py")
    assert "_texto" not in leer(proyecto / "categorias/serializers.py")


def test_relacion_consigo_mismo(proyecto, capsys):
    assert main(["nuevo", "recurso", "categoria", "nombre", "categoria:fk"]) == 1
    assert "apunta a la misma pieza" in capsys.readouterr().err


@pytest.mark.django
@requiere_django
def test_relacion_migra_y_funciona(proyecto):
    assert main(["nuevo", "recurso", "categoria", "nombre"]) == 0
    assert main(["nuevo", "recurso", "producto", "nombre", "categoria:fk"]) == 0
    (proyecto / "productos/test_relacion.py").write_text(PRUEBA_RELACION, encoding="utf-8")
    for argumentos in (["makemigrations"], ["test"], ["spectacular", "--validate", "--fail-on-warn", "--file", "schema.yml"]):
        resultado = manage(proyecto, *argumentos)
        assert resultado.returncode == 0, f"manage.py {' '.join(argumentos)}\n{resultado.stdout}\n{resultado.stderr}"


# --- Acciones y solo lectura ---------------------------------------------------------


def test_accion_en_un_recurso_que_existe(proyecto, capsys):
    assert main(["nuevo", "accion", "producto", "destacar"]) == 1
    assert "nuevo recurso producto" in capsys.readouterr().err
    assert main(["nuevo", "recurso", "producto", "nombre", "--protegido"]) == 0
    assert main(["nuevo", "accion", "producto", "destacar", "marcar-vendido"]) == 0
    vistas = leer(proyecto / "productos/views.py")
    assert "from rest_framework.decorators import action\nfrom rest_framework.response import Response\n# --- andamio:imports" in vistas
    assert '    @action(detail=True, methods=["post"])\n    def destacar(self, request, pk=None):' in vistas
    assert '@action(detail=True, methods=["post"], url_path="marcar-vendido")' in vistas
    assert "# TODO(logica): qué hace la acción" in vistas
    assert '    def test_marcar_vendido(self):\n        objeto = self.crear()\n        respuesta = self.client.post(f"{URL}{objeto.pk}/marcar-vendido/")' in leer(proyecto / "productos/tests.py")
    assert "POST {{base}}/1/destacar/\nAuthorization: Bearer {{token}}" in leer(proyecto / "http/productos.http")
    # Otra vez: no se repite nada.
    antes = vistas
    assert main(["nuevo", "accion", "producto", "destacar"]) == 0
    assert leer(proyecto / "productos/views.py") == antes
    capsys.readouterr()
    assert main(["nuevo", "accion", "producto", "destroy"]) == 1
    assert "el ViewSet ya usa ese nombre" in capsys.readouterr().err


def test_recurso_solo_lectura(proyecto, capsys):
    assert main(["nuevo", "recurso", "pais", "nombre", "--plural", "paises", "--solo-lectura"]) == 0
    assert "class PaisViewSet(viewsets.ReadOnlyModelViewSet):" in leer(proyecto / "paises/views.py")
    tests = leer(proyecto / "paises/tests.py")
    assert "def test_solo_lectura(self):" in tests and "def test_crear" not in tests
    assert "responden 405" in leer(proyecto / "http/paises.http")
    assert main(["nuevo", "recurso", "producto", "nombre", "--solo-lectura", "--protegido"]) == 1
    assert "no tienen sentido" in capsys.readouterr().err


@pytest.mark.django
@requiere_django
def test_accion_y_solo_lectura_funcionan(proyecto):
    assert main(["nuevo", "recurso", "pais", "nombre", "--plural", "paises", "--solo-lectura"]) == 0
    assert main(["nuevo", "recurso", "producto", "nombre", "precio:decimal"]) == 0
    assert main(["nuevo", "accion", "producto", "destacar", "marcar-vendido"]) == 0
    for argumentos in (["makemigrations"], ["test"], ["spectacular", "--validate", "--fail-on-warn", "--file", "schema.yml"]):
        resultado = manage(proyecto, *argumentos)
        assert resultado.returncode == 0, f"manage.py {' '.join(argumentos)}\n{resultado.stdout}\n{resultado.stderr}"
        if argumentos[0] == "test":
            assert "Ran 10 tests" in resultado.stderr  # país: 3; producto: 5 + 2 acciones
