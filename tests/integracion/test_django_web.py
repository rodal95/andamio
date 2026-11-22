"""Stack django-web: sitio con plantillas (monolito), crud con vistas y página."""

import py_compile

import pytest

from andamio.cli import main
from andamio.nucleo.deteccion import buscar_proyecto

from .test_django import TODOS_LOS_TIPOS, leer, manage, requiere_django


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "django-web", "Mi Sitio"]) == 0
    raiz = en_carpeta / "mi-sitio"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_piezas(proyecto):
    assert main(["nuevo", "crud", "producto", *TODOS_LOS_TIPOS]) == 0
    assert main(["nuevo", "crud", "cliente", "nombre", "email:email", "--protegido"]) == 0
    assert main(["nuevo", "crud", "medicion", "valor:float", "fecha:date"]) == 0
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    return proyecto


def test_estructura_del_proyecto(proyecto):
    for archivo in ["manage.py", "config/settings.py", "config/urls.py", "config/views.py", "templates/base.html",
                    "templates/registration/login.html", "static/css/estilos.css", ".env", ".gitignore"]:  # fmt: skip
        assert (proyecto / archivo).is_file(), archivo
    settings = leer(proyecto / "config/settings.py")
    assert "rest_framework" not in settings and 'BASE_DIR / "templates"' in settings
    assert 'LOGIN_URL = "login"' in settings


def test_se_detecta_antes_que_django_rest(proyecto):
    assert buscar_proyecto(proyecto / "templates")[0].clave == "django-web"


def test_crud_genera_la_app_y_la_registra(con_piezas):
    raiz = con_piezas
    app = raiz / "productos"
    for archivo in ["models.py", "forms.py", "views.py", "urls.py", "admin.py", "tests.py",
                    "templates/productos/producto_lista.html", "templates/productos/producto_detalle.html",
                    "templates/productos/producto_form.html", "templates/productos/producto_confirmar_eliminar.html"]:  # fmt: skip
        assert (app / archivo).is_file(), archivo
    # El menú está en una plantilla parcial (la incluye base.html).
    urls, base = leer(raiz / "config/urls.py"), leer(raiz / "templates/partials/navbar.html")
    assert 'path("productos/", include("productos.urls")),' in urls
    assert 'path("contacto/", TemplateView.as_view(template_name="paginas/contacto.html"), name="contacto"),' in urls
    assert "<a href=\"{% url 'productos:lista' %}\">Productos</a>" in base
    assert "<a href=\"{% url 'contacto' %}\">Contacto</a>" in base
    formulario = leer(app / "forms.py")
    assert '"vence": forms.DateInput(attrs={"type": "date"}' in formulario
    lista = leer(app / "templates/productos/producto_lista.html")
    assert '{{ producto.activo|yesno:"Sí,No" }}' in lista and "<th>Descripcion</th>" not in lista
    vistas = leer(app / "views.py")
    assert "LoginRequiredMixin" not in vistas and 'success_message = "Se agregó «%(nombre)s»."' in vistas
    assert "class ClienteCrearView(LoginRequiredMixin, " in leer(raiz / "clientes/views.py")
    # Sin campos de texto: busca por número de registro.
    assert "Q(pk=int(texto))" in leer(raiz / "mediciones/views.py")
    for archivo in raiz.rglob("*.py"):
        py_compile.compile(str(archivo), doraise=True)


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        (["pagina", "admin"], "ya la usa el proyecto"),
        (["crud", "cuenta", "nombre"], "rutas de login"),
        (["crud", "producto", "objects"], "Django usa"),
    ],
)
def test_nombres_que_no_se_pueden_usar(proyecto, capsys, argumentos, esperado):
    assert main(["nuevo", *argumentos]) == 1
    assert esperado in capsys.readouterr().err


def test_pagina_repetida(proyecto, capsys):
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "pagina", "contacto"]) == 1


@pytest.mark.django
@requiere_django
def test_check_migraciones_y_tests_generados(con_piezas):
    for argumentos in (["check"], ["makemigrations"], ["test", "-v", "2"]):
        resultado = manage(con_piezas, *argumentos)
        assert resultado.returncode == 0, f"manage.py {' '.join(argumentos)}\n{resultado.stdout}\n{resultado.stderr}"
        if argumentos[0] == "test":
            # 6 por crud, más el de "sin login" del protegido.
            assert "Ran 19 tests" in resultado.stderr


@pytest.mark.django
@requiere_django
def test_las_paginas_se_ven(con_piezas):
    """Arma las páginas de verdad (plantillas, menú, login) con el cliente de pruebas de Django."""
    assert manage(con_piezas, "makemigrations").returncode == 0
    codigo = (
        "import django, os\n"
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')\n"
        "django.setup()\n"
        "from django.test.utils import setup_test_environment\n"
        "from django.test.runner import DiscoverRunner\n"
        "setup_test_environment()\n"
        "r = DiscoverRunner(verbosity=0); viejo = r.setup_databases()\n"
        "from django.test import Client\n"
        "c = Client()\n"
        "for url in ['/', '/productos/', '/productos/nuevo/', '/contacto/', '/cuentas/login/', '/cuentas/registro/', '/clientes/']:\n"
        "    respuesta = c.get(url)\n"
        "    assert respuesta.status_code == 200, (url, respuesta.status_code)\n"
        "    assert b'Contacto</a>' in respuesta.content, url\n"
        "assert c.get('/clientes/nuevo/').status_code == 302\n"
        "print('ok')\n"
    )
    import subprocess
    import sys

    resultado = subprocess.run([sys.executable, "-c", codigo], cwd=con_piezas, capture_output=True, text=True, encoding="utf-8")
    assert resultado.returncode == 0 and "ok" in resultado.stdout, resultado.stderr


# --- Menú y pie como plantillas parciales; páginas protegidas; login obligatorio ----------


def test_menu_y_pie_como_plantillas_parciales(en_carpeta, monkeypatch):
    assert main(["crear", "django-web", "sitio"]) == 0
    raiz = en_carpeta / "sitio"
    base = leer(raiz / "templates/base.html")
    assert '{% include "partials/navbar.html" %}' in base and '{% include "partials/footer.html" %}' in base
    assert "andamio:enlaces" in leer(raiz / "templates/partials/navbar.html")
    assert '<footer class="pie">' in leer(raiz / "templates/partials/footer.html")


def test_pagina_protegida(en_carpeta, monkeypatch):
    assert main(["crear", "django-web", "sitio"]) == 0
    raiz = en_carpeta / "sitio"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    urls = leer(raiz / "config/urls.py")
    assert "from django.contrib.auth.decorators import login_required" in urls
    assert 'path("perfil/", login_required(TemplateView.as_view(template_name="paginas/perfil.html")), name="perfil"),' in urls
    navbar = leer(raiz / "templates/partials/navbar.html")
    assert "{% if user.is_authenticated %}<a href=\"{% url 'perfil' %}\">Perfil</a>{% endif %}" in navbar


def test_login_obligatorio(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "django-web", "sitio"]) == 0
    raiz = en_carpeta / "sitio"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "login"]) == 1
    assert "ya viene con el proyecto" in capsys.readouterr().err
    assert main(["nuevo", "crud", "nota", "texto"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "login", "--obligatorio"]) == 0
    assert "notas/tests.py entra sin usuario" in capsys.readouterr().out
    assert 'MIDDLEWARE += ["django.contrib.auth.middleware.LoginRequiredMiddleware"]' in leer(raiz / "config/settings.py")
    assert "@login_not_required" in leer(raiz / "config/views.py")  # el registro sigue abierto
    # Un crud nuevo entra a sus tests con un usuario (y la lista también pide ingresar).
    assert main(["nuevo", "crud", "producto", "nombre"]) == 0
    tests = leer(raiz / "productos/tests.py")
    assert "self.client.force_login(self.usuario)" in tests
    assert 'self.assertRedirects(self.client.get(URL), f"/cuentas/login/?next={URL}")' in tests


def test_proyecto_anterior_con_el_menu_en_base(en_carpeta, monkeypatch):
    """Los proyectos creados antes (el menú dentro de base.html) siguen funcionando."""
    assert main(["crear", "django-web", "sitio"]) == 0
    raiz = en_carpeta / "sitio"
    monkeypatch.chdir(raiz)
    navbar = leer(raiz / "templates/partials/navbar.html").replace("{# El menú", "{# Menú")
    base = leer(raiz / "templates/base.html").replace('{% include "partials/navbar.html" %}', navbar)
    (raiz / "templates/base.html").write_text(base, encoding="utf-8")
    (raiz / "templates/partials/navbar.html").unlink()
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    assert "<a href=\"{% url 'contacto' %}\">Contacto</a>" in leer(raiz / "templates/base.html")
