"""python -m andamio configurar (sin tocar el PATH real: el registro se simula)."""

import os
import sys
from pathlib import Path

import pytest

from andamio import configurar as modulo
from andamio.cli import main
from andamio.nucleo import consola


@pytest.fixture
def registro(tmp_path, monkeypatch):
    """Simula la instalación de andamio y el PATH del usuario en el registro de Windows."""
    carpeta = tmp_path / "Python312" / "Scripts"
    carpeta.mkdir(parents=True)
    estado = {"valor": r"C:\Windows\system32;%USERPROFILE%\bin", "tipo": 2, "escrituras": []}
    monkeypatch.setattr(modulo, "carpeta_de_andamio", lambda: carpeta)
    monkeypatch.setattr(modulo, "leer_path_usuario", lambda: (estado["valor"], estado["tipo"]))

    def escribir(valor, tipo):
        estado["escrituras"].append((valor, tipo))
        estado["valor"] = valor

    monkeypatch.setattr(modulo, "escribir_path_usuario", escribir)
    estado["carpeta"] = carpeta
    return estado


def test_agrega_la_carpeta_al_path_del_usuario(registro, capsys):
    assert modulo.configurar(windows=True) == 0
    assert len(registro["escrituras"]) == 1
    valor, tipo = registro["escrituras"][0]
    assert valor.endswith(os.pathsep + str(registro["carpeta"]))
    assert valor.startswith(r"C:\Windows\system32;%USERPROFILE%\bin")
    assert tipo == 2  # se conserva el tipo del valor (REG_EXPAND_SZ)
    salida = capsys.readouterr().out
    assert "no hizo falta ser administrador" in salida
    assert "abrí una nueva" in salida


def test_no_lo_agrega_dos_veces(registro, capsys):
    modulo.configurar(windows=True)
    capsys.readouterr()
    assert modulo.configurar(windows=True) == 0
    assert len(registro["escrituras"]) == 1
    assert "Ya está configurado" in capsys.readouterr().out


def test_simular_no_escribe(registro, capsys):
    assert modulo.configurar(simular=True, windows=True) == 0
    assert registro["escrituras"] == []
    assert "Simulación" in capsys.readouterr().out


def test_error_al_escribir(registro, monkeypatch):
    def falla(valor, tipo):
        raise PermissionError(13, "Acceso denegado")

    monkeypatch.setattr(modulo, "escribir_path_usuario", falla)
    with pytest.raises(modulo.AndamioError) as e:
        modulo.configurar(windows=True)
    assert "python -m andamio" in e.value.sugerencia


def test_linux_y_mac_solo_explican(registro, monkeypatch, capsys):
    monkeypatch.setenv("PATH", "/usr/bin")
    assert modulo.configurar(windows=False) == 0
    assert registro["escrituras"] == []
    assert f'export PATH="$PATH:{registro["carpeta"]}"' in capsys.readouterr().out


def test_sin_instalar(monkeypatch):
    monkeypatch.setattr(modulo, "carpeta_de_andamio", lambda: None)
    with pytest.raises(modulo.AndamioError, match="sin instalar"):
        modulo.configurar(windows=True)


def test_desde_la_linea_de_comandos(registro, monkeypatch, capsys):
    monkeypatch.setattr(modulo, "es_windows", lambda: True)
    assert main(["configurar", "--simular"]) == 0
    assert "Simulación" in capsys.readouterr().out


def test_esta_en_path_ignora_mayusculas_y_barras(tmp_path):
    carpeta = tmp_path / "Scripts"
    assert modulo.esta_en_path(carpeta, os.pathsep.join(["/otra", str(carpeta) + os.sep]))
    assert not modulo.esta_en_path(carpeta, "/otra")
    assert modulo.agregar_a_path("", carpeta) == str(carpeta)
    assert modulo.agregar_a_path("a" + os.pathsep, carpeta) == "a" + os.pathsep + str(carpeta)


def test_encuentra_la_carpeta_en_el_registro_de_la_instalacion(tmp_path, monkeypatch):
    scripts = tmp_path / "Scripts"
    scripts.mkdir()
    (scripts / "andamio.exe").touch()

    class Distribucion:
        files = [Path("andamio/__init__.py"), Path("../../Scripts/andamio.exe")]

        def locate_file(self, archivo):
            return tmp_path / "Lib" / "site-packages" / archivo

    (tmp_path / "Lib" / "site-packages").mkdir(parents=True)
    monkeypatch.setattr(modulo.metadata, "distribution", lambda nombre: Distribucion())
    assert modulo.carpeta_de_andamio() == scripts.resolve()


def test_los_mensajes_muestran_como_se_ejecuta(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["/home/x/andamio.pyz"])
    assert consola.programa() == "python andamio.pyz"
    monkeypatch.setattr(sys, "argv", ["/home/x/andamio/__main__.py"])
    assert consola.programa() == "python -m andamio"


@pytest.mark.skipif(os.name != "nt", reason="solo en Windows")
def test_lee_el_path_real_del_usuario_en_windows():
    valor, tipo = modulo.leer_path_usuario()
    assert isinstance(valor, str) and tipo in (1, 2)  # REG_SZ o REG_EXPAND_SZ


def test_encuentra_el_comando_si_andamio_esta_instalado():
    try:
        modulo.metadata.distribution("andamio")
    except modulo.metadata.PackageNotFoundError:
        pytest.skip("andamio no está instalado con pip en este entorno")
    carpeta = modulo.carpeta_de_andamio()
    assert carpeta is not None
    assert (carpeta / ("andamio.exe" if os.name == "nt" else "andamio")).is_file()
