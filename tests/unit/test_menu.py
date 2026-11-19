"""Menú interactivo con respuestas simuladas."""

from andamio.cli import main


def test_menu_crea_un_proyecto(stack_prueba, en_carpeta, respuestas, capsys):
    respuestas(["1", "Mi Tienda", "s"])
    assert main([]) == 0
    assert (en_carpeta / "mi-tienda" / "main.txt").exists()
    salida = capsys.readouterr().out
    assert "¿Qué proyecto querés crear?" in salida
    assert "cd mi-tienda" in salida


def test_menu_valida_y_vuelve_a_preguntar(stack_prueba, en_carpeta, respuestas, capsys):
    respuestas(["7", "1", "mi tienda!", "mi tienda", "s"])
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "Escribí un número del 1 al 2" in salida
    assert "caracteres que no se pueden usar" in salida
    assert (en_carpeta / "mi-tienda").is_dir()


def test_menu_cancelar_no_escribe(stack_prueba, en_carpeta, respuestas, capsys):
    respuestas(["1", "x", "n"])
    assert main([]) == 130
    assert not (en_carpeta / "x").exists()
    assert "No se creó ni modificó ningún archivo" in capsys.readouterr().out


def test_menu_genera_una_pieza(stack_prueba, en_carpeta, monkeypatch, respuestas, capsys):
    main(["crear", "prueba", "tienda"])
    raiz = en_carpeta / "tienda"
    monkeypatch.chdir(raiz)
    preguntas = respuestas(
        [
            "1",  # pieza: cosa
            "productos",  # parece plural
            "n",  # no usarlo
            "línea venta",
            "n",  # el plural no está bien
            "líneas de venta",
            "precio",
            "2",  # tipo int
            "precio",  # repetido
            "class",  # reservado
            "nota:str",  # nombre y tipo juntos
            "",  # terminar
            "s",  # confirmar
        ]
    )
    capsys.readouterr()
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto Prueba detectado" in salida
    assert "parece estar en plural" in salida
    assert any("El plural será 'lineas_venta'" in p for p in preguntas)
    assert "ya está en la lista" in salida
    assert "reservada" in salida
    assert "Se van a crear" in salida
    contenido = (raiz / "cosas/linea_venta.txt").read_text(encoding="utf-8")
    assert contenido == "Clase LineaVenta\n    precio: int\n    nota: str\nFin\n"
    assert "item linea_venta (lineas_de_venta)" in (raiz / "main.txt").read_text(encoding="utf-8")
    assert any("Enter para terminar" in p for p in preguntas)


def test_menu_salir(stack_prueba, en_carpeta, respuestas):
    respuestas(["2"])
    assert main([]) == 0
    assert list(en_carpeta.iterdir()) == []


def test_menu_ctrl_d(stack_prueba, en_carpeta, respuestas, capsys):
    respuestas([])
    assert main([]) == 130
    assert "Cancelado" in capsys.readouterr().out
