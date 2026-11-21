"""andamio-guia.html: la página dentro del proyecto para guiarse."""

from andamio.cli import main


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def test_crear_la_arma_y_la_ignora_en_git(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "react", "mi-web"]) == 0
    raiz = en_carpeta / "mi-web"
    guia = leer(raiz / "andamio-guia.html")
    assert "abrí en el navegador andamio-guia.html" in capsys.readouterr().out.replace("\x1b[1m", "").replace("\x1b[0m", "")
    for esperado in ("<h1>mi-web</h1>", "Proyecto React + Vite (TypeScript)", "npm run dev", "Todavía no generaste piezas", "nuevo pagina Contacto", "https://rodal95.github.io/andamio/react.html"):
        assert esperado in guia, esperado
    assert "andamio-guia.html" in leer(raiz / ".gitignore")


def test_nuevo_la_actualiza_con_lo_generado_y_la_logica(en_carpeta, monkeypatch):
    assert main(["crear", "django", "api"]) == 0
    raiz = en_carpeta / "api"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "recurso", "producto", "nombre:str", "precio:decimal"]) == 0
    guia = leer(raiz / "andamio-guia.html")
    assert "nuevo recurso producto nombre:str precio:decimal" in guia
    assert '<a href="productos/models.py">productos/models.py</a>' in guia
    assert "productos/serializers.py" in guia and "validaciones propias" in guia  # TODO(logica)
    assert "config/settings.py" in guia  # dónde se conecta (LOCAL_APPS)
    # pendientes no cuenta las marcas que nombra la guía.
    assert main(["pendientes"]) == 0


def test_simular_no_la_escribe(en_carpeta, monkeypatch):
    assert main(["crear", "python", "kiosco"]) == 0
    raiz = en_carpeta / "kiosco"
    monkeypatch.chdir(raiz)
    antes = leer(raiz / "andamio-guia.html")
    assert main(["nuevo", "entidad", "producto", "nombre", "--simular"]) == 0
    assert leer(raiz / "andamio-guia.html") == antes


def test_proyecto_viejo_sin_guia_no_la_crea_hasta_init(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "python", "kiosco"]) == 0
    raiz = en_carpeta / "kiosco"
    (raiz / "andamio-guia.html").unlink()
    gitignore = leer(raiz / ".gitignore").replace("andamio-guia.html", "")
    (raiz / ".gitignore").write_text(gitignore, encoding="utf-8")
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "entidad", "producto", "nombre"]) == 0
    assert not (raiz / "andamio-guia.html").exists()
    assert main(["init"]) == 0
    assert "nuevo entidad producto nombre:str" in leer(raiz / "andamio-guia.html")
    assert "andamio-guia.html" in leer(raiz / ".gitignore")
