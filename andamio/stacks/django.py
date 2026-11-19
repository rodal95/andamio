"""Stack `django`: API REST con Django + Django REST Framework."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

from andamio.nucleo import consola
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


def _contexto_recurso(sol: Solicitud) -> dict[str, str]:
    campos = sol.campos
    nombres = [c.nombre for c in campos]
    para_str = next((c for c in campos if c.tipo in ("str", "email")), None)
    verificado = campos[0]
    valor_verificado, import_necesario = _VALOR_EN_PYTHON.get(
        verificado.tipo, (_literal(_VALORES_PRUEBA[verificado.tipo][1]), None)
    )
    return {
        "campos_modelo": "\n".join(f"{c.nombre} = {_CAMPO_MODELO[c.tipo].format(t=c.titulo)}" for c in campos),
        "verbose": " ".join(sol.nombre.palabras),
        "verbose_plural": " ".join(sol.nombre.plural_palabras),
        "str_modelo": f"self.{para_str.nombre}" if para_str else f'f"{sol.nombre.pascal} {{self.pk}}"',
        "campos_serializer": _lista(["id", *nombres, "creado", "actualizado"]),
        "campos_filtro": _lista([c.nombre for c in campos if c.tipo != "text"]),
        "campos_busqueda": _lista([c.nombre for c in campos if c.tipo in _TEXTO]),
        "campos_orden": _lista(["id", *nombres, "creado", "actualizado"]),
        "campos_admin": _lista(["id", *[c.nombre for c in campos if c.tipo != "text"]]),
        "campos_admin_filtro": _lista([c.nombre for c in campos if c.tipo in ("bool", "date", "datetime")]),
        "datos_prueba": "\n".join(f'"{c.nombre}": {_literal(_VALORES_PRUEBA[c.tipo][0])},' for c in campos),
        "datos_modificados": "\n".join(f'"{c.nombre}": {_literal(_VALORES_PRUEBA[c.tipo][1])},' for c in campos),
        "campo_verificado": verificado.nombre,
        "valor_verificado": valor_verificado,
        # La línea en blanco final separa los import de Python de los de las librerías.
        "imports_tests": f"{import_necesario}\n" if import_necesario else "",
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


def _migrar(sol: Solicitud) -> None:
    if not sol.opciones.get("migrar"):
        return
    app = sol.nombre.plural
    python = python_del_proyecto(sol.raiz)
    activar = r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate"
    comprobacion = subprocess.run(
        [python, "-c", "import django, rest_framework, django_filters, corsheaders, drf_spectacular"],
        cwd=sol.raiz,
        capture_output=True,
    )
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


def _pasos_recurso(sol: Solicitud) -> list[str]:
    pasos = [] if sol.opciones.get("migrado") else ["python manage.py makemigrations @@plural@@", "python manage.py migrate"]
    return [*pasos, "python manage.py runserver", "http://127.0.0.1:8000/api/@@plural@@/"]


RECURSO = Pieza(
    clave="recurso",
    titulo="Recurso REST",
    descripcion="app con modelo, API (CRUD), admin y tests",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("pascal", "snake"),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"migrar"}),
    contexto=_contexto_recurso,
    campos_reservados=_campos_reservados,
    marcadores={
        "campos_modelo": "una línea por campo: nombre = models.CharField(...)",
        "verbose": 'nombre en minúsculas y con espacios: "linea venta"',
        "verbose_plural": 'plural en minúsculas y con espacios: "lineas venta"',
        "str_modelo": "lo que devuelve __str__: self.nombre",
        "campos_serializer": 'campos de la API entre comillas: "id", "nombre", ...',
        "campos_filtro": "campos para ?campo=valor",
        "campos_busqueda": "campos de texto para ?search=",
        "campos_orden": "campos para ?ordering=",
        "campos_admin": "columnas de la lista del admin",
        "campos_admin_filtro": "filtros laterales del admin (sí/no y fechas)",
        "datos_prueba": 'datos de ejemplo para los tests: "nombre": "Texto de prueba",',
        "datos_modificados": "datos de ejemplo para el test de modificación",
        "campo_verificado": "campo que se controla en el test de modificación",
        "valor_verificado": "valor esperado de ese campo",
        "imports_tests": "import que necesitan los tests (puede estar vacío)",
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
    tipos=TIPOS,
    piezas={"recurso": RECURSO},
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
