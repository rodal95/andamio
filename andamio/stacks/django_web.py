"""Stack `django-web`: sitio web con Django y plantillas HTML (todo en un proyecto, "monolito").

Es la otra forma de usar Django: en lugar de una API que usa un frontend aparte, el
servidor arma las páginas HTML con plantillas. Trae login, registro y admin.
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.estilos import piezas_de_estilos
from andamio.stacks import django
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

TIPOS = django.TIPOS

# Valores de ejemplo que manda el formulario en los tests: (al crear, al modificar).
# Son textos, como los manda el navegador.
_VALORES_FORMULARIO = {
    "str": ("Texto de prueba", "Texto modificado"),
    "text": ("Descripción de prueba", "Descripción modificada"),
    "int": ("1", "2"),
    "decimal": ("10.50", "20.75"),
    "float": ("1.5", "2.5"),
    "bool": ("on", ""),
    "date": ("2025-01-15", "2025-02-20"),
    "datetime": ("2025-01-15T10:30", "2025-02-20T18:45"),
    "email": ("prueba@ejemplo.com", "modificado@ejemplo.com"),
}

# Controles del navegador para fechas (si no, Django muestra un cuadro de texto común).
_WIDGETS = {
    "date": 'forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")',
    "datetime": 'forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")',
}

_FILTROS_PLANTILLA = {
    "bool": '|yesno:"Sí,No"',
    "date": '|date:"d/m/Y"',
    "datetime": '|date:"d/m/Y H:i"',
    "text": "|linebreaksbr",
}


def _detectar(raiz: Path) -> bool:
    return django._detectar(raiz) and (raiz / "templates" / "base.html").is_file()


def _valor(campo, indice: int) -> str:
    return json.dumps(_VALORES_FORMULARIO[campo.tipo][indice], ensure_ascii=False)


def _contexto_crud(sol: Solicitud) -> dict[str, str]:
    contexto = django._contexto_recurso(sol)
    campos = sol.campos
    variable = sol.nombre.snake
    textos = [c for c in campos if c.tipo in ("str", "text", "email")]
    para_str = next((c for c in campos if c.tipo in ("str", "email")), None)
    widgets = {c.nombre: _WIDGETS[c.tipo] for c in campos if c.tipo in _WIDGETS}
    en_tabla = [c for c in campos if c.tipo != "text"] or campos
    if textos:
        condicion = " | ".join(f"Q({c.nombre}__icontains=texto)" for c in textos)
        filtro = f"consulta = consulta.filter({condicion})"
    else:
        filtro = "consulta = consulta.filter(Q(pk=int(texto)) if texto.isdigit() else Q(pk__in=[]))"
    # Con checkbox, "no marcado" es no mandar el campo (como el navegador).
    datos = [f'"{c.nombre}": {_valor(c, 0)},' for c in campos]
    modificados = [f'"{c.nombre}": {_valor(c, 1)},' for c in campos if not (c.tipo == "bool")]
    verificado = next((c for c in campos if c.tipo != "bool"), campos[0])
    protegido = bool(sol.opciones.get("protegido"))
    contexto.update(
        campos_form=", ".join(f'"{c.nombre}"' for c in campos),
        widgets=(
            "widgets = {\n" + "\n".join(f'    "{n}": {w},' for n, w in widgets.items()) + "\n}" if widgets else ""
        ),
        filtro_busqueda=filtro,
        mensaje_creado=f'"Se agregó «%({para_str.nombre})s»."' if para_str else f'"Se agregó {" ".join(sol.nombre.palabras)}."',
        columnas_encabezado="\n".join(f"<th>{c.titulo}</th>" for c in en_tabla),
        columnas_fila="\n".join(f"<td>{{{{ {variable}.{c.nombre}{_FILTROS_PLANTILLA.get(c.tipo, '')} }}}}</td>" for c in en_tabla),
        campos_detalle="\n".join(
            f"<dt>{c.titulo}</dt>\n<dd>{{{{ {variable}.{c.nombre}{_FILTROS_PLANTILLA.get(c.tipo, '')} }}}}</dd>" for c in campos
        ),
        datos_prueba="\n".join(datos),
        datos_modificados="\n".join(modificados),
        campo_verificado=verificado.nombre,
        import_login="from django.contrib.auth.mixins import LoginRequiredMixin" if protegido else "",
        mixin_login="LoginRequiredMixin, " if protegido else "",
        import_usuario="from django.contrib.auth import get_user_model" if protegido else "",
        preparar_tests=_PREPARAR_TESTS_PROTEGIDO if protegido else "",
    )
    return contexto


_PREPARAR_TESTS_PROTEGIDO = """\
def setUp(self):
    # El crud está protegido (--protegido): los tests entran con un usuario.
    self.usuario = get_user_model().objects.create_user("prueba", password="clave-de-prueba-123")
    self.client.force_login(self.usuario)

def test_sin_login_pide_ingresar(self):
    self.client.logout()
    respuesta = self.client.get(f"{URL}nuevo/")
    self.assertRedirects(respuesta, f"/cuentas/login/?next={URL}nuevo/")
    # Ver la lista sigue siendo libre.
    self.assertEqual(self.client.get(URL).status_code, 200)
"""


_NOMBRES_OCUPADOS = {
    "cuentas": "lo usan las rutas de login (/cuentas/)",
    "paginas": "es la carpeta de las páginas (templates/paginas/)",
    "registration": "es la carpeta de las plantillas de login",
}


def _validar_nombre(raiz: Path, nombre: Nombre) -> None:
    for forma in (nombre.plural, nombre.snake):
        if forma in _NOMBRES_OCUPADOS:
            raise AndamioError(f"No se puede usar '{forma}': {_NOMBRES_OCUPADOS[forma]}.", "Elegí otro nombre.")


def _validar_crud(raiz: Path, nombre: Nombre) -> None:
    django._validar_nombre(raiz, nombre)


_RUTAS_OCUPADAS = {"admin", "cuentas", "static", "media", "inicio", "login", "logout", "registro"}


def _validar_pagina(raiz: Path, nombre: Nombre) -> None:
    if nombre.kebab in _RUTAS_OCUPADAS or nombre.snake in _RUTAS_OCUPADAS:
        raise AndamioError(f"La ruta /{nombre.kebab}/ ya la usa el proyecto.", "Elegí otro nombre para la página.")
    try:
        urls = (raiz / "config" / "urls.py").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return
    if f'path("{nombre.kebab}/"' in urls or f'name="{nombre.snake}"' in urls:
        raise AndamioError(
            f"Ya hay una página en /{nombre.kebab}/ (config/urls.py).", "Elegí otro nombre, o borrá esa ruta si ya no la usás."
        )


def _pasos_crud(sol: Solicitud) -> list[str]:
    pasos = [] if sol.opciones.get("migrado") else ["python manage.py makemigrations @@plural@@", "python manage.py migrate"]
    return [*pasos, "python manage.py runserver", "http://127.0.0.1:8000/@@pluralKebab@@/"]


_MARCADORES_CRUD = {
    **django.RECURSO.marcadores,
    "campos_form": "campos del formulario entre comillas",
    "widgets": "controles de fecha del formulario (vacío si no hay fechas)",
    "filtro_busqueda": "cómo busca la lista con ?q=",
    "mensaje_creado": "mensaje después de crear",
    "columnas_encabezado": "un <th> por campo de la tabla",
    "columnas_fila": "un <td> por campo de la tabla",
    "campos_detalle": "un <dt> y un <dd> por campo",
    "import_login": "import de LoginRequiredMixin (vacío sin --protegido)",
    "mixin_login": "LoginRequiredMixin en las vistas que modifican (vacío sin --protegido)",
}

CRUD = Pieza(
    clave="crud",
    titulo="CRUD con plantillas",
    descripcion="app con modelo, formulario, vistas, plantillas HTML, rutas, admin y tests",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "app @@plural@@", "ruta /@@pluralKebab@@/"),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"migrar", "protegido"}),
    contexto=_contexto_crud,
    campos_reservados=django._campos_reservados,
    validar_nombre=_validar_crud,
    marcadores=_MARCADORES_CRUD,
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
            'path("@@pluralKebab@@/", include("@@plural@@.urls")),',
            marcador="urls",
            descripcion="rutas /@@pluralKebab@@/",
            ubicacion="dentro de la lista urlpatterns",
        ),
        Insercion(
            "templates/base.html",
            "<a href=\"{% url '@@plural@@:lista' %}\">@@titulo@@</a>",
            marcador="enlaces",
            descripcion="enlace en el menú",
            ubicacion="dentro de <nav>",
            comentario="{#",
        ),
    ),
    siguiente_paso=_pasos_crud,
    despues=django.migrador("django, dotenv, dj_database_url"),
    confirmaciones={"migrar": "¿Ejecutar ahora las migraciones (makemigrations y migrate)?"},
)

PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="plantilla HTML con su ruta y su enlace en el menú",
    ejemplo="Contacto",
    formas=("templates/paginas/@@nombreKebab@@.html", "ruta /@@nombreKebab@@/"),
    validar_nombre=_validar_pagina,
    existe_si=("templates/paginas/@@nombreKebab@@.html",),
    inserciones=(
        Insercion(
            "config/urls.py",
            'path("@@nombreKebab@@/", TemplateView.as_view(template_name="paginas/@@nombreKebab@@.html"), name="@@nombre@@"),',
            marcador="urls",
            descripcion="ruta /@@nombreKebab@@/",
            ubicacion="dentro de la lista urlpatterns",
        ),
        Insercion(
            "templates/base.html",
            "<a href=\"{% url '@@nombre@@' %}\">@@nombreTitulo@@</a>",
            marcador="enlaces",
            descripcion="enlace en el menú",
            ubicacion="dentro de <nav>",
            comentario="{#",
        ),
    ),
    siguiente_paso=["python manage.py runserver", "http://127.0.0.1:8000/@@nombreKebab@@/"],
)

ESTILOS = piezas_de_estilos(
    "static/css",
    lambda ruta: Insercion(
        "templates/base.html",
        f"<link rel=\"stylesheet\" href=\"{{% static 'css/{ruta}' %}}\" />",
        marcador="estilos",
        descripcion="CSS cargado en base.html",
        ubicacion="en el <head>, después de estilos.css",
        comentario="{#",
    ),
    'Usá las clases en tus plantillas: class="...".',
)

STACK = Stack(
    clave="django-web",
    titulo="Django con plantillas",
    senal="manage.py, config/settings.py y templates/base.html",
    detectar=_detectar,
    tipos=TIPOS,
    piezas={"crud": CRUD, "pagina": PAGINA, **ESTILOS},
    ejemplo_proyecto="mi-sitio",
    siguiente_paso_proyecto=[
        "cd @@carpeta@@",
        "python -m venv .venv",
        "@@activar@@",
        "pip install -r requirements.txt",
        "python manage.py migrate",
        "python manage.py createsuperuser",
        "python manage.py runserver",
        "http://127.0.0.1:8000/",
    ],
    contexto_proyecto=django._contexto_proyecto,
    contexto_env=lambda: {"secret_key": secrets.token_urlsafe(50)},
    validar_nombre=_validar_nombre,
)
