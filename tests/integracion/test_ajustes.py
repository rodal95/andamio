"""andamio.json (la configuración opcional de un proyecto) y el comando init."""

import json

import pytest

from andamio.cli import main
from andamio.nucleo import ajustes
from andamio.nucleo.errores import AndamioError


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ('{"stack": "react",}', "no es un JSON válido (línea 1"),
        ('{"stak": "react"}', "no conozco 'stak'"),
        ('{"variante": "python"}', '"variante" tiene que ser "ts" o "js"'),
        ('{"guia": "no"}', '"guia" tiene que ser true o false'),
        ('{"version": 2}', "la versión 2 no existe"),
        ('{"conexiones": {"rutas": "../otro/App.tsx"}}', "dentro del proyecto"),
        ('{"conexiones": {"rutas": "C:/x/App.tsx"}}', "dentro del proyecto"),
        ('["react"]', "tiene que ser un objeto"),
    ],
)
def test_errores_claros_en_andamio_json(texto, esperado):
    with pytest.raises(AndamioError) as error:
        ajustes.desde_texto(texto)
    assert esperado in error.value.mensaje


def test_valores_por_defecto():
    leidos = ajustes.desde_texto('{"stack": "vue"}')
    assert leidos.stack == "vue" and leidos.guia is None and leidos.plantillas == ".andamio/plantillas"
    assert leidos.conexiones == {}


def _proyecto_vite(carpeta):
    """Un proyecto React hecho sin andamio (como npm create vite): sin marcadores."""
    (carpeta / "src").mkdir(parents=True)
    (carpeta / "package.json").write_text('{"dependencies": {"react": "^19", "react-dom": "^19"}, "devDependencies": {"vite": "^7"}}', encoding="utf-8")
    (carpeta / "tsconfig.json").write_text("{}", encoding="utf-8")
    (carpeta / "src/App.tsx").write_text("export default function App() { return <h1>Hola</h1>; }\n", encoding="utf-8")
    (carpeta / "src/main.tsx").write_text("import App from './App';\n", encoding="utf-8")
    return carpeta


def test_init_en_un_proyecto_que_no_hizo_andamio(en_carpeta, monkeypatch, capsys):
    raiz = _proyecto_vite(en_carpeta / "vite")
    monkeypatch.chdir(raiz)
    assert main(["init"]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto React + Vite (TypeScript)" in salida
    assert "falta  src/App.tsx  andamio:rutas" in salida
    assert "{/* --- andamio:rutas (no borrar esta línea) --- */}" in salida
    assert json.loads(leer(raiz / "andamio.json"))["stack"] == "react"
    assert leer(raiz / "src/App.tsx").startswith("export default")  # no toca tu código
    # La segunda vez no pisa andamio.json.
    (raiz / "andamio.json").write_text('{"stack": "react", "guia": false}', encoding="utf-8")
    assert main(["init"]) == 0
    assert "Ya existe andamio.json" in capsys.readouterr().out
    assert json.loads(leer(raiz / "andamio.json"))["guia"] is False


def test_init_de_un_proyecto_de_andamio_tiene_todo_conectado(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "vue", "web"]) == 0
    monkeypatch.chdir(en_carpeta / "web")
    capsys.readouterr()
    assert main(["init", "--simular"]) == 0
    salida = capsys.readouterr().out
    assert "falta" not in salida and "ok" in salida
    assert not (en_carpeta / "web/andamio.json").exists()


def test_init_sin_tipo_fuera_de_un_proyecto(en_carpeta, capsys):
    assert main(["init"]) == 1
    assert "init <tipo>" in capsys.readouterr().err
    assert main(["init", "fastapi"]) == 0
    assert json.loads(leer(en_carpeta / "andamio.json"))["stack"] == "fastapi"


def test_stack_que_no_existe_en_andamio_json(en_carpeta, capsys):
    (en_carpeta / "andamio.json").write_text('{"stack": "angular"}', encoding="utf-8")
    assert main(["info"]) == 1
    assert "el stack 'angular' no existe" in capsys.readouterr().err


def test_crear_sin_guia_queda_anotado_para_las_piezas(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "django", "api", "--sin-guia"]) == 0
    raiz = en_carpeta / "api"
    assert json.loads(leer(raiz / "andamio.json"))["guia"] is False
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "recurso", "producto", "nombre:str"]) == 0
    assert leer(raiz / "productos/models.py").startswith("from django.db import models")
    capsys.readouterr()
    assert main(["info"]) == 0
    assert "Configuración: andamio.json (guía: no)" in capsys.readouterr().out


def test_plantillas_en_otra_carpeta(en_carpeta, monkeypatch):
    assert main(["crear", "python", "consola"]) == 0
    raiz = en_carpeta / "consola"
    (raiz / "andamio.json").write_text('{"stack": "python", "plantillas": "plantillas-catedra"}', encoding="utf-8")
    monkeypatch.chdir(raiz)
    assert main(["plantillas", "exportar", "entidad"]) == 0
    plantilla = raiz / "plantillas-catedra/python/entidad/entidades/@@nombre@@.py"
    assert plantilla.is_file() and not (raiz / ".andamio").exists()
    plantilla.write_text("# versión de la cátedra: @@Nombre@@\n", encoding="utf-8")
    assert main(["nuevo", "entidad", "cliente", "nombre:str"]) == 0
    assert leer(raiz / "entidades/cliente.py") == "# versión de la cátedra: Cliente\n"


def test_conexiones_en_otro_archivo(en_carpeta, monkeypatch):
    # Las rutas de React en un archivo propio (src/router.tsx) en lugar de src/App.tsx.
    assert main(["crear", "react", "web"]) == 0
    raiz = en_carpeta / "web"
    (raiz / "src/router.tsx").write_text(
        "// --- andamio:imports (no borrar esta línea) ---\n"
        "export const rutas = (\n  <>\n    {/* --- andamio:rutas (no borrar esta línea) --- */}\n  </>\n);\n",
        encoding="utf-8",
    )
    (raiz / "andamio.json").write_text(
        json.dumps({"stack": "react", "conexiones": {"rutas": "src/router.tsx", "imports": "src/router.tsx"}}), encoding="utf-8"
    )
    app_antes = leer(raiz / "src/App.tsx")
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    router = leer(raiz / "src/router.tsx")
    assert "ContactoPage" in router and 'path="/contacto"' in router
    assert "ContactoPage" not in leer(raiz / "src/App.tsx").replace(app_antes, "")  # las rutas no van a App.tsx


def test_el_error_dice_de_que_carpeta_es_el_andamio_json(en_carpeta, monkeypatch, capsys):
    # Un andamio.json roto en una carpeta de más arriba: el error dice cuál es.
    (en_carpeta / "andamio.json").write_text('{"stack": "react",}', encoding="utf-8")
    (en_carpeta / "sub").mkdir()
    monkeypatch.chdir(en_carpeta / "sub")
    assert main(["info"]) == 1
    error = capsys.readouterr().err
    assert str(en_carpeta / "andamio.json") in error and "no es un JSON válido" in error
