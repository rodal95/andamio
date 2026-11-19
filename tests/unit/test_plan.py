import codecs
from pathlib import Path

import pytest

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.plan import Plan


def test_crea_archivos_y_carpetas(tmp_path):
    plan = Plan(tmp_path)
    plan.crear("a/b/c.txt", "hola ñandú")
    plan.crear_carpeta("vacia")
    plan.aplicar()
    assert (tmp_path / "a/b/c.txt").read_text(encoding="utf-8") == "hola ñandú"
    assert (tmp_path / "vacia").is_dir()


def test_escribe_utf8_y_saltos_lf(tmp_path):
    plan = Plan(tmp_path)
    plan.crear("x.py", "# línea\nprint('año')\n")
    plan.aplicar()
    assert (tmp_path / "x.py").read_bytes() == "# línea\nprint('año')\n".encode("utf-8")


def test_nunca_sobrescribe_y_no_escribe_nada(tmp_path):
    (tmp_path / "existe.txt").write_text("original", encoding="utf-8")
    plan = Plan(tmp_path)
    plan.crear("nuevo.txt", "x")
    plan.crear("existe.txt", "pisado")
    with pytest.raises(AndamioError) as e:
        plan.aplicar()
    assert "existe.txt" in e.value.mensaje
    assert not (tmp_path / "nuevo.txt").exists()
    assert (tmp_path / "existe.txt").read_text(encoding="utf-8") == "original"


def test_si_no_existe_mantiene_el_archivo(tmp_path):
    (tmp_path / "http.ts").write_text("mío", encoding="utf-8")
    plan = Plan(tmp_path)
    plan.crear("http.ts", "nuevo", si_no_existe=True)
    plan.aplicar()
    assert (tmp_path / "http.ts").read_text(encoding="utf-8") == "mío"
    assert plan.mantenidos == [tmp_path / "http.ts"]


def test_exigir_inexistente(tmp_path):
    (tmp_path / "productos").mkdir()
    plan = Plan(tmp_path)
    plan.exigir_inexistente("productos")
    with pytest.raises(AndamioError, match="productos"):
        plan.validar()


def test_insercion_con_marcador(tmp_path):
    (tmp_path / "main.py").write_text("import a\n# --- andamio:imports ---\n", encoding="utf-8")
    plan = Plan(tmp_path)
    plan.insertar("main.py", "import b", marcador="imports", descripcion="import")
    plan.insertar("main.py", "import c", marcador="imports", descripcion="import")
    plan.aplicar()
    assert (tmp_path / "main.py").read_text(encoding="utf-8") == "import a\nimport b\nimport c\n# --- andamio:imports ---\n"


def test_insercion_sin_marcador_genera_igual_e_indica_que_pegar(tmp_path, capsys):
    (tmp_path / "main.py").write_text("import a\n", encoding="utf-8")
    plan = Plan(tmp_path)
    plan.crear("nuevo.py", "x")
    plan.insertar("main.py", "import b", marcador="imports", ubicacion="junto a los otros import")
    plan.aplicar()
    assert (tmp_path / "nuevo.py").exists()
    assert (tmp_path / "main.py").read_text(encoding="utf-8") == "import a\n"
    plan.mostrar_manuales()
    salida = capsys.readouterr().out
    assert "main.py" in salida
    assert "import b" in salida
    assert "andamio:imports" in salida
    assert "junto a los otros import" in salida


def test_insercion_en_archivo_inexistente(tmp_path):
    plan = Plan(tmp_path)
    plan.insertar("index.ts", "export * from './a';", crear_si_falta=True)
    plan.insertar("main.py", "x", marcador="m")
    plan.aplicar()
    assert (tmp_path / "index.ts").read_text(encoding="utf-8") == "export * from './a';\n"
    assert plan.manuales[0].motivo == "el archivo no existe"


def test_insercion_no_duplica(tmp_path):
    (tmp_path / "index.ts").write_text("export * from './a';\n", encoding="utf-8")
    plan = Plan(tmp_path)
    plan.insertar("index.ts", "export * from './a';")
    assert not plan.modificados


def test_preserva_bom_y_crlf(tmp_path):
    original = codecs.BOM_UTF8 + "a\r\n# andamio:m\r\n".encode("utf-8")
    (tmp_path / "f.py").write_bytes(original)
    plan = Plan(tmp_path)
    plan.insertar("f.py", "b", marcador="m")
    plan.aplicar()
    assert (tmp_path / "f.py").read_bytes() == codecs.BOM_UTF8 + "a\r\nb\r\n# andamio:m\r\n".encode("utf-8")


def test_archivo_que_no_es_utf8_pide_edicion_manual(tmp_path):
    (tmp_path / "f.py").write_bytes("# año\n# andamio:m\n".encode("latin-1"))
    plan = Plan(tmp_path)
    plan.insertar("f.py", "b", marcador="m")
    assert "UTF-8" in plan.manuales[0].motivo


def test_deshace_todo_si_falla_una_escritura(tmp_path):
    (tmp_path / "main.py").write_text("# andamio:m\n", encoding="utf-8")
    (tmp_path / "bloqueo").write_text("soy un archivo, no una carpeta", encoding="utf-8")
    plan = Plan(tmp_path)
    plan.insertar("main.py", "x", marcador="m")
    plan.crear("carpeta/nueva/a.txt", "a")
    plan.crear("bloqueo/b.txt", "b")  # falla: 'bloqueo' es un archivo
    with pytest.raises(AndamioError, match="Se deshicieron"):
        plan.aplicar()
    assert not (tmp_path / "carpeta").exists()
    assert (tmp_path / "main.py").read_text(encoding="utf-8") == "# andamio:m\n"


def test_deshace_si_se_interrumpe(tmp_path, monkeypatch):
    plan = Plan(tmp_path)
    plan.crear("a/1.txt", "1")
    plan.crear("a/2.txt", "2")
    escrituras = []
    original_open = open

    def open_que_se_interrumpe(ruta, modo="r", *args, **kwargs):
        if "x" in modo:
            escrituras.append(ruta)
            if len(escrituras) == 2:
                raise KeyboardInterrupt
        return original_open(ruta, modo, *args, **kwargs)

    monkeypatch.setattr("builtins.open", open_que_se_interrumpe)
    with pytest.raises(KeyboardInterrupt):
        plan.aplicar()
    assert not (tmp_path / "a").exists()


def test_mostrar_resumen(tmp_path, capsys):
    (tmp_path / "main.py").write_text("# andamio:m\n", encoding="utf-8")
    plan = Plan(tmp_path)
    plan.crear("nuevo.py", "x")
    plan.insertar("main.py", "x", marcador="m", descripcion="import")
    plan.mostrar()
    salida = capsys.readouterr().out
    assert "+ nuevo.py" in salida
    assert "~ main.py  (import)" in salida
    assert isinstance(tmp_path, Path)
