"""La página web: demostraciones generadas con la versión actual y archivos completos."""

import re
import sys
import tempfile
from pathlib import Path

import pytest

import andamio
from andamio import stacks

RAIZ = Path(__file__).resolve().parents[2]
SITIO = RAIZ / "sitio"
sys.path.insert(0, str(RAIZ / "scripts"))
import sitio  # noqa: E402


@pytest.fixture(scope="module")
def datos():
    return sitio.generar()


def test_una_guia_por_tecnologia_y_variante(datos):
    assert datos["version"] == andamio.__version__
    assert [t["clave"] for t in datos["tecnologias"]] == [s.clave for s in stacks.ORDEN_MENU]
    for tecnologia, stack in zip(datos["tecnologias"], stacks.ORDEN_MENU):
        assert [v["clave"] for v in tecnologia["variantes"]] == (list(stack.variantes) or [""])
        for variante in tecnologia["variantes"]:
            assert [p["clave"] for p in variante["piezas"]] == list(stack.piezas)
            for pieza in variante["piezas"]:
                assert pieza["creados"] or pieza["modificados"], pieza["clave"]
                assert "Listo." in pieza["salida"] and "Error" not in pieza["salida"]


def test_cada_archivo_generado_tiene_su_explicacion(datos):
    """Si falla: agregá el archivo a DESCRIPCIONES (o CARPETAS) en scripts/sitio.py."""
    for tecnologia in datos["tecnologias"]:
        for variante in tecnologia["variantes"]:
            for archivo in variante["archivos"] + variante["archivos_crear"]:
                assert archivo["descripcion"], f"{tecnologia['clave']}/{variante['clave']}: {archivo['ruta']}"
            for pieza in variante["piezas"]:
                for modificado in pieza["modificados"]:
                    assert modificado["que"], (pieza["clave"], modificado["ruta"])


def test_sin_rutas_temporales(datos):
    texto = str(datos)
    temporal = Path(tempfile.gettempdir()).resolve()
    assert str(temporal) not in texto and tempfile.gettempdir() not in texto
    assert "SECRET_KEY=(se genera al azar" in texto


def test_la_terminal_es_la_de_windows(datos):
    for tecnologia in datos["tecnologias"]:
        for variante in tecnologia["variantes"]:
            terminal = [variante["crear"]["salida"], *(p["salida"] for p in variante["piezas"])]
            assert not any("source .venv/bin/activate" in t for t in terminal), tecnologia["clave"]
    django = next(t for t in datos["tecnologias"] if t["clave"] == "django")
    assert ".venv\\Scripts\\activate" in django["variantes"][0]["crear"]["salida"]


def test_sesion_del_menu(datos):
    eventos = datos["menu"]
    assert any(e["tipo"] == "entrada" for e in eventos)
    salida = "".join(e["texto"] for e in eventos if e["tipo"] == "salida")
    assert "Proyecto Django REST detectado." in salida
    assert "C:\\Users\\alumno\\mi-api" in salida


def test_la_app_de_consola_generada_funciona(datos):
    salida = datos["tecnologias"][0]["ejecucion"]["salida"]
    assert "Yerba Mate" in salida and "Tiene que ser un número entero" in salida


def test_existen_las_paginas_y_las_capturas():
    for stack in stacks.REGISTRO:
        pagina = SITIO / f"{stack.clave}.html"
        assert pagina.is_file(), pagina
        assert f'data-tecnologia="{stack.clave}"' in pagina.read_text(encoding="utf-8")
    codigo = (SITIO / "tecnologia.js").read_text(encoding="utf-8")
    for imagen in re.findall(r"img/[\w.-]+\.jpg", codigo):
        assert (SITIO / imagen).is_file(), f"falta {imagen}: ejecutá python scripts/capturas_sitio.py"
    # Las capturas de una combinación tienen que ser de una combinación que existe.
    ids = {c["id"] for combinaciones in sitio.COMBINACIONES.values() for c in combinaciones}
    for bloque in re.findall(r"combinaciones: \{(.*?)\n      \},", codigo, re.S):
        for clave in re.findall(r'"([\w-]+)": \{', bloque):
            assert clave in ids, clave


def test_el_camino_de_cada_guia_tiene_todas_las_piezas(datos):
    """Si falla: agregá la pieza a CAMINO en scripts/sitio.py, en el orden en que conviene aprenderla."""
    for tecnologia, stack in zip(datos["tecnologias"], stacks.ORDEN_MENU):
        for variante in tecnologia["variantes"]:
            piezas = [l["clave"] for l in variante["camino"] if l["tipo"] == "pieza"]
            assert sorted(piezas) == sorted(stack.piezas), tecnologia["clave"]
            rutas = {a["ruta"] for a in variante["archivos"]}
            for tema in (l for l in variante["camino"] if l["tipo"] == "tema"):
                assert tema["texto"] and set(tema["archivos"]) <= rutas, (tecnologia["clave"], tema["id"])


def test_las_combinaciones_usan_piezas_de_la_guia(datos):
    for tecnologia, stack in zip(datos["tecnologias"], stacks.ORDEN_MENU):
        for variante in tecnologia["variantes"]:
            for combinacion in variante["combinaciones"]:
                assert set(combinacion["usa"]) <= set(stack.piezas), (tecnologia["clave"], combinacion["id"])
                assert combinacion["claves"] and combinacion["pasos"]
                for archivo in combinacion["archivos"]:
                    assert archivo["contenido"].strip(), archivo["ruta"]
                # Los comandos de este proyecto (sin "En la web", etc.) son piezas de este stack.
                for paso in combinacion["pasos"]:
                    if not paso["lugar"] and " nuevo " in paso["comando"]:
                        pieza = paso["comando"].split(" nuevo ")[1].split()[0]
                        assert pieza in stack.piezas, (tecnologia["clave"], paso["comando"])


def test_los_ejemplos_no_tienen_restos_de_otra_variante():
    for ejemplo in (SITIO / "ejemplos").rglob("*"):
        if ejemplo.suffix in (".js", ".jsx"):
            texto = ejemplo.read_text(encoding="utf-8")
            assert "type " not in texto and ": unknown" not in texto and "<Producto" not in texto, ejemplo


def test_compartir_la_pagina_muestra_imagen_y_logo():
    """Si falla: ejecutá python scripts/compartir_sitio.py (o --etiquetas) y subí lo que cambió."""
    import struct

    import compartir_sitio

    for ruta, texto in compartir_sitio.archivos_de_texto().items():
        assert ruta.read_text(encoding="utf-8") == texto, f"{ruta.name} no está al día"
    for pagina in compartir_sitio.paginas():
        contenido = pagina["archivo"].read_text(encoding="utf-8")
        for etiqueta in ('property="og:image"', 'name="twitter:card" content="summary_large_image"', 'rel="canonical"', 'rel="apple-touch-icon"'):
            assert etiqueta in contenido, (pagina["clave"], etiqueta)
        imagen = SITIO / pagina["imagen"]
        assert imagen.is_file(), f"falta {imagen.name}: ejecutá python scripts/compartir_sitio.py"
        ancho, alto = struct.unpack(">II", imagen.read_bytes()[16:24])
        assert (ancho, alto) == (1200, 630), imagen.name
    # Los datos estructurados (para buscadores) son JSON válido: SoftwareApplication en la
    # portada; TechArticle y la ruta de navegación en cada guía.
    import json

    for pagina in compartir_sitio.paginas():
        contenido = pagina["archivo"].read_text(encoding="utf-8")
        bloques = re.findall(r'<script type="application/ld\+json">(.*?)</script>', contenido)
        assert len(bloques) == 1, pagina["clave"]
        datos = json.loads(bloques[0])
        tipos = {d["@type"] for d in datos} if isinstance(datos, list) else {datos["@type"]}
        esperado = {"SoftwareApplication"} if pagina["clave"] == "index" else {"TechArticle", "BreadcrumbList"}
        assert tipos == esperado, pagina["clave"]
    for icono in ("icono-32.png", "apple-touch-icon.png", "icono-192.png", "icono-512.png"):
        assert (SITIO / "img" / icono).is_file(), icono


def test_cada_pieza_tiene_forma_general_y_variantes(datos):
    for tecnologia in datos["tecnologias"]:
        for variante in tecnologia["variantes"]:
            for pieza in variante["piezas"]:
                assert pieza["forma"].startswith(f"python -m andamio nuevo {pieza['clave']}"), (tecnologia["clave"], pieza["clave"])
                comandos = [v["comando"] for v in pieza["variantes"]]
                assert comandos[0] == pieza["comando"]
                assert any(c.endswith("--simular") for c in comandos)  # la simulación
                assert any(" new " in c for c in comandos)  # en inglés
                assert len(set(comandos)) == len(comandos)
                for opcion in pieza["opciones"]:
                    if opcion != "modo":
                        assert any(f"--{opcion.replace('_', '-')}" in c for c in comandos), (tecnologia["clave"], pieza["clave"], opcion)


def test_el_proyecto_completo_se_arma_de_verdad(datos):
    """Si falla: revisá RECORRIDOS en scripts/sitio.py (cada paso de andamio se ejecuta)."""
    for tecnologia in datos["tecnologias"]:
        for variante in tecnologia["variantes"]:
            pasos = variante["recorrido"]
            de_andamio = [p for p in pasos if p["andamio"]]
            assert pasos[0]["comando"].startswith(f"python -m andamio crear {tecnologia['clave']} "), tecnologia["clave"]
            assert len(de_andamio) >= 3, tecnologia["clave"]
            for paso in de_andamio:
                assert "Listo." in paso["salida"] and "Error" not in paso["salida"], paso["comando"]
            for paso in de_andamio[1:]:
                assert paso["creados"] or paso["modificados"], paso["comando"]
            assert all(p["explicacion"] for p in pasos)


def test_las_tecnologias_web_tienen_la_pestana_de_estilos(datos):
    for tecnologia in datos["tecnologias"]:
        piezas = {p["clave"] for p in tecnologia["variantes"][0]["piezas"]}
        if "tema" in piezas:
            assert tecnologia["estilos"] and {"base", "componente", "pagina"} <= set(tecnologia["estilos"]), tecnologia["clave"]
