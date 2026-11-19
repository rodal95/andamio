"""Comandos de punta a punta con un stack de prueba (sin depender de las plantillas reales)."""

from andamio import __version__
from andamio.cli import main


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def test_version(capsys):
    assert main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_comando_desconocido_en_espanol(capsys):
    assert main(["volar"]) == 2
    salida = capsys.readouterr().err
    assert "opción inválida" in salida
    assert "--help" in salida


def test_ayuda_en_espanol(capsys):
    assert main(["--help"]) == 0
    salida = capsys.readouterr().out
    assert "uso:" in salida and "muestra esta ayuda" in salida


def test_crear_proyecto(stack_prueba, en_carpeta, capsys):
    assert main(["crear", "prueba", "Mi Tienda"]) == 0
    proyecto = en_carpeta / "mi-tienda"
    assert leer(proyecto / "main.txt").startswith("Proyecto Mi tienda")
    assert leer(proyecto / ".env.example") == "CLAVE=cambiar\n"
    assert leer(proyecto / ".env") == "CLAVE=secreta\n"
    assert (proyecto / ".gitignore").is_file()
    salida = capsys.readouterr().out
    assert "cd mi-tienda" in salida


def test_crear_tipo_desconocido(stack_prueba, en_carpeta, capsys):
    assert main(["crear", "cobol", "x"]) == 1
    assert "Tipos disponibles: prueba" in capsys.readouterr().err


def test_crear_en_carpeta_no_vacia(stack_prueba, en_carpeta, capsys):
    (en_carpeta / "mi-tienda").mkdir()
    (en_carpeta / "mi-tienda" / "algo.txt").touch()
    assert main(["crear", "prueba", "mi-tienda"]) == 1
    assert "no está vacía" in capsys.readouterr().err


def test_crear_simulado_no_escribe(stack_prueba, en_carpeta, capsys):
    assert main(["crear", "prueba", "x", "--simular"]) == 0
    assert not (en_carpeta / "x").exists()
    assert "Simulación" in capsys.readouterr().out


def _proyecto(en_carpeta, monkeypatch):
    main(["crear", "prueba", "tienda"])
    raiz = en_carpeta / "tienda"
    monkeypatch.chdir(raiz)
    return raiz


def test_nuevo_genera_inserta_y_muestra_siguiente_paso(stack_prueba, en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    capsys.readouterr()
    assert main(["nuevo", "cosa", "Línea Venta", "cantidad:int", "detalle"]) == 0
    assert leer(raiz / "cosas/linea_venta.txt") == "Clase LineaVenta\n    cantidad: int\n    detalle: str\nFin\n"
    assert leer(raiz / "comun.txt") == "compartido\n"
    assert not (raiz / "LEEME.md").exists()
    assert "    item linea_venta (lineas_venta)\n    # --- andamio:items" in leer(raiz / "main.txt")
    assert leer(raiz / "lista.txt") == "linea_venta\n"
    salida = capsys.readouterr().out
    assert "Se usará: LineaVenta / linea_venta  (plural: lineas_venta)" in salida
    assert "usar linea_venta" in salida


def test_nuevo_desde_subcarpeta(stack_prueba, en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch)
    (raiz / "sub").mkdir()
    monkeypatch.chdir(raiz / "sub")
    assert main(["nuevo", "cosa", "producto", "nombre"]) == 0
    assert (raiz / "cosas/producto.txt").exists()


def test_nuevo_dos_veces_cancela_sin_escribir(stack_prueba, en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    main(["nuevo", "cosa", "producto", "nombre"])
    antes = leer(raiz / "main.txt")
    capsys.readouterr()
    assert main(["nuevo", "cosa", "producto", "nombre"]) == 1
    assert "ya existen" in capsys.readouterr().err
    assert leer(raiz / "main.txt") == antes


def test_nuevo_con_marcador_borrado(stack_prueba, en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    (raiz / "main.txt").write_text("Proyecto\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "cosa", "producto", "nombre"]) == 0
    assert (raiz / "cosas/producto.txt").exists()
    assert leer(raiz / "main.txt") == "Proyecto\n"
    salida = capsys.readouterr().out
    assert "pegá estas líneas" in salida
    assert "item producto (productos)" in salida


def test_nuevo_simulado(stack_prueba, en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    capsys.readouterr()
    assert main(["nuevo", "cosa", "producto", "nombre", "--simular"]) == 0
    assert not (raiz / "cosas").exists()
    salida = capsys.readouterr().out
    assert "+ " in salida and "producto.txt" in salida
    assert "~ main.txt" in salida


def test_nuevo_fuera_de_un_proyecto(stack_prueba, en_carpeta, capsys):
    assert main(["nuevo", "cosa", "producto"]) == 1
    error = capsys.readouterr().err
    assert "No encontré un proyecto" in error
    assert "andamio crear" in error


def test_nuevo_errores_esperables(stack_prueba, en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch)
    casos = [
        (["nuevo", "volador", "x"], "Piezas disponibles: cosa"),
        (["nuevo", "cosa", "producto"], "al menos un campo"),
        (["nuevo", "cosa", "producto", "precio:decimal"], "Tipos válidos: str, int"),
        (["nuevo", "cosa", "productos", "a"], "parece estar en plural"),
        (["nuevo", "cosa", "class", "a"], "reservada"),
        (["nuevo", "cosa", "producto", "id"], "automáticamente"),
        (["nuevo", "cosa", "producto", "a", "--migrar"], "no acepta la opción --migrar"),
    ]
    for argumentos, esperado in casos:
        capsys.readouterr()
        assert main(argumentos) == 1, argumentos
        assert esperado in capsys.readouterr().err, argumentos


def test_plural_explicito(stack_prueba, en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch)
    assert main(["nuevo", "cosa", "país", "nombre", "--plural", "países"]) == 0
    assert "item pais (paises)" in leer(raiz / "main.txt")


def test_info(stack_prueba, en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch)
    capsys.readouterr()
    assert main(["info"]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto Prueba" in salida
    assert "andamio nuevo cosa producto nombre:str" in salida
    assert "número entero" in salida


def test_plantillas_personalizadas(stack_prueba, en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    propia = raiz / ".andamio/plantillas/prueba/cosa/cosas"
    propia.mkdir(parents=True)
    (propia / "@@nombre@@.txt").write_text("MI VERSION @@Nombre@@\n", encoding="utf-8")
    assert main(["nuevo", "cosa", "producto", "nombre"]) == 0
    assert leer(raiz / "cosas/producto.txt") == "MI VERSION Producto\n"
    assert "tus plantillas" in capsys.readouterr().out


def test_plantilla_personalizada_con_error_de_tipeo(stack_prueba, en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch)
    propia = raiz / ".andamio/plantillas/prueba/cosa"
    propia.mkdir(parents=True)
    (propia / "x.txt").write_text("@@Nombr@@\n", encoding="utf-8")
    assert main(["nuevo", "cosa", "producto", "nombre"]) == 1
    error = capsys.readouterr().err
    assert "@@Nombr@@" in error and "@@Nombre@@" in error
    assert not (raiz / "x.txt").exists()


def test_error_inesperado_no_oculta_el_detalle(stack_prueba, en_carpeta, monkeypatch, capsys):
    import andamio.acciones

    def explota(*args, **kwargs):
        raise ZeroDivisionError("bug")

    monkeypatch.setattr(andamio.acciones, "info", explota)
    _proyecto(en_carpeta, monkeypatch)
    assert main(["info"]) == 1
    error = capsys.readouterr().err
    assert "error de andamio" in error
    assert "ZeroDivisionError" in error
