"""Stack express: crear el proyecto (TypeScript y JavaScript), generar recursos y probarlos."""

import json
import re
import shutil

import pytest

from andamio import stacks
from andamio.cli import main
from andamio.nucleo.deteccion import buscar_proyecto

from .node import NPM, NPX, ejecutar, npm_install, requiere_node

TODOS_LOS_TIPOS = [
    "nombre:str",
    "descripcion:text",
    "precio:decimal",
    "stock:int",
    "peso:float",
    "activo:bool",
    "vence:date",
    "publicado:datetime",
    "contacto:email",
]


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture(params=["ts", "js"])
def variante(request):
    return request.param


@pytest.fixture
def proyecto(en_carpeta, monkeypatch, variante):
    assert main(["crear", "express", "Mi API", "--variante", variante]) == 0
    raiz = en_carpeta / "mi-api"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_recursos(proyecto):
    assert main(["nuevo", "recurso", "producto", *TODOS_LOS_TIPOS]) == 0
    assert main(["nuevo", "recurso", "cliente", "nombre", "email:email"]) == 0
    return proyecto


def _archivos(raiz):
    return {p.relative_to(raiz).as_posix() for p in raiz.rglob("*") if p.is_file()}


# --- Sin necesidad de Node ------------------------------------------------------


def test_estructura_del_proyecto(proyecto, variante):
    ext = variante
    esperados = {
        ".env",
        ".env.example",
        ".gitignore",
        "andamio-guia.html",
        "README.md",
        "package.json",
        f"prisma.config.{ext}",
        "prisma/schema.prisma",
        *(f"src/{n}.{ext}" for n in ("app", "config", "db", "docs", "errores", "fechas", "servidor", "validacion")),
        f"tests/api.{ext}",
    }
    if variante == "ts":
        esperados.add("tsconfig.json")
    assert _archivos(proyecto) == esperados
    paquete = json.loads(leer(proyecto / "package.json"))
    assert paquete["name"] == "mi-api"
    assert ("typescript" in paquete["devDependencies"]) == (variante == "ts")
    assert "--force-reset" not in paquete["scripts"]["pretest"]  # los tests no borran bases con Prisma
    assert "PORT=8000" in leer(proyecto / ".env")
    for archivo in proyecto.rglob("*"):
        if archivo.is_file():
            assert "@@" not in leer(archivo).replace("@@map", ""), archivo


def test_recurso_genera_y_registra(con_recursos, variante):
    raiz, ext = con_recursos, variante
    for archivo in (f"src/productos/esquema.{ext}", f"src/productos/router.{ext}", f"tests/productos.test.{ext}"):
        assert (raiz / archivo).is_file(), archivo
    app = leer(raiz / f"src/app.{ext}")
    assert f"import {{ productosDocs, productosRouter }} from './productos/router.{ext}';" in app
    assert "app.use('/api/productos', productosRouter);\napp.use('/api/clientes', clientesRouter);\n// --- andamio:rutas" in app
    assert "  productosDocs,\n  clientesDocs,\n  // --- andamio:docs" in app
    esquema = leer(raiz / "prisma/schema.prisma")
    assert re.search(r"model Producto \{\n  id +Int +@id @default\(autoincrement\(\)\)\n", esquema)
    assert re.search(r"\n  activo +Boolean +@default\(false\)\n", esquema)
    assert re.search(r"\n  actualizado +DateTime +@updatedAt\n\n  @@map\(\"productos\"\)\n\}\n", esquema)
    assert esquema.index("model Producto") < esquema.index("model Cliente") < esquema.index("andamio:modelos")
    for archivo in raiz.rglob("*"):
        if archivo.is_file():
            assert "@@" not in leer(archivo).replace("@@map", ""), archivo


def test_validacion_y_json_del_recurso(con_recursos, variante):
    esquema = leer(con_recursos / f"src/productos/esquema.{variante}")
    for esperado in [
        "nombre: texto(),",
        "descripcion: textoLargo(),",
        "precio: decimal(),",
        "stock: entero(),",
        "peso: numero(),",
        "activo: booleano(),",
        "vence: fecha(),",
        "publicado: fechaHora(),",
        "contacto: correo(),",
        "export const productoCrear = z.object({ ...campos, activo: campos.activo.default(false) });",
        "export const productoActualizar = z.object(campos).partial();",
        "stock: campos.stock.optional(),",
        "precio: producto.precio.toNumber(),",
        "vence: jsonFecha(producto.vence),",
        "publicado: jsonFechaHora(producto.publicado),",
        "import { jsonFecha, jsonFechaHora } from '../fechas.",
    ]:
        assert esperado in esquema, esperado
    assert "descripcion: campos.descripcion" not in esquema  # el texto largo no se filtra
    router = leer(con_recursos / f"src/productos/router.{variante}")
    assert "{ descripcion: { contains: search } }," in router and "OR: [" in router
    if variante == "js":
        for sintaxis in ("import type", " as Prisma", "): string", ": DocsRecurso"):
            assert sintaxis not in esquema + router, sintaxis


def test_busqueda_segun_los_campos_de_texto(proyecto, variante):
    assert main(["nuevo", "recurso", "evento", "fecha:datetime", "lugar"]) == 0
    assert main(["nuevo", "recurso", "medicion", "valor:float"]) == 0
    eventos = leer(proyecto / f"src/eventos/router.{variante}")
    assert "...(search ? { lugar: { contains: search } } : {})," in eventos and "OR:" not in eventos
    assert "contains" not in leer(proyecto / f"src/mediciones/router.{variante}")
    assert "export const medicionCrear = z.object(campos);" in leer(proyecto / f"src/mediciones/esquema.{variante}")
    assert "new Date('2025-02-20T18:45:00Z').getTime()" in leer(proyecto / f"tests/eventos.test.{variante}")


def test_nombre_compuesto(proyecto, variante):
    assert main(["nuevo", "recurso", "Línea Venta", "cantidad:int"]) == 0
    assert "model LineaVenta {" in leer(proyecto / "prisma/schema.prisma")
    router = leer(proyecto / f"src/lineas_venta/router.{variante}")
    assert "export const lineasVentaRouter = Router();" in router and "prisma.lineaVenta.findMany" in router
    assert "app.use('/api/lineas_venta', lineasVentaRouter);" in leer(proyecto / f"src/app.{variante}")


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        (["recurso", "generado", "nombre", "--plural", "generated"], "cliente de Prisma"),
        (["recurso", "producto", "search"], "?search="),
        (["recurso", "producto", "ordering"], "?ordering="),
        (["recurso", "producto", "precio:money"], "Tipos válidos: str, text, int, decimal"),
        (["recurso", "productos", "nombre"], "parece estar en plural"),
    ],
)
def test_nombres_que_no_se_pueden_usar(proyecto, capsys, argumentos, esperado):
    assert main(["nuevo", *argumentos]) == 1
    assert esperado in capsys.readouterr().err


def test_recurso_repetido_no_toca_nada(con_recursos, capsys):
    antes = {p: p.read_bytes() for p in con_recursos.rglob("*") if p.is_file()}
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 1
    assert "productos" in capsys.readouterr().err
    assert antes == {p: p.read_bytes() for p in con_recursos.rglob("*") if p.is_file()}


def test_modelo_o_router_que_ya_existen(con_recursos, variante, capsys):
    shutil.rmtree(con_recursos / "src/clientes")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "cliente", "nombre"]) == 1
    assert "ya existe el modelo Cliente en prisma/schema.prisma" in capsys.readouterr().err
    esquema = con_recursos / "prisma/schema.prisma"
    esquema.write_text(leer(esquema).replace("model Cliente {", "model Comprador {"), encoding="utf-8")
    assert main(["nuevo", "recurso", "cliente", "nombre"]) == 1
    assert f"ya está registrado en src/app.{variante}" in capsys.readouterr().err


def test_marcadores_borrados(proyecto, variante, capsys):
    app = proyecto / f"src/app.{variante}"
    app.write_text(leer(app).replace("// --- andamio:rutas (no borrar esta línea) ---\n", ""), encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 0
    salida = capsys.readouterr().out
    assert "app.use('/api/productos', productosRouter);" in salida
    assert "productosDocs," in leer(app)


def test_migrar_sin_dependencias(proyecto, capsys):
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre", "--migrar"]) == 1
    error = capsys.readouterr().err
    assert "npm install" in error and "npx prisma migrate dev --name productos" in error
    assert (proyecto / "src/productos").is_dir()  # los archivos se generan igual


def test_deteccion(proyecto, variante, en_carpeta):
    express = stacks.por_clave("express")
    for carpeta in (proyecto, proyecto / "src", proyecto / "prisma", proyecto / "tests"):
        assert buscar_proyecto(carpeta) == (express, proyecto)
    assert express.detectar_variante(proyecto) == variante
    # Un proyecto de React que además usa express sigue siendo de React.
    web = en_carpeta / "web"
    web.mkdir()
    (web / "package.json").write_text(json.dumps({"dependencies": {"react": "19", "vite": "8", "express": "5"}}), encoding="utf-8")
    assert buscar_proyecto(web)[0].clave == "react"


def test_menu(en_carpeta, respuestas, capsys, monkeypatch):
    respuestas(["4", "2", "mi api", "s"])
    assert main([]) == 0
    assert (en_carpeta / "mi-api/src/app.js").is_file()
    respuestas(["1", "producto", "", "nombre", "1", "", "s", "n"])
    monkeypatch.chdir(en_carpeta / "mi-api")
    capsys.readouterr()
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto Express + Prisma (JavaScript) detectado." in salida
    assert "npx prisma migrate dev --name productos" in salida


# --- Con Node: instalar, migrar, tests generados y tipos -------------------------


@pytest.mark.lento
@requiere_node
def test_el_proyecto_generado_instala_migra_y_pasa_sus_tests(con_recursos, variante):
    raiz = con_recursos
    assert main(["nuevo", "recurso", "evento", "fecha:datetime", "lugar"]) == 0
    assert main(["nuevo", "recurso", "medicion", "valor:float"]) == 0
    npm_install(raiz)
    if variante == "ts":
        ejecutar([NPX, "prisma", "migrate", "dev", "--name", "inicial"], raiz)
    else:
        # En JavaScript se prueba la opción --migrar (andamio ejecuta la migración).
        assert main(["nuevo", "recurso", "marca", "nombre", "--migrar"]) == 0
    assert list((raiz / "prisma/migrations").glob("*/migration.sql"))
    resultado = ejecutar([NPM, "test"], raiz)
    total = 25 if variante == "js" else 20
    assert f"# pass {total}" in resultado.stdout and "# fail 0" in resultado.stdout, resultado.stdout[-3000:]
    if variante == "ts":
        ejecutar([NPM, "run", "tipos"], raiz)
