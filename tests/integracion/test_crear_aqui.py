"""crear <tipo> . : el proyecto en la carpeta actual, sin crear otra ni tener que entrar."""

import pytest

from andamio.cli import main


@pytest.fixture
def carpeta(en_carpeta, monkeypatch):
    destino = en_carpeta / "Mi Tienda"
    destino.mkdir()
    (destino / ".git").mkdir()  # git init antes: se permite
    monkeypatch.chdir(destino)
    return destino


@pytest.mark.parametrize("tipo, archivo", [("python", "main.py"), ("django", "manage.py"), ("react", "package.json"), ("react-native", "app.json")])
def test_crea_el_proyecto_en_la_carpeta_actual(carpeta, capsys, tipo, archivo):
    assert main(["crear", tipo, "."]) == 0
    salida = capsys.readouterr().out
    assert (carpeta / archivo).is_file()
    assert not (carpeta / "mi-tienda").exists()
    assert "Se usará la carpeta actual" in salida
    assert "cd mi-tienda" not in salida  # ya estás en la carpeta
    # Las piezas se generan ahí mismo.
    pieza = {"python": ["entidad", "producto", "nombre"], "django": ["recurso", "producto", "nombre"],
             "react": ["servicio", "producto", "nombre"], "react-native": ["servicio", "producto", "nombre"]}[tipo]  # fmt: skip
    assert main(["nuevo", *pieza]) == 0


def test_el_nombre_es_el_de_la_carpeta(carpeta):
    assert main(["crear", "react", "."]) == 0
    assert '"name": "mi-tienda"' in (carpeta / "package.json").read_text(encoding="utf-8")


def test_la_carpeta_tiene_que_estar_vacia(carpeta, capsys):
    (carpeta / "notas.txt").write_text("hola", encoding="utf-8")
    assert main(["crear", "django", "."]) == 1
    assert "tiene que estar vacía, y tiene: notas.txt" in capsys.readouterr().err
    assert not (carpeta / "manage.py").exists()


def test_sin_guia_y_simular(carpeta):
    assert main(["crear", "python", ".", "--simular"]) == 0
    assert not (carpeta / "main.py").exists()
    assert main(["crear", "python", ".", "--sin-guia"]) == 0
    assert (carpeta / "andamio.json").is_file()


def test_menu_acepta_el_punto(carpeta, respuestas):
    respuestas(["1", ".", "s"])  # Python + SQLite, en esta carpeta, confirmar
    assert main([]) == 0
    assert (carpeta / "main.py").is_file()


def test_avisa_si_queda_dentro_de_otro_proyecto(en_carpeta, capsys, monkeypatch):
    assert main(["crear", "django", "api"]) == 0
    front = en_carpeta / "api" / "front"
    front.mkdir()
    monkeypatch.chdir(front)
    capsys.readouterr()
    assert main(["crear", "react", "."]) == 0
    assert "Estás dentro de un proyecto Django" in capsys.readouterr().out
