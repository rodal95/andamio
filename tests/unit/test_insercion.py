from andamio.nucleo.insercion import (
    agregar_al_final,
    insertar_antes_de_marcador,
    linea_marcador,
    ya_presente,
)

SETTINGS = """LOCAL_APPS = [
    "productos",
    # --- andamio:apps (no borrar esta línea) ---
]
"""


def test_inserta_antes_del_marcador_con_su_sangria():
    resultado = insertar_antes_de_marcador(SETTINGS, "apps", '"clientes",')
    assert resultado == """LOCAL_APPS = [
    "productos",
    "clientes",
    # --- andamio:apps (no borrar esta línea) ---
]
"""


def test_inserta_varias_lineas():
    resultado = insertar_antes_de_marcador("  // --- andamio:x ---\n", "x", "a\nb")
    assert resultado == "  a\n  b\n  // --- andamio:x ---\n"


def test_marcador_faltante_devuelve_none():
    assert insertar_antes_de_marcador('LOCAL_APPS = [\n    "productos",\n]\n', "apps", '"x",') is None


def test_no_confunde_claves_con_prefijo_comun():
    texto = "# andamio:appsx\n# andamio:apps\n"
    assert insertar_antes_de_marcador(texto, "apps", "N") == "# andamio:appsx\nN\n# andamio:apps\n"


def test_el_texto_del_marcador_puede_cambiar():
    assert insertar_antes_de_marcador("# andamio:apps, no la borres\n", "apps", "x") == "x\n# andamio:apps, no la borres\n"


def test_respeta_crlf():
    texto = "a\r\n# --- andamio:m ---\r\n"
    assert insertar_antes_de_marcador(texto, "m", "b") == "a\r\nb\r\n# --- andamio:m ---\r\n"


def test_agregar_al_final():
    assert agregar_al_final("a\n", "b") == "a\nb\n"
    assert agregar_al_final("a", "b") == "a\nb\n"
    assert agregar_al_final("", "b") == "b\n"
    assert agregar_al_final("a\r\n", "b\nc") == "a\r\nb\r\nc\r\n"


def test_ya_presente():
    assert ya_presente(SETTINGS, '"productos",')
    assert not ya_presente(SETTINGS, '"clientes",')


def test_linea_marcador():
    assert linea_marcador("apps") == "# --- andamio:apps (no borrar esta línea) ---"
    assert linea_marcador("exports", "//") == "// --- andamio:exports (no borrar esta línea) ---"
