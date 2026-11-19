"""Stack python: crear el proyecto, generar entidades y ejecutar el código generado."""

import os
import py_compile
import subprocess
import sys
import textwrap

import pytest

from andamio.cli import main


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "python", "Mi Tienda"]) == 0
    raiz = en_carpeta / "mi-tienda"
    monkeypatch.chdir(raiz)
    return raiz


def ejecutar_python(raiz, codigo, entrada=None):
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(codigo)],
        cwd=raiz,
        input=entrada,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def test_estructura_del_proyecto(proyecto):
    for archivo in ["main.py", "db.py", "sql/schema.sql", "entidades/__init__.py", "menus/entrada.py", ".gitignore", "README.md"]:
        assert (proyecto / archivo).is_file(), archivo
    assert "Mi tienda" in leer(proyecto / "main.py")


def test_dos_entidades_y_crud_contra_una_base_temporal(proyecto, tmp_path):
    assert main(["nuevo", "entidad", "producto", "nombre:str", "precio:float", "stock:int"]) == 0
    assert main(["nuevo", "entidad", "cliente", "nombre", "email:str"]) == 0

    for archivo in proyecto.rglob("*.py"):
        py_compile.compile(str(archivo), doraise=True)

    base = tmp_path / "prueba.db"
    resultado = ejecutar_python(
        proyecto,
        f"""
        import db
        db.RUTA_DB = {str(base)!r}
        db.inicializar()
        from entidades import producto, cliente

        id1 = producto.crear("Yerba", 1500.5, 10)
        id2 = producto.crear("Mate", 3000.0, 2)
        assert [p["nombre"] for p in producto.listar()] == ["Yerba", "Mate"]
        assert producto.obtener(id1) == {{"id": id1, "nombre": "Yerba", "precio": 1500.5, "stock": 10}}
        assert producto.actualizar(id1, "Yerba suave", 1600.0, 8) is True
        assert producto.obtener(id1)["nombre"] == "Yerba suave"
        assert producto.eliminar(id2) is True
        assert producto.eliminar(id2) is False
        assert producto.obtener(id2) is None
        assert producto.actualizar(999, "x", 1.0, 1) is False

        cliente.crear("Ana", "ana@ejemplo.com")
        assert cliente.listar()[0]["email"] == "ana@ejemplo.com"

        # Inyección SQL: el texto se guarda tal cual, no se ejecuta.
        cliente.crear("x'); DROP TABLE clientes; --", "y")
        assert len(cliente.listar()) == 2

        # db.inicializar() se puede ejecutar varias veces (CREATE TABLE IF NOT EXISTS).
        db.inicializar()
        print("ok")
        """,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == "ok"
    assert not (proyecto / "datos.db").exists()


def test_el_menu_generado_funciona(proyecto):
    main(["nuevo", "entidad", "producto", "nombre:str", "precio:float", "stock:int"])
    entrada = "\n".join(
        ["1", "2", "Yerba Mate", "1500,50", "diez", "10", "1", "3", "1", "", "1800", "", "1", "4", "1", "s", "1", "0", "0"]
    )
    resultado = subprocess.run(
        [sys.executable, "main.py"],
        cwd=proyecto,
        input=entrada + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert resultado.returncode == 0, resultado.stderr
    salida = resultado.stdout
    assert "1. Productos" in salida
    assert "Tiene que ser un número entero" in salida
    assert "Yerba Mate | 1500.5" in salida
    assert "Yerba Mate | 1800.0" in salida
    assert "Eliminado." in salida
    assert "(no hay registros)" in salida
    assert "¡Hasta luego!" in salida


def test_entidad_con_un_solo_campo(proyecto, tmp_path):
    main(["nuevo", "entidad", "categoria", "nombre"])
    assert "(nombre,)" in leer(proyecto / "entidades/categoria.py")
    resultado = ejecutar_python(
        proyecto,
        f"""
        import db
        db.RUTA_DB = {str(tmp_path / "x.db")!r}
        db.inicializar()
        from entidades import categoria
        categoria.crear("Bebidas")
        assert categoria.listar() == [{{"id": 1, "nombre": "Bebidas"}}]
        """,
    )
    assert resultado.returncode == 0, resultado.stderr


def test_nombre_compuesto_y_con_tildes(proyecto):
    assert main(["nuevo", "entidad", "Línea Venta", "cantidad:int", "precio unitario:float"]) == 0
    assert (proyecto / "entidades/linea_venta.py").is_file()
    assert "CREATE TABLE IF NOT EXISTS lineas_venta" in leer(proyecto / "sql/schema.sql")
    assert '"Lineas venta": menu_linea_venta.mostrar_menu,' in leer(proyecto / "main.py")
    assert 'precio_unitario = pedir("Precio unitario", float)' in leer(proyecto / "menus/menu_linea_venta.py")


def test_entidad_repetida_no_toca_nada(proyecto, capsys):
    main(["nuevo", "entidad", "producto", "nombre"])
    antes = {p: p.read_bytes() for p in proyecto.rglob("*") if p.is_file()}
    capsys.readouterr()
    assert main(["nuevo", "entidad", "producto", "nombre", "precio:float"]) == 1
    assert "ya existen" in capsys.readouterr().err
    despues = {p: p.read_bytes() for p in proyecto.rglob("*") if p.is_file()}
    assert antes == despues


@pytest.mark.parametrize(
    "campo, motivo",
    [
        ("producto", "mismo nombre que la entidad"),
        ("print", "función 'print'"),
        ("conexion", "variable"),
        ("pedir", "función que usa"),
        ("id", "automáticamente"),
        ("precio:decimal", "Tipos válidos: str, int, float"),
    ],
)
def test_campos_que_romperian_el_codigo(proyecto, capsys, campo, motivo):
    assert main(["nuevo", "entidad", "producto", campo]) == 1
    assert motivo in capsys.readouterr().err
    assert not (proyecto / "entidades/producto.py").exists()


def test_nombres_reservados(proyecto, capsys):
    assert main(["nuevo", "entidad", "db", "nombre"]) == 1
    assert "db.py" in capsys.readouterr().err


def test_marcadores_borrados(proyecto, capsys):
    (proyecto / "main.py").write_text("import db\nMENUS = {}\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "entidad", "producto", "nombre"]) == 0
    assert (proyecto / "entidades/producto.py").is_file()
    assert "CREATE TABLE IF NOT EXISTS productos" in leer(proyecto / "sql/schema.sql")
    assert leer(proyecto / "main.py") == "import db\nMENUS = {}\n"
    salida = capsys.readouterr().out
    assert "from menus import menu_producto" in salida
    assert '"Productos": menu_producto.mostrar_menu,' in salida
    assert "dentro del diccionario MENUS" in salida


def test_detecta_desde_una_subcarpeta(proyecto, monkeypatch, capsys):
    monkeypatch.chdir(proyecto / "entidades")
    capsys.readouterr()
    assert main(["info"]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto Python + SQLite" in salida
    assert "entidad" in salida
    assert main(["nuevo", "entidad", "producto", "nombre"]) == 0
    assert (proyecto / "entidades/producto.py").is_file()


def test_menu_interactivo_genera_una_entidad(proyecto, respuestas, capsys):
    respuestas(["1", "producto", "", "nombre", "1", "precio", "3", "", "s"])
    capsys.readouterr()
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto Python + SQLite detectado." in salida
    assert "Siguiente paso:" in salida and "python main.py" in salida
    assert 'precio = pedir("Precio", float)' in leer(proyecto / "menus/menu_producto.py")


def test_menu_interactivo_crea_el_proyecto(en_carpeta, respuestas, capsys):
    respuestas(["1", "Mi Kiosco", "s"])
    assert main([]) == 0
    assert (en_carpeta / "mi-kiosco" / "main.py").is_file()
    assert "¿Qué proyecto querés crear?" in capsys.readouterr().out
