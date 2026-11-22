"""Stack `django-web`: sitio web con Django y plantillas HTML (todo en un proyecto, "monolito").

Es la otra forma de usar Django: en lugar de una API que usa un frontend aparte, el
servidor arma las páginas HTML con plantillas. Trae login, registro y admin.
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre, kebab
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
    obligatorio = sitio_obligatorio(sol.raiz)
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
        import_usuario="from django.contrib.auth import get_user_model" if protegido or obligatorio else "",
        # Con todo el sitio protegido, los tests entran con un usuario (y la lista tampoco es libre).
        preparar_tests=_PREPARAR_TESTS_OBLIGATORIO if obligatorio else _PREPARAR_TESTS_PROTEGIDO if protegido else "",
    )
    return contexto


_PREPARAR_TESTS_OBLIGATORIO = """\
def setUp(self):
    # Todo el sitio pide ingresar (nuevo login --obligatorio): los tests entran con un usuario.
    self.usuario = get_user_model().objects.create_user("prueba", password="clave-de-prueba-123")
    self.client.force_login(self.usuario)

def test_sin_login_pide_ingresar(self):
    self.client.logout()
    self.assertRedirects(self.client.get(URL), f"/cuentas/login/?next={URL}")
"""

_MIDDLEWARE_OBLIGATORIO = "django.contrib.auth.middleware.LoginRequiredMiddleware"


def sitio_obligatorio(raiz: Path) -> bool:
    """Si todo el sitio pide ingresar (nuevo login --obligatorio)."""
    try:
        return _MIDDLEWARE_OBLIGATORIO in (raiz / "config" / "settings.py").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return False


_PREPARAR_TESTS_PROTEGIDO = """\
def setUp(self):
    # El crud está protegido (--protegido): los tests entran con un usuario.
    self.usuario = get_user_model().objects.create_user("prueba", password="clave-de-prueba-123")
    self.client.force_login(self.usuario)

def test_sin_login_pide_ingresar(self):
    self.client.logout()
    res = self.client.get(f"{URL}nuevo/")
    self.assertRedirects(res, f"/cuentas/login/?next={URL}nuevo/")
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


_RUTAS_OCUPADAS = {"admin", "cuentas", "static", "media", "inicio", "login", "logout", "registro"}


def _leer_urls(raiz: Path) -> str:
    try:
        return (raiz / "config" / "urls.py").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return ""


def _validar_ruta(raiz: Path, ruta: str, que: str, sugerencia: str) -> None:
    """Rechaza una ruta (/ruta/) que ya usa el proyecto o que ya está en config/urls.py."""
    if ruta in _RUTAS_OCUPADAS:
        raise AndamioError(f"La ruta /{ruta}/ ya la usa el proyecto.", sugerencia)
    if f'path("{ruta}/"' in _leer_urls(raiz):
        raise AndamioError(f"Ya hay {que} en /{ruta}/ (config/urls.py).", sugerencia)


def _validar_crud(raiz: Path, nombre: Nombre) -> None:
    _validar_nombre(raiz, nombre)  # primero: explica mejor por qué (ej.: /cuentas/ es del login)
    django._validar_nombre(raiz, nombre)
    # El crud ocupa /<plural>/ (ej.: una página "Productos" ya usa /productos/).
    _validar_ruta(
        raiz,
        kebab(nombre.plural_palabras),
        "una ruta",
        "Elegí otro nombre o indicá otro plural con --plural, o borrá esa ruta de config/urls.py si ya no la usás.",
    )


def _validar_pagina(raiz: Path, nombre: Nombre) -> None:
    if nombre.snake in _RUTAS_OCUPADAS:
        raise AndamioError(f"La ruta /{nombre.kebab}/ ya la usa el proyecto.", "Elegí otro nombre para la página.")
    _validar_ruta(raiz, nombre.kebab, "una página", "Elegí otro nombre, o borrá esa ruta si ya no la usás.")
    if f'name="{nombre.snake}"' in _leer_urls(raiz):
        raise AndamioError(
            f"Ya hay una ruta llamada '{nombre.snake}' en config/urls.py.", "Elegí otro nombre para la página."
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

def _enlace(texto: str, descripcion: str = "enlace en el menú", condicion=None) -> Insercion:
    """Un enlace en el menú: en templates/partials/navbar.html; en los proyectos anteriores
    (el menú dentro de base.html), en base.html."""
    return Insercion(
        "templates/partials/navbar.html",
        texto,
        marcador="enlaces",
        descripcion=descripcion,
        ubicacion="dentro de <nav>",
        comentario="{#",
        condicion=condicion,
        alternativa=Insercion(
            "templates/base.html", texto, marcador="enlaces", descripcion=descripcion, ubicacion="dentro de <nav>", comentario="{#", condicion=condicion
        ),
    )


CRUD = Pieza(
    clave="crud",
    lectura=(
        ('@@plural@@/models.py', 'el modelo: la tabla y sus campos'),
        ('@@plural@@/forms.py', 'el formulario: qué campos muestra y cómo valida'),
        ('@@plural@@/views.py', 'las vistas: lista, detalle, crear, editar y eliminar'),
        ('@@plural@@/urls.py', 'las rutas /@@pluralKebab@@/...'),
        ('@@plural@@/templates/@@plural@@/@@nombre@@_lista.html', 'el HTML de la lista'),
        ('@@plural@@/templates/@@plural@@/@@nombre@@_form.html', 'el HTML del formulario (crear y editar)'),
        ('@@plural@@/tests.py', 'los tests'),
    ),
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
        _enlace("<a href=\"{% url '@@plural@@:lista' %}\">@@titulo@@</a>"),
    ),
    siguiente_paso=_pasos_crud,
    despues=django.migrador("django, dotenv, dj_database_url"),
    confirmaciones={"migrar": "¿Ejecutar ahora las migraciones (makemigrations y migrate)?"},
)

def _protegida(sol: Solicitud) -> bool:
    return bool(sol.opciones.get("protegido"))


def _publica(sol: Solicitud) -> bool:
    return not _protegida(sol)


PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="plantilla HTML con su ruta y su enlace en el menú; con --protegido, pide ingresar",
    ejemplo="Contacto",
    formas=("templates/paginas/@@nombreKebab@@.html", "ruta /@@nombreKebab@@/"),
    opciones=frozenset({"protegido"}),
    validar_nombre=_validar_pagina,
    existe_si=("templates/paginas/@@nombreKebab@@.html",),
    inserciones=(
        Insercion(
            "config/urls.py",
            'path("@@nombreKebab@@/", TemplateView.as_view(template_name="paginas/@@nombreKebab@@.html"), name="@@nombre@@"),',
            marcador="urls",
            descripcion="ruta /@@nombreKebab@@/",
            ubicacion="dentro de la lista urlpatterns",
            condicion=_publica,
        ),
        # --protegido: login_required lleva a /cuentas/login/ (y después vuelve) si nadie ingresó.
        Insercion(
            "config/urls.py",
            "from django.contrib.auth.decorators import login_required",
            marcador="imports",
            descripcion="import de login_required",
            ubicacion="arriba, junto a los otros import",
            condicion=_protegida,
        ),
        Insercion(
            "config/urls.py",
            'path("@@nombreKebab@@/", login_required(TemplateView.as_view(template_name="paginas/@@nombreKebab@@.html")), name="@@nombre@@"),',
            marcador="urls",
            descripcion="ruta /@@nombreKebab@@/ (pide ingresar)",
            ubicacion="dentro de la lista urlpatterns",
            condicion=_protegida,
        ),
        _enlace("<a href=\"{% url '@@nombre@@' %}\">@@nombreTitulo@@</a>", condicion=_publica),
        # El enlace a una página protegida solo se ve si alguien ingresó.
        _enlace(
            "{% if user.is_authenticated %}<a href=\"{% url '@@nombre@@' %}\">@@nombreTitulo@@</a>{% endif %}",
            "enlace en el menú, solo con sesión",
            _protegida,
        ),
    ),
    siguiente_paso=["python manage.py runserver", "http://127.0.0.1:8000/@@nombreKebab@@/"],
)

# --- Login obligatorio para todo el sitio (nuevo login --obligatorio) ----------------------

_CONFIG_OBLIGATORIO = f"""
# --- Login obligatorio (lo agregó: andamio nuevo login --obligatorio) --------------
# Todo el sitio pide ingresar: sin sesión, cualquier página lleva a /cuentas/login/.
# Quedan abiertas las vistas marcadas con @login_not_required: ingresar, el registro
# (config/views.py) y el panel /admin/ (que tiene su propio login).
MIDDLEWARE += ["{_MIDDLEWARE_OBLIGATORIO}"]"""


def _contexto_login(sol: Solicitud) -> dict[str, str]:
    if not sol.opciones.get("obligatorio"):
        raise AndamioError(
            "El login ya viene con el proyecto: /cuentas/login/, /cuentas/registro/ y Salir en el menú.",
            "Para que todo el sitio pida ingresar: python -m andamio nuevo login --obligatorio. "
            "Para una sola página: nuevo pagina Perfil --protegido",
        )
    return {}


def _pasos_login(sol: Solicitud) -> list[str]:
    try:
        abierto = "login_not_required" in (sol.raiz / "config" / "views.py").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        abierto = True
    aviso = [] if abierto else [
        "# El registro (config/views.py) también pediría login: agregale @login_not_required",
        "# (from django.contrib.auth.decorators import login_not_required) arriba de def registro.",
    ]
    for tests in sorted(sol.raiz.glob("*/tests.py")):
        try:
            texto = tests.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        if "TestCase" in texto and "force_login" not in texto:
            aviso.append(
                f"# {tests.parent.name}/tests.py entra sin usuario y ahora todo pide ingresar: en su setUp, "
                "self.client.force_login(get_user_model().objects.create_user(\"prueba\", password=\"clave-de-prueba-123\"))"
            )
    return [*aviso, "python manage.py runserver", "http://127.0.0.1:8000/   (lleva a /cuentas/login/)"]


LOGIN = Pieza(
    clave="login",
    titulo="Login obligatorio",
    descripcion="el login ya viene con el proyecto; con --obligatorio, todo el sitio pide ingresar",
    ejemplo="--obligatorio",
    nombre_defecto="sesion",
    formas=("config/settings.py (LoginRequiredMiddleware)",),
    opciones=frozenset({"obligatorio"}),
    contexto=_contexto_login,
    inserciones=(Insercion("config/settings.py", _CONFIG_OBLIGATORIO, descripcion="todo el sitio pide ingresar (al final)"),),
    siguiente_paso=_pasos_login,
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
    piezas={"crud": CRUD, "pagina": PAGINA, "login": LOGIN, **ESTILOS},
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
