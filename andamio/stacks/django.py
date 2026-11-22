"""Stack `django`: API REST con Django + Django REST Framework."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
from typing import Callable

from andamio.nucleo import consola, ejemplos, historial, relaciones
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

TIPOS = {
    "str": "texto corto (hasta 200 caracteres)",
    "text": "texto largo",
    "int": "número entero",
    "decimal": "número con 2 decimales exactos (precios)",
    "float": "número con decimales",
    "bool": "verdadero o falso",
    "date": "fecha (2025-03-15)",
    "datetime": "fecha y hora",
    "email": "correo electrónico",
}

# El recurso de la API también acepta relaciones: categoria:fk (Django con plantillas, todavía no).
TIPOS_RECURSO = {**TIPOS, relaciones.TIPO: relaciones.descripcion("otro recurso")}

_CAMPO_MODELO = {
    "str": 'models.CharField("{t}", max_length=200)',
    "text": 'models.TextField("{t}")',
    "int": 'models.IntegerField("{t}")',
    "decimal": 'models.DecimalField("{t}", max_digits=10, decimal_places=2)',
    "float": 'models.FloatField("{t}")',
    "bool": 'models.BooleanField("{t}", default=False)',
    "date": 'models.DateField("{t}")',
    "datetime": 'models.DateTimeField("{t}")',
    "email": 'models.EmailField("{t}")',
}

# Valores de ejemplo para los tests generados: (al crear, al modificar).
_VALORES_PRUEBA = {
    "str": ("Texto de prueba", "Texto modificado"),
    "text": ("Descripción de prueba", "Descripción modificada"),
    "int": (1, 2),
    "decimal": ("10.50", "20.75"),
    "float": (1.5, 2.5),
    "bool": (True, False),
    "date": ("2025-01-15", "2025-02-20"),
    "datetime": ("2025-01-15T10:30:00Z", "2025-02-20T18:45:00Z"),
    "email": ("prueba@ejemplo.com", "modificado@ejemplo.com"),
    # Una relación es opcional: los tests no necesitan crear la categoría.
    relaciones.TIPO: (None, None),
}

# Cómo se ve en Python el valor modificado después de leerlo de la base.
_VALOR_EN_PYTHON = {
    "decimal": ('Decimal("20.75")', "from decimal import Decimal"),
    "date": ("datetime.date(2025, 2, 20)", "import datetime"),
    "datetime": ("datetime.datetime(2025, 2, 20, 18, 45, tzinfo=datetime.timezone.utc)", "import datetime"),
}

_TEXTO = ("str", "text", "email")


def _detectar(raiz: Path) -> bool:
    return (raiz / "manage.py").is_file() and (raiz / "config" / "settings.py").is_file()


def _literal(valor: object) -> str:
    if isinstance(valor, str):
        return json.dumps(valor, ensure_ascii=False)
    return repr(valor)


def _lista(nombres: list[str]) -> str:
    return ", ".join(f'"{n}"' for n in nombres)


def _relaciones(sol: Solicitud) -> list[relaciones.Relacion]:
    """Los campos :fk, controlando que exista la app del recurso al que apuntan."""
    lista = relaciones.de_campos(sol.raiz, sol.campos, sol.nombre, ("recurso",))
    for rel in lista:
        try:
            modelos = (sol.raiz / rel.destino.plural / "models.py").read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            modelos = ""
        if f"class {rel.destino.pascal}(" not in modelos:
            raise relaciones.falta(rel.campo, f"el recurso '{rel.campo.nombre}' (la app {rel.destino.plural})", f"python -m andamio nuevo recurso {rel.campo.nombre} nombre:str")
    return lista


def _campo_modelo(campo, plural_propio: str, destinos: dict) -> str:
    if campo.nombre in destinos:
        destino = destinos[campo.nombre]
        # SET_NULL: si se borra la categoría, el producto queda sin categoría (no se pierde ni falla).
        return (
            f'models.ForeignKey("{destino.plural}.{destino.pascal}", on_delete=models.SET_NULL, null=True, blank=True, '
            f'related_name="{plural_propio}", verbose_name="{campo.titulo}")'
        )
    return _CAMPO_MODELO[campo.tipo].format(t=campo.titulo)


def _contexto_recurso(sol: Solicitud) -> dict[str, str]:
    campos = sol.campos
    nombres = [c.nombre for c in campos]
    rels = _relaciones(sol)
    destinos = {r.campo.nombre: r.destino for r in rels}
    con_texto = [n for c in campos for n in ((c.nombre, f"{c.nombre}_texto") if c.nombre in destinos else (c.nombre,))]
    para_str = next((c for c in campos if c.tipo in ("str", "email")), None)
    verificado = next((c for c in campos if c.tipo != relaciones.TIPO), campos[0])
    valor_verificado, import_necesario = _VALOR_EN_PYTHON.get(
        verificado.tipo, (_literal(_VALORES_PRUEBA[verificado.tipo][1]), None)
    )
    return {
        "campos_modelo": "\n".join(f"{c.nombre} = {_campo_modelo(c, sol.nombre.plural, destinos)}" for c in campos),
        "verbose": " ".join(sol.nombre.palabras),
        "verbose_plural": " ".join(sol.nombre.plural_palabras),
        "str_modelo": f"self.{para_str.nombre}" if para_str else f'f"{sol.nombre.pascal} {{self.pk}}"',
        "campos_serializer": _lista(["id", *con_texto, "creado", "actualizado"]),
        # La API devuelve el id de la relación y, además, su texto (para mostrarlo sin otra consulta).
        "campos_relacion": "".join(
            f'{n}_texto = serializers.StringRelatedField(source="{n}", read_only=True)\n' for n in destinos
        ),
        # select_related trae la relación en la misma consulta (si no, una consulta por fila).
        "queryset": f"{sol.nombre.pascal}.objects.select_related({_lista(list(destinos))})" if destinos else f"{sol.nombre.pascal}.objects.all()",
        "campos_filtro": _lista([c.nombre for c in campos if c.tipo != "text"]),
        "campos_busqueda": _lista([c.nombre for c in campos if c.tipo in _TEXTO]),
        "campos_orden": _lista(["id", *nombres, "creado", "actualizado"]),
        "campos_admin": _lista(["id", *[c.nombre for c in campos if c.tipo != "text"]]),
        "campos_admin_filtro": _lista([c.nombre for c in campos if c.tipo in ("bool", "date", "datetime", relaciones.TIPO)]),
        "datos_prueba": "\n".join(f'"{c.nombre}": {_literal(_VALORES_PRUEBA[c.tipo][0])},' for c in campos),
        "datos_modificados": "\n".join(f'"{c.nombre}": {_literal(_VALORES_PRUEBA[c.tipo][1])},' for c in campos),
        "campo_verificado": verificado.nombre,
        "valor_verificado": valor_verificado,
        # La línea en blanco final separa los import de Python de los de las librerías.
        "imports_tests": f"{import_necesario}\n" if import_necesario else "",
        **_contexto_permisos(sol),
    }


_PREPARAR_TESTS_PROTEGIDO = """\
def setUp(self):
    # El recurso está protegido (--protegido): los tests entran con un usuario.
    usuario = get_user_model().objects.create_user("prueba", password="clave-de-prueba-123")
    self.client.force_authenticate(usuario)

def test_sin_login_no_se_puede_crear(self):
    self.client.force_authenticate(None)
    respuesta = self.client.post(URL, DATOS, format="json")
    # 401 con el login de JWT (andamio nuevo login); 403 si solo hay sesión.
    self.assertIn(respuesta.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
    # Leer sigue siendo libre.
    self.assertEqual(self.client.get(URL).status_code, status.HTTP_200_OK)
"""


_PREPARAR_TESTS_OBLIGATORIO = """\
def setUp(self):
    # Toda la API pide login (nuevo login --obligatorio): los tests entran con un usuario.
    usuario = get_user_model().objects.create_user("prueba", password="clave-de-prueba-123")
    self.client.force_authenticate(usuario)

def test_sin_login_no_se_puede_ver(self):
    self.client.force_authenticate(None)
    self.assertEqual(self.client.get(URL).status_code, status.HTTP_401_UNAUTHORIZED)
"""

# La línea que agrega nuevo login --obligatorio en config/settings.py.
_PERMISO_OBLIGATORIO = 'REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = ["rest_framework.permissions.IsAuthenticated"]'

_CONFIG_OBLIGATORIO = f"""
# Toda la API pide login (nuevo login --obligatorio): sin token, 401. Registrarse, pedir el
# token y la documentación siguen abiertos (sus vistas lo dicen). Un recurso --protegido
# sigue dejando ver: su vista lo dice (IsAuthenticatedOrReadOnly).
{_PERMISO_OBLIGATORIO}"""


def login_obligatorio(raiz: Path) -> bool:
    """Si el proyecto tiene el login obligatorio para toda la API (nuevo login --obligatorio)."""
    try:
        return _PERMISO_OBLIGATORIO in (raiz / "config" / "settings.py").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return False


def _contexto_permisos(sol: Solicitud) -> dict[str, str]:
    """--protegido: cualquiera puede leer; para crear, modificar y eliminar hay que tener login.

    Con el login obligatorio (nuevo login --obligatorio), los tests entran con un usuario.
    """
    if not sol.opciones.get("protegido"):
        if login_obligatorio(sol.raiz):
            return {
                "import_permisos": "",
                "permisos": "",
                "import_usuario": "from django.contrib.auth import get_user_model",
                "preparar_tests": _PREPARAR_TESTS_OBLIGATORIO,
            }
        return {"import_permisos": "", "permisos": "", "import_usuario": "", "preparar_tests": ""}
    return {
        "import_permisos": "from rest_framework.permissions import IsAuthenticatedOrReadOnly",
        "permisos": "# Leer es libre; crear, modificar y eliminar necesitan login (token JWT o sesión).\n"
        "permission_classes = [IsAuthenticatedOrReadOnly]",
        "import_usuario": "from django.contrib.auth import get_user_model",
        "preparar_tests": _PREPARAR_TESTS_PROTEGIDO,
    }


# --- Validación de nombres ------------------------------------------------------

_NOMBRES_OCUPADOS = {
    **{n: "es una app de Django" for n in ("admin", "auth", "contenttypes", "sessions", "messages", "staticfiles")},
    **{
        n: "es una librería que usa el proyecto"
        for n in (
            "django",
            "rest_framework",
            "django_filters",
            "corsheaders",
            "drf_spectacular",
            "drf_spectacular_sidecar",
            "dotenv",
            "dj_database_url",
        )
    },
    "config": "es la carpeta de configuración del proyecto",
    "api": "chocaría con la ruta /api/",
    "docs": "chocaría con la documentación en /api/docs/",
    "schema": "chocaría con /api/schema/",
    "static": "es la carpeta de archivos estáticos",
    "media": "es la carpeta de archivos subidos",
    "templates": "es la carpeta de plantillas HTML",
    "tests": "confunde al buscador de tests",
    "test": "confunde al buscador de tests",
    "manage": "ya existe manage.py",
}


def _validar_nombre(raiz: Path, nombre: Nombre) -> None:
    app = nombre.plural
    motivo = _NOMBRES_OCUPADOS.get(app)
    if motivo is None and app in sys.stdlib_module_names:
        motivo = "es el nombre de un módulo de Python y la app no se podría importar"
    if motivo is None:
        try:
            if f'"{app}"' in (raiz / "config" / "settings.py").read_text(encoding="utf-8-sig"):
                motivo = "ya está registrada en LOCAL_APPS (config/settings.py)"
        except (OSError, UnicodeDecodeError):
            pass
    if motivo:
        raise AndamioError(
            f"No se puede crear la app '{app}': {motivo}.",
            "Elegí otro nombre, o indicá otro plural con --plural.",
        )


_ATRIBUTOS_DE_MODELO = (
    "objects",
    "save",
    "delete",
    "clean",
    "clean_fields",
    "full_clean",
    "validate_unique",
    "validate_constraints",
    "refresh_from_db",
    "serializable_value",
    "check",
    "from_db",
    "get_deferred_fields",
    "save_base",
)


def _campos_reservados(nombre: Nombre) -> dict[str, str]:
    reservados = {n: "es un nombre que Django usa en los modelos" for n in _ATRIBUTOS_DE_MODELO}
    reservados["search"] = "lo usa la API para buscar (?search=)"
    reservados["ordering"] = "lo usa la API para ordenar (?ordering=)"
    reservados["format"] = "lo usa la API para elegir el formato (?format=json)"
    return reservados


# --- Migraciones (--migrar) -------------------------------------------------------


def python_del_proyecto(raiz: Path) -> str:
    """El Python del entorno virtual del proyecto; si no hay, el activo; si no, el actual."""
    carpetas = [raiz / nombre for nombre in (".venv", "venv", "env")]
    if os.environ.get("VIRTUAL_ENV"):
        carpetas.append(Path(os.environ["VIRTUAL_ENV"]))
    for carpeta in carpetas:
        for ejecutable in (carpeta / "Scripts" / "python.exe", carpeta / "bin" / "python"):
            if ejecutable.is_file():
                return str(ejecutable)
    return sys.executable


def migrador(modulos: str) -> Callable[[Solicitud], None]:
    """--migrar: makemigrations y migrate. `modulos` son los import que tienen que funcionar antes."""

    def migrar(sol: Solicitud) -> None:
        if not sol.opciones.get("migrar"):
            return
        app = sol.nombre.plural
        python = python_del_proyecto(sol.raiz)
        activar = r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate"
        comprobacion = subprocess.run([python, "-c", f"import {modulos}"], cwd=sol.raiz, capture_output=True)
        if comprobacion.returncode != 0:
            raise AndamioError(
                f"Los archivos se generaron, pero no se pudo migrar: falta instalar Django en {python}.",
                f"Activá el entorno virtual ({activar}), instalá las dependencias "
                f"(pip install -r requirements.txt) y ejecutá: python manage.py makemigrations {app}",
            )
        for argumentos in (["makemigrations", app], ["migrate"]):
            comando = "python manage.py " + " ".join(argumentos)
            consola.escribir()
            consola.titulo(f"Ejecutando: {comando}")
            # En otro proceso: este proceso no tiene cargada la app nueva.
            resultado = subprocess.run([python, "manage.py", *argumentos], cwd=sol.raiz)
            if resultado.returncode != 0:
                raise AndamioError(
                    f"Falló '{comando}'. Los archivos del recurso se generaron igual.",
                    f"Leé el error de arriba, corregilo y ejecutá de nuevo: {comando}",
                )
        sol.opciones["migrado"] = True

    return migrar


_migrar = migrador("django, rest_framework, django_filters, corsheaders, drf_spectacular")


def _pasos_recurso(sol: Solicitud) -> list[str]:
    pasos = [] if sol.opciones.get("migrado") else ["python manage.py makemigrations @@plural@@", "python manage.py migrate"]
    return [*pasos, "python manage.py runserver", "http://127.0.0.1:8000/api/@@plural@@/"]



_TESTS_ESCRITURA = """\
def test_crear(self):
    respuesta = self.client.post(URL, DATOS, format="json")
    self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.json())
    self.assertEqual({modelo}.objects.count(), 1)

def test_actualizar(self):
    objeto = self.crear()
    respuesta = self.client.put(f"{{URL}}{{objeto.pk}}/", DATOS_MODIFICADOS, format="json")
    self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.json())
    objeto.refresh_from_db()
    self.assertEqual(objeto.{campo}, {valor})

def test_eliminar(self):
    objeto = self.crear()
    respuesta = self.client.delete(f"{{URL}}{{objeto.pk}}/")
    self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
    self.assertFalse({modelo}.objects.filter(pk=objeto.pk).exists())"""

_TESTS_SOLO_LECTURA = """\
def test_solo_lectura(self):
    # --solo-lectura: la API no crea, modifica ni elimina (405); los datos se cargan desde /admin/.
    objeto = self.crear()
    for respuesta in (
        self.client.post(URL, DATOS, format="json"),
        self.client.put(f"{URL}{objeto.pk}/", DATOS_MODIFICADOS, format="json"),
        self.client.delete(f"{URL}{objeto.pk}/"),
    ):
        self.assertEqual(respuesta.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)"""


def _contexto_lectura(sol: Solicitud, contexto: dict[str, str]) -> dict[str, str]:
    """--solo-lectura: un ReadOnlyModelViewSet (listar y ver) y sus tests."""
    if not sol.opciones.get("solo_lectura"):
        return {
            "clase_viewset": "ModelViewSet",
            "doc_viewset": "Listar, crear, ver, modificar y eliminar",
            "tests_escritura": _TESTS_ESCRITURA.format(
                modelo=sol.nombre.pascal, campo=contexto["campo_verificado"], valor=contexto["valor_verificado"]
            ),
            "http_solo_lectura": "",
        }
    if sol.opciones.get("protegido"):
        raise AndamioError(
            "--solo-lectura y --protegido juntos no tienen sentido: con --solo-lectura la API no crea, modifica ni elimina.",
            "Elegí una de las dos.",
        )
    return {
        "clase_viewset": "ReadOnlyModelViewSet",
        "doc_viewset": "Listar y ver (solo lectura: los datos se cargan desde /admin/)",
        "tests_escritura": _TESTS_SOLO_LECTURA,
        "http_solo_lectura": "#\n# Solo lectura (--solo-lectura): crear, reemplazar, modificar y eliminar responden 405.\n# Los datos se cargan desde el panel /admin/.",
    }


def _contexto_recurso_api(sol: Solicitud) -> dict[str, str]:
    """El del recurso, más el archivo http/<plural>.http para probar la API a mano."""
    protegido = bool(sol.opciones.get("protegido"))
    http = ejemplos.contexto_http(sol.campos, "http://127.0.0.1:8000/api", "python manage.py runserver", protegido)
    contexto = _contexto_recurso(sol)
    return {**contexto, **http, **_contexto_lectura(sol, contexto)}


RECURSO = Pieza(
    clave="recurso",
    lectura=(
        ('@@plural@@/models.py', 'el modelo: la tabla y sus campos'),
        ('@@plural@@/serializers.py', 'cómo se convierte a JSON y qué se valida'),
        ('@@plural@@/views.py', 'la API: listar, crear, ver, modificar y eliminar'),
        ('@@plural@@/urls.py', 'las rutas /api/@@plural@@/'),
        ('@@plural@@/tests.py', 'los tests: lo que la API tiene que cumplir'),
        ('http/@@plural@@.http', 'peticiones para probar la API a mano'),
    ),
    titulo="Recurso REST",
    descripcion="app con modelo, API (CRUD), admin y tests",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("pascal", "snake"),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"migrar", "protegido", "solo_lectura"}),
    contexto=_contexto_recurso_api,
    campos_reservados=_campos_reservados,
    marcadores={
        **ejemplos.MARCADORES_HTTP,
        "campos_modelo": "una línea por campo: nombre = models.CharField(...)",
        "verbose": 'nombre en minúsculas y con espacios: "linea venta"',
        "verbose_plural": 'plural en minúsculas y con espacios: "lineas venta"',
        "str_modelo": "lo que devuelve __str__: self.nombre",
        "campos_serializer": 'campos de la API entre comillas: "id", "nombre", ...',
        "campos_filtro": "campos para ?campo=valor",
        "campos_busqueda": "campos de texto para ?search=",
        "campos_orden": "campos para ?ordering=",
        "campos_admin": "columnas de la lista del admin",
        "campos_admin_filtro": "filtros laterales del admin (sí/no, fechas y relaciones)",
        "campos_relacion": "en el serializer, el texto de cada relación: categoria_texto = ... (vacío sin campos :fk)",
        "queryset": "la consulta del ViewSet: Producto.objects.all(), o con select_related si hay relaciones",
        "datos_prueba": 'datos de ejemplo para los tests: "nombre": "Texto de prueba",',
        "datos_modificados": "datos de ejemplo para el test de modificación",
        "campo_verificado": "campo que se controla en el test de modificación",
        "valor_verificado": "valor esperado de ese campo",
        "imports_tests": "import que necesitan los tests (puede estar vacío)",
        "import_permisos": "import de IsAuthenticatedOrReadOnly (vacío sin --protegido)",
        "permisos": "permission_classes del ViewSet (vacío sin --protegido)",
        "import_usuario": "import de get_user_model para los tests (vacío sin --protegido)",
        "preparar_tests": "setUp con un usuario y el test sin login (vacío sin --protegido)",
        "clase_viewset": "ModelViewSet, o ReadOnlyModelViewSet con --solo-lectura",
        "doc_viewset": "la primera línea del docstring del ViewSet: qué hace",
        "tests_escritura": "los tests de crear, actualizar y eliminar (con --solo-lectura, uno que controla el 405)",
        "http_solo_lectura": "con --solo-lectura, el aviso de que crear, modificar y eliminar responden 405",
    },
    existe_si=("@@plural@@",),
    inserciones=(
        Insercion(
            "config/settings.py",
            '"@@plural@@",',
            marcador="apps",
            descripcion="app en LOCAL_APPS",
            ubicacion="dentro de la lista LOCAL_APPS",
        ),
        Insercion(
            "config/urls.py",
            'path("api/", include("@@plural@@.urls")),',
            marcador="urls",
            descripcion="rutas /api/@@plural@@/",
            ubicacion="dentro de la lista urlpatterns",
        ),
    ),
    siguiente_paso=_pasos_recurso,
    despues=_migrar,
    confirmaciones={"migrar": "¿Ejecutar ahora las migraciones (makemigrations y migrate)?"},
)


# --- Login con JWT (SimpleJWT) ----------------------------------------------------

VERSION_SIMPLEJWT = "5.5.1"

_CONFIG_JWT = """
# --- Login con JWT (lo agregó: andamio nuevo login) ------------------------------
# La API acepta el token de acceso en el encabezado  Authorization: Bearer <token>
# y también la sesión del panel /admin/ (útil para probar en el navegador).
from datetime import timedelta  # noqa: E402

# Como app, para que sus mensajes ("Usuario o contraseña incorrectos"...) salgan en español.
INSTALLED_APPS += ["rest_framework_simplejwt"]

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",
]

SIMPLE_JWT = {
    # El token de acceso dura poco; con el de refresco se pide uno nuevo sin volver a loguearse.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}"""


def _validar_login(raiz: Path, nombre: Nombre) -> None:
    try:
        settings = (raiz / "config" / "settings.py").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return
    if "JWTAuthentication" in settings:
        raise AndamioError(
            "El proyecto ya tiene el login con JWT (JWTAuthentication está en config/settings.py).",
            "Para proteger un recurso nuevo: python -m andamio nuevo recurso <nombre> <campos> --protegido",
        )
    # El login es una app más (por defecto "cuentas"). Si ya hay una app con ese nombre
    # (ej.: un recurso "cuenta" de un banco), el login se genera con otro nombre.
    if f'"{nombre.plural}"' in settings or (raiz / nombre.plural).exists():
        raise AndamioError(
            f"Ya hay una app '{nombre.plural}' en el proyecto, así que el login no puede usar ese nombre.",
            f"Generalo con otro nombre: {consola.programa()} nuevo login acceso",
        )


def _tests_sin_login(raiz: Path, login: str) -> list[str]:
    """Las apps cuyos tests piden sin usuario: con el login obligatorio, responderían 401."""
    apps = []
    for tests in sorted(raiz.glob("*/tests.py")):
        if tests.parent.name == login:
            continue
        try:
            texto = tests.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        if "APITestCase" in texto and "force_authenticate" not in texto:
            apps.append(tests.parent.name)
    return apps


def _pasos_login(sol: Solicitud) -> list[str]:
    avisos = []
    if sol.opciones.get("obligatorio"):
        for app in _tests_sin_login(sol.raiz, sol.nombre.plural):
            avisos.append(
                f"# {app}/tests.py pide sin usuario y ahora la API responde 401: en su setUp, "
                "self.client.force_authenticate(get_user_model().objects.create_user(\"prueba\", password=\"clave-de-prueba-123\"))"
            )
    return [
        *avisos,
        "pip install -r requirements.txt",
        "python manage.py createsuperuser",
        "python manage.py runserver",
        "# Pedí un token: POST /api/token/ con {\"username\": ..., \"password\": ...}",
        "http://127.0.0.1:8000/api/docs/",
        "# Para que un recurso pida login al crear, modificar y eliminar: nuevo recurso ... --protegido",
    ]


# --- Acciones propias de un recurso (nuevo accion producto destacar) -----------------

# Métodos que ya tiene un ViewSet: una acción con ese nombre lo pisaría.
_METODOS_VIEWSET = {
    "list", "create", "retrieve", "update", "partial_update", "destroy", "get_object", "get_queryset",
    "get_serializer", "get_serializer_class", "perform_create", "perform_update", "perform_destroy",
    "initial", "dispatch", "options", "filter_queryset", "paginate_queryset", "action", "request", "response",
}  # fmt: skip

_CODIGO_ACCION = """
@action(detail=True, methods=["post"]{url_path})
def {accion}(self, request, pk=None):
    \"\"\"POST /api/{plural}/<id>/{ruta}/: {descripcion}\"\"\"
    {variable} = self.get_object()
    # TODO(logica): qué hace la acción. Ejemplo: {variable}.{accion}_en = timezone.now(); {variable}.save()
    return Response(self.get_serializer({variable}).data)"""

_TEST_ACCION = """
def test_{accion}(self):
    objeto = self.crear()
    respuesta = self.client.post(f"{{URL}}{{objeto.pk}}/{ruta}/")
    self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.json())"""

_HTTP_ACCION = """
### Acción {ruta} sobre el registro 1
POST {{{{base}}}}/1/{ruta}/
{auth}"""


def _contexto_accion(sol: Solicitud) -> dict[str, str]:
    entrada = historial.ultima(sol.raiz, sol.nombre.snake, ("recurso",))
    nombre = entrada.nombre if entrada else sol.nombre
    vistas = sol.raiz / nombre.plural / "views.py"
    try:
        texto = vistas.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        texto = ""
    if f"class {nombre.pascal}ViewSet(" not in texto:
        raise AndamioError(
            f"No existe el recurso '{nombre.snake}' ({nombre.plural}/views.py con {nombre.pascal}ViewSet).",
            f"Generalo primero: python -m andamio nuevo recurso {nombre.snake} nombre:str",
        )
    protegido = bool(entrada and entrada.opciones.get("protegido"))
    codigo, tests, http = [], [], []
    for campo in sol.campos:
        accion = campo.nombre
        if accion in _METODOS_VIEWSET or accion == nombre.snake:
            raise AndamioError(f"No se puede usar '{accion}' como acción: el ViewSet ya usa ese nombre.", "Elegí otro nombre.")
        ruta = accion.replace("_", "-")
        codigo.append(
            _CODIGO_ACCION.format(
                accion=accion,
                url_path=f', url_path="{ruta}"' if ruta != accion else "",
                plural=nombre.plural,
                ruta=ruta,
                descripcion=f"la acción {ruta} sobre un {' '.join(nombre.palabras)}.",
                # El nombre del recurso, salvo que choque con lo que ya usa el método.
                variable=nombre.snake if nombre.snake not in ("self", "request", "pk", "action", "status") else "objeto",
            )
        )
        tests.append(_TEST_ACCION.format(accion=accion, ruta=ruta))
        http.append(_HTTP_ACCION.format(ruta=ruta, auth="Authorization: Bearer {{token}}" if protegido else "").rstrip())
    return {
        **nombre.marcadores(),
        "codigo_acciones": "\n".join(codigo),
        "tests_acciones": "\n".join(tests),
        "http_acciones": "\n".join(http),
    }


ACCION = Pieza(
    clave="accion",
    lectura=(
        ('@@plural@@/views.py', 'la acción, al final del ViewSet (con la marca para tu lógica)'),
        ('@@plural@@/tests.py', 'su test: responde 200'),
        ('http/@@plural@@.http', 'la petición para probarla a mano'),
    ),
    titulo="Acción",
    descripcion="una acción propia en un recurso que ya existe: POST /api/<plural>/<id>/<acción>/",
    ejemplo="producto destacar",
    preparar=("recurso producto nombre:str precio:decimal",),
    formas=("snake",),
    usa_campos=True,
    define_campos=False,
    usa_existente=True,
    contexto=_contexto_accion,
    marcadores={
        "codigo_acciones": "el @action de cada acción, para el final del ViewSet",
        "tests_acciones": "un test por acción (responde 200)",
        "http_acciones": "una petición POST por acción, para el archivo .http",
    },
    inserciones=(
        Insercion(
            "@@plural@@/views.py",
            "from rest_framework.decorators import action\nfrom rest_framework.response import Response",
            marcador="imports",
            descripcion="imports de action y Response",
            ubicacion="arriba, junto a from rest_framework import viewsets",
        ),
        Insercion(
            "@@plural@@/views.py",
            "@@codigo_acciones@@",
            marcador="acciones",
            descripcion="la acción en el ViewSet",
            ubicacion="al final de la clase @@Nombre@@ViewSet (con 4 espacios de sangría)",
        ),
        Insercion(
            "@@plural@@/tests.py",
            "@@tests_acciones@@",
            marcador="tests",
            descripcion="el test de la acción",
            ubicacion="al final de la clase @@Nombre@@APITest (con 4 espacios de sangría)",
        ),
        Insercion("http/@@plural@@.http", "@@http_acciones@@", descripcion="la petición (al final)"),
    ),
    siguiente_paso=["python manage.py test @@plural@@", "python manage.py runserver", "http://127.0.0.1:8000/api/docs/"],
)


LOGIN = Pieza(
    clave="login",
    lectura=(
        ('@@plural@@/serializers.py', 'qué datos pide el registro y cómo se valida la clave'),
        ('@@plural@@/views.py', 'registrarse (/api/registro/) y el usuario actual (/api/yo/)'),
        ('@@plural@@/urls.py', 'las rutas, incluidas las del token (/api/token/)'),
        ('http/login.http', 'peticiones para registrarse, pedir el token y usarlo'),
        ('@@plural@@/tests.py', 'los tests del login'),
    ),
    titulo="Login con JWT",
    descripcion="registro, token de acceso (SimpleJWT) y usuario actual",
    ejemplo="",
    nombre_defecto="cuenta",
    pregunta_nombre="Nombre de la app del login (Enter para cuenta)",
    formas=("app @@plural@@",),
    opciones=frozenset({"obligatorio"}),
    validar_nombre=_validar_login,
    existe_si=("@@plural@@",),
    inserciones=(
        Insercion(
            "config/settings.py",
            '"@@plural@@",',
            marcador="apps",
            descripcion="app en LOCAL_APPS",
            ubicacion="dentro de la lista LOCAL_APPS",
        ),
        Insercion("config/settings.py", _CONFIG_JWT, descripcion="autenticación con JWT (al final)"),
        Insercion("config/settings.py", _CONFIG_OBLIGATORIO, descripcion="toda la API pide login (al final)", condicion=lambda sol: bool(sol.opciones.get("obligatorio"))),
        Insercion(
            "config/urls.py",
            'path("api/", include("@@plural@@.urls")),',
            marcador="urls",
            descripcion="rutas /api/token/, /api/registro/ y /api/yo/",
            ubicacion="dentro de la lista urlpatterns",
        ),
        Insercion(
            "requirements.txt",
            f"# Login con tokens JWT (andamio nuevo login).\ndjangorestframework-simplejwt~={VERSION_SIMPLEJWT}",
            descripcion="djangorestframework-simplejwt",
        ),
    ),
    siguiente_paso=_pasos_login,
)


def _contexto_proyecto(nombre: Nombre) -> dict[str, str]:
    return {
        "secret_key": "cambiar-por-una-clave-larga-y-secreta",
        "activar": r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate",
    }


STACK = Stack(
    clave="django",
    titulo="Django REST",
    senal="manage.py y config/settings.py",
    detectar=_detectar,
    tipos=TIPOS_RECURSO,
    piezas={"recurso": RECURSO, "accion": ACCION, "login": LOGIN},
    ejemplo_proyecto="mi-api",
    siguiente_paso_proyecto=[
        "cd @@carpeta@@",
        "python -m venv .venv",
        "@@activar@@",
        "pip install -r requirements.txt",
        "python manage.py migrate",
        "python manage.py runserver",
        "http://127.0.0.1:8000/api/docs/",
    ],
    contexto_proyecto=_contexto_proyecto,
    contexto_env=lambda: {"secret_key": secrets.token_urlsafe(50)},
    validar_nombre=_validar_nombre,
)
