"""El historial (.andamio/historial.jsonl) y el comando mapa."""

import json

from andamio.cli import main
from andamio.nucleo import historial


def _proyecto(en_carpeta, monkeypatch, stack="django"):
    assert main(["crear", stack, "proy"]) == 0
    raiz = en_carpeta / "proy"
    monkeypatch.chdir(raiz)
    return raiz


def test_cada_nuevo_queda_en_el_historial(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch)
    assert main(["nuevo", "recurso", "producto", "nombre:str", "precio:decimal", "--protegido"]) == 0
    assert main(["nuevo", "recurso", "pais", "nombre:str", "--plural", "paises", "--simular"]) == 0
    lineas = (raiz / ".andamio/historial.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lineas) == 1  # la simulación no se anota
    datos = json.loads(lineas[0])
    assert datos["pieza"] == "recurso" and datos["nombre"] == "producto" and datos["plural"] == "productos"
    assert datos["campos"] == [{"nombre": "nombre", "tipo": "str"}, {"nombre": "precio", "tipo": "decimal"}]
    assert datos["opciones"] == {"protegido": True}
    entradas, malas = historial.leer(raiz)
    assert malas == 0 and entradas[0].resumen() == "recurso producto nombre:str precio:decimal --protegido"


def test_mapa_sin_historial(en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch)
    capsys.readouterr()
    assert main(["map"]) == 0
    assert "Todavía no hay piezas" in capsys.readouterr().out


def test_mapa_controla_archivos_y_conexiones(en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    assert main(["nuevo", "recurso", "producto", "nombre:str"]) == 0
    assert main(["nuevo", "recurso", "cliente", "nombre:str"]) == 0
    capsys.readouterr()
    assert main(["mapa"]) == 0
    salida = capsys.readouterr().out
    assert "2 piezas generadas" in salida and "revisar" not in salida
    # Se borra un archivo de un recurso y la ruta del otro.
    (raiz / "productos/admin.py").unlink()
    urls = raiz / "config/urls.py"
    urls.write_text(urls.read_text(encoding="utf-8").replace('path("api/", include("clientes.urls")),', ""), encoding="utf-8")
    capsys.readouterr()
    assert main(["mapa"]) == 0
    salida = capsys.readouterr().out
    assert "falta productos/admin.py" in salida
    assert "sin conectar: config/urls.py (rutas /api/clientes/)" in salida


def test_mapa_avisa_si_los_campos_no_coinciden(en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch, "next-fullstack")
    assert main(["nuevo", "recurso", "producto", "nombre:str", "precio:decimal"]) == 0
    assert main(["nuevo", "crud", "producto", "nombre:str", "precio:int"]) == 0
    capsys.readouterr()
    assert main(["mapa"]) == 0
    assert "'producto' tiene campos distintos según la pieza" in capsys.readouterr().out


def test_lineas_que_no_se_pueden_leer(en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    assert main(["nuevo", "recurso", "producto", "nombre:str"]) == 0
    with open(raiz / ".andamio/historial.jsonl", "a", encoding="utf-8") as archivo:
        archivo.write("esto no es JSON\n")
    capsys.readouterr()
    assert main(["mapa"]) == 0
    assert "1 línea de .andamio/historial.jsonl no se pudo leer" in capsys.readouterr().out
