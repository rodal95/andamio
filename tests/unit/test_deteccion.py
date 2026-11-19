import json

from andamio.nucleo.deteccion import buscar_proyecto, dependencias_npm, error_no_detectado
from andamio.stacks.base import Stack


def _stack(clave, detectar):
    return Stack(clave=clave, titulo=clave.title(), senal=f"señal de {clave}", detectar=detectar, tipos={}, piezas={})


A = _stack("a", lambda r: (r / "a.txt").is_file())
B = _stack("b", lambda r: (r / "b.txt").is_file())


def test_detecta_en_la_carpeta_actual(tmp_path):
    (tmp_path / "a.txt").touch()
    assert buscar_proyecto(tmp_path, [A, B]) == (A, tmp_path)


def test_sube_desde_una_subcarpeta(tmp_path):
    (tmp_path / "b.txt").touch()
    profunda = tmp_path / "x" / "y" / "z"
    profunda.mkdir(parents=True)
    assert buscar_proyecto(profunda, [A, B]) == (B, tmp_path)


def test_gana_la_carpeta_mas_cercana(tmp_path):
    (tmp_path / "a.txt").touch()
    interna = tmp_path / "frontend"
    interna.mkdir()
    (interna / "b.txt").touch()
    assert buscar_proyecto(interna, [A, B]) == (B, interna)


def test_en_la_misma_carpeta_gana_el_orden_del_registro(tmp_path):
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.txt").touch()
    assert buscar_proyecto(tmp_path, [B, A])[0] is B


def test_sin_proyecto(tmp_path):
    assert buscar_proyecto(tmp_path, [A, B]) is None
    error = error_no_detectado(tmp_path, [A, B])
    assert "señal de a" in error.mensaje
    assert "andamio crear" in error.sugerencia


def test_dependencias_npm(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"react": "1"}, "devDependencies": {"vite": "1"}}), encoding="utf-8"
    )
    assert dependencias_npm(tmp_path) == {"react", "vite"}


def test_package_json_roto_no_rompe(tmp_path):
    (tmp_path / "package.json").write_text("{ esto no es json", encoding="utf-8")
    assert dependencias_npm(tmp_path) == set()
