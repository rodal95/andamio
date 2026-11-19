"""Piezas de estilos: tema, ui y estilo (web, django-web, vue, react, next) y el tema de React Native y Reflex."""

import pytest

from andamio.cli import main
from andamio.estilos import PALETA, PARTES, css_tema

from .node import NPM, ejecutar, npm_install, requiere_node

# stack -> (carpeta de los CSS, archivo que los carga, cómo se carga uno: {ruta} es la ruta dentro de la carpeta)
STACKS = {
    "web": ("css", "css/estilos.css", '@import url("{ruta}");'),
    "django-web": ("static/css", "templates/base.html", "<link rel=\"stylesheet\" href=\"{{% static 'css/{ruta}' %}}\" />"),
    "vue": ("src", "src/main.js", "import './{ruta}';"),
    "react": ("src", "src/main.tsx", "import './{ruta}';"),
    "next": ("app", "app/layout.tsx", "import './{ruta}';"),
    "next-fullstack": ("app", "app/layout.tsx", "import './{ruta}';"),
}


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def crear(en_carpeta, monkeypatch):
    def hacer(clave, *opciones):
        assert main(["crear", clave, "proyecto", *opciones]) == 0
        raiz = en_carpeta / "proyecto"
        monkeypatch.chdir(raiz)
        return raiz

    return hacer


@pytest.mark.parametrize("clave", STACKS)
def test_tema_ui_y_estilo(clave, crear):
    raiz = crear(clave)
    carpeta, cargador, linea = STACKS[clave]
    assert main(["nuevo", "tema", "verde", "--modo", "oscuro"]) == 0
    assert main(["nuevo", "ui", "tarjetas"]) == 0
    assert main(["new", "ui", "modal"]) == 0
    assert main(["nuevo", "estilo", "Perfil Usuario"]) == 0
    tema = leer(raiz / carpeta / "tema.css")
    assert f"--acento: {PALETA['verde'][1]};" in tema.split(":root:root[data-tema")[0]  # oscuro de entrada
    assert "@media (prefers-color-scheme: dark)" not in tema
    assert ".tarjetas {" in leer(raiz / carpeta / "ui/tarjetas.css")
    estilo = leer(raiz / carpeta / "estilos/perfil-usuario.css")
    assert ".perfil-usuario {" in estilo and "var(--acento" in estilo
    archivo = leer(raiz / cargador)
    for ruta in ("tema.css", "ui/tarjetas.css", "ui/modal.css", "estilos/perfil-usuario.css"):
        assert linea.format(ruta=ruta) in archivo, ruta


def test_todas_las_partes_y_los_colores(crear):
    raiz = crear("web")
    for parte in PARTES:
        assert main(["nuevo", "ui", parte]) == 0, parte
        assert (raiz / "css/ui" / f"{parte}.css").read_text(encoding="utf-8").startswith("/*")
    for color in PALETA:
        for modo in ("auto", "claro", "oscuro"):
            css = css_tema(color, modo)
            assert css.count("{") == css.count("}"), (color, modo)
    assert "prefers-color-scheme: dark" in css_tema("azul", "auto")


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        (["tema", "fucsia"], "Colores: azul"),
        (["tema", "azul", "--modo", "noche"], "Modos: auto"),
        (["ui", "carrusel"], "nuevo estilo <nombre>"),
        (["estilo", "tarjetas"], "nuevo ui tarjetas"),
        (["recurso", "producto", "nombre", "--modo", "oscuro"], None),
    ],
)
def test_errores(argumentos, esperado, crear, capsys):
    crear("web")
    capsys.readouterr()
    assert main(["nuevo", *argumentos]) != 0
    if esperado:
        assert esperado in capsys.readouterr().err


def test_tema_sin_nombre_es_azul_y_no_se_pisa(crear, capsys):
    raiz = crear("vue")
    assert main(["nuevo", "tema"]) == 0
    assert f"--acento: {PALETA['azul'][0]};" in leer(raiz / "src/tema.css")
    capsys.readouterr()
    assert main(["nuevo", "tema", "rojo"]) == 1  # andamio nunca sobrescribe: hay que borrar el tema


def test_tema_react_native(crear):
    raiz = crear("react-native")
    assert main(["nuevo", "tema", "violeta", "--mode", "claro"]) == 0
    tema = leer(raiz / "constants/tema.ts")
    assert "const MODO = 'claro' as 'auto' | 'claro' | 'oscuro';" in tema
    assert f"acento: '{PALETA['violeta'][0]}'," in tema and "export function useTema()" in tema


def test_tema_reflex(crear):
    raiz = crear("reflex")
    app = raiz / "proyecto"
    assert main(["nuevo", "tema", "turquesa"]) == 0
    assert 'accent_color="teal"' in leer(app / "tema.py") and 'appearance="inherit"' in leer(app / "tema.py")
    principal = leer(app / "proyecto.py")
    assert "from proyecto.tema import TEMA" in principal and "app.theme = TEMA" in principal


@pytest.mark.lento
@requiere_node
@pytest.mark.parametrize("clave", ["react", "vue", "next"])
def test_compila_con_tema_y_todas_las_partes(clave, crear):
    raiz = crear(clave)
    assert main(["nuevo", "tema", "violeta"]) == 0
    for parte in PARTES:
        assert main(["nuevo", "ui", parte]) == 0
    assert main(["nuevo", "estilo", "catalogo"]) == 0
    npm_install(raiz)
    ejecutar([NPM, "run", "build"], raiz, env={"NEXT_TELEMETRY_DISABLED": "1"})


def test_tema_desde_el_menu(crear, respuestas):
    raiz = crear("web")
    # 5: tema (después de pagina, componente, servicio y crud), el color, el modo (3: oscuro) y confirmar.
    preguntas = respuestas(["5", "rosa", "3", "s"])
    assert main([]) == 0
    assert any(p.startswith("Color (azul") for p in preguntas)
    tema = leer(raiz / "css/tema.css")
    assert f"--acento: {PALETA['rosa'][1]};" in tema.split(":root:root[data-tema")[0]


def test_tema_desde_el_menu_con_enter_es_azul(crear, respuestas):
    raiz = crear("web")
    respuestas(["5", "", "1", "s"])
    assert main([]) == 0
    assert f"--acento: {PALETA['azul'][0]};" in leer(raiz / "css/tema.css")
