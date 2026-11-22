"""Stack fastapi: crear el proyecto, generar recursos y ejecutar sus tests y la API."""

import os
import py_compile
import shutil
import subprocess
import sys

import pytest

from andamio.cli import main
from andamio.nucleo.deteccion import buscar_proyecto

from .apis import requiere

requiere_fastapi = requiere("fastapi")

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


def python(raiz, *argumentos, entorno=None):
    return subprocess.run(
        [sys.executable, *argumentos],
        cwd=raiz,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", **(entorno or {})},
    )


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "fastapi", "Mi API"]) == 0
    raiz = en_carpeta / "mi-api"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_recursos(proyecto):
    assert main(["nuevo", "recurso", "producto", *TODOS_LOS_TIPOS]) == 0
    assert main(["nuevo", "recurso", "cliente", "nombre", "email:email"]) == 0
    return proyecto


# --- Sin necesidad de FastAPI instalado -----------------------------------------


def test_estructura_del_proyecto(proyecto):
    for archivo in [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/db.py",
        "app/tipos.py",
        "app/errores.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "requirements.txt",
        ".env",
        ".env.example",
        ".gitignore",
        "README.md",
    ]:
        assert (proyecto / archivo).is_file(), archivo
    assert "datos.db" in leer(proyecto / ".gitignore")
    assert "fastapi" in leer(proyecto / "requirements.txt")
    assert 'title="API de Mi api"' in leer(proyecto / "app/main.py")
    for archivo in proyecto.rglob("*"):
        if archivo.is_file():
            assert "@@" not in leer(archivo), archivo


def test_dos_veces_el_mismo_proyecto(proyecto, en_carpeta, monkeypatch, capsys):
    monkeypatch.chdir(en_carpeta)
    capsys.readouterr()
    assert main(["crear", "fastapi", "mi-api"]) == 1
    assert "no está vacía" in capsys.readouterr().err


def test_recurso_genera_el_modulo_y_lo_registra(con_recursos):
    raiz = con_recursos
    for archivo in ["app/productos/__init__.py", "app/productos/modelo.py", "app/productos/router.py", "tests/test_productos.py"]:
        assert (raiz / archivo).is_file(), archivo
    main_py = leer(raiz / "app/main.py")
    assert (
        "from app.productos.router import router as productos_router\n"
        "from app.clientes.router import router as clientes_router\n"
        "# --- andamio:imports"
    ) in main_py
    assert "app.include_router(productos_router)\napp.include_router(clientes_router)\n# --- andamio:routers" in main_py
    for archivo in raiz.rglob("*.py"):
        py_compile.compile(str(archivo), doraise=True)
    for archivo in raiz.rglob("*"):
        if archivo.is_file() and archivo.suffix != ".pyc":
            assert "@@" not in leer(archivo), archivo


def test_tipos_de_campo_del_modelo(con_recursos):
    modelo = leer(con_recursos / "app/productos/modelo.py")
    for esperado in [
        "nombre: str = Field(min_length=1, max_length=200)",
        "descripcion: str = Field(min_length=1, sa_type=Text)",
        "precio: Decimal = Field(max_digits=10, decimal_places=2)",
        "stock: int\n",
        "peso: float\n",
        "activo: bool = False",
        "vence: date\n",
        "publicado: FechaHora\n",
        "contacto: EmailStr = Field(max_length=254)",
        '__tablename__ = "productos"',
        "precio: DecimalNumero",
        "stock: int | None = None",
        "from app.tipos import DecimalNumero, FechaHora, ahora",
    ]:
        assert esperado in modelo, esperado
    router = leer(con_recursos / "app/productos/router.py")
    assert "from sqlmodel import col, or_, select" in router
    assert "col(Producto.descripcion).icontains(search)," in router
    assert "publicado: FechaHora | None = None," in router
    assert "descripcion: str | None = None," not in router  # el texto largo no se filtra
    assert 'router = APIRouter(prefix="/api/productos", tags=["Productos"])' in router


def test_busqueda_segun_los_campos_de_texto(proyecto):
    assert main(["nuevo", "recurso", "evento", "fecha:datetime", "lugar"]) == 0
    assert main(["nuevo", "recurso", "medicion", "valor:float"]) == 0
    eventos = leer(proyecto / "app/eventos/router.py")
    assert "from sqlmodel import col, select" in eventos
    assert "consulta = consulta.where(col(Evento.lugar).icontains(search))" in eventos
    mediciones = leer(proyecto / "app/mediciones/router.py")
    assert "icontains" not in mediciones and "from app.tipos import ahora" in mediciones
    assert "from datetime import datetime, timezone" in leer(proyecto / "tests/test_eventos.py")
    assert "from datetime" not in leer(proyecto / "tests/test_mediciones.py")


def test_nombre_compuesto(proyecto):
    assert main(["nuevo", "recurso", "Línea Venta", "cantidad:int"]) == 0
    assert "class LineaVenta(LineaVentaBase, table=True):" in leer(proyecto / "app/lineas_venta/modelo.py")
    assert 'URL = "/api/lineas_venta/"' in leer(proyecto / "tests/test_lineas_venta.py")


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        (["recurso", "tipo", "nombre"], "ya existe app/tipos.py"),
        (["recurso", "conf", "nombre", "--plural", "config"], "ya existe app/config.py"),
        (["recurso", "producto", "sesion"], "lo usa el código generado"),
        (["recurso", "producto", "search"], "?search="),
        (["recurso", "producto", "id_producto"], "el id"),
        (["recurso", "producto", "json"], "SQLModel"),
        (["recurso", "producto", "model_config"], "SQLModel"),
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


def test_router_registrado_pero_borrado(con_recursos, capsys):
    shutil.rmtree(con_recursos / "app/clientes")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "cliente", "nombre"]) == 1
    assert "ya está registrado en app/main.py" in capsys.readouterr().err


def test_marcadores_borrados(proyecto, capsys):
    main_py = proyecto / "app/main.py"
    main_py.write_text(leer(main_py).replace("# --- andamio:routers (no borrar esta línea) ---\n", ""), encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 0
    salida = capsys.readouterr().out
    assert "app.include_router(productos_router)" in salida
    assert "from app.productos.router import router as productos_router" in leer(main_py)


def test_detecta_fastapi_desde_cualquier_carpeta(proyecto):
    # app/ tiene main.py y db.py, igual que un proyecto de consola: no hay que confundirlos.
    assert buscar_proyecto(proyecto / "app") == (buscar_proyecto(proyecto)[0], proyecto)
    assert buscar_proyecto(proyecto / "app")[0].clave == "fastapi"
    assert buscar_proyecto(proyecto / "tests")[0].clave == "fastapi"


def test_crear_desde_el_menu(en_carpeta, respuestas, capsys):
    respuestas(["3", "mi api", "s"])
    assert main([]) == 0
    assert "python -m uvicorn app.main:app --reload" in capsys.readouterr().out
    assert (en_carpeta / "mi-api/app/main.py").is_file()


def test_menu_interactivo(proyecto, respuestas, capsys):
    respuestas(["1", "producto", "", "n", "nombre", "1", "precio", "4", "", "s"])  # n: sin --protegido
    capsys.readouterr()
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto FastAPI detectado." in salida
    assert "python -m uvicorn app.main:app --reload" in salida
    assert "precio: Decimal = Field(max_digits=10, decimal_places=2)" in leer(proyecto / "app/productos/modelo.py")


# --- Con FastAPI instalado -----------------------------------------------------


@pytest.mark.fastapi
@requiere_fastapi
def test_tests_generados(con_recursos):
    assert main(["nuevo", "recurso", "evento", "fecha:datetime", "lugar"]) == 0
    assert main(["nuevo", "recurso", "medicion", "valor:float"]) == 0
    resultado = python(con_recursos, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "error")
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert "20 passed" in resultado.stdout


CONTRATO = """\
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

URL = "/api/productos/"
DATOS = {
    "nombre": "Yerba", "descripcion": "1 kg", "precio": 4850.5, "stock": 3, "peso": 1.5, "activo": True,
    "vence": "2027-01-01", "publicado": "2026-11-19T10:30", "contacto": "ventas@ejemplo.com",
}

with TestClient(app) as c:  # with: arranca la app (crea las tablas)
    r = c.post(URL, json=DATOS)
    assert r.status_code == 201, r.text
    p = r.json()
    assert p["precio"] == 4850.5, "decimal como número"
    assert p["publicado"] == "2026-11-19T10:30:00-03:00", p["publicado"]
    assert datetime.fromisoformat(p["creado"]).utcoffset() is not None
    c.post(URL, json={**DATOS, "nombre": "Mate", "precio": "12500", "activo": False})
    assert isinstance(c.get(URL).json(), list)
    assert [x["nombre"] for x in c.get(URL, params={"ordering": "-precio"}).json()] == ["Mate", "Yerba"]
    assert [x["nombre"] for x in c.get(URL, params={"search": "yer"}).json()] == ["Yerba"]
    assert [x["nombre"] for x in c.get(URL, params={"activo": "false"}).json()] == ["Mate"]
    assert len(c.get(URL, params={"publicado": "2026-11-19T13:30:00Z"}).json()) == 2
    assert c.get(URL, params={"stock": "abc"}).status_code == 400

    r = c.post(URL, json={"precio": "abc", "contacto": "no-es-mail"})
    assert r.status_code == 400
    errores = r.json()
    assert errores["nombre"] == ["Este campo es requerido."], errores
    assert errores["precio"] == ["Introduzca un número válido."], errores
    assert "correo" in errores["contacto"][0], errores
    r = c.post(URL, content="{roto", headers={"Content-Type": "application/json"})
    assert r.status_code == 400 and list(r.json()) == ["general"], r.text
    r = c.post(URL, json={**DATOS, "precio": 123456789012})
    assert "dígitos" in r.json()["precio"][0], r.text

    r = c.patch(f"{URL}{p['id']}/", json={"stock": 9})
    assert r.status_code == 200 and r.json()["stock"] == 9 and r.json()["nombre"] == "Yerba"
    assert c.put(f"{URL}{p['id']}/", json={"nombre": "x"}).status_code == 400
    assert c.get(f"{URL}abc/").status_code == 404
    assert c.get(f"{URL}999/").json() == {"detail": "No encontrado."}
    assert c.get("/api/productos", follow_redirects=False).status_code == 307
    r = c.options(URL, headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "DELETE"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
    r = c.delete(f"{URL}{p['id']}/")
    assert r.status_code == 204 and r.content == b""

    # La documentación funciona sin internet: Swagger se sirve desde el proyecto, no de un CDN.
    docs = c.get("/docs").text
    assert "/static-offline-docs/swagger-ui-bundle.js" in docs and "cdn." not in docs
    assert c.get("/static-offline-docs/swagger-ui-bundle.js").status_code == 200
    assert c.get("/api/", follow_redirects=False).headers["location"] == "/docs"
print("contrato ok")
"""


@pytest.mark.fastapi
@requiere_fastapi
def test_contrato_de_la_api(con_recursos, tmp_path):
    (con_recursos / "contrato.py").write_text(CONTRATO, encoding="utf-8")
    base = (tmp_path / "contrato.db").as_posix()
    resultado = python(con_recursos, "contrato.py", entorno={"DATABASE_URL": f"sqlite:///{base}", "ZONA_HORARIA": ""})
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert "contrato ok" in resultado.stdout


# --- Login con JWT (nuevo login) y recurso --protegido ------------------------------


def test_login_genera_el_paquete_y_lo_registra(proyecto):
    assert main(["nuevo", "login"]) == 0
    for archivo in ("modelo.py", "seguridad.py", "router.py"):
        assert (proyecto / "app/cuentas" / archivo).is_file(), archivo
    main_py = leer(proyecto / "app/main.py")
    assert "from app.cuentas.router import router as cuentas_router" in main_py
    assert "app.include_router(cuentas_router)" in main_py
    assert 'SECRET_KEY = os.getenv("SECRET_KEY")' in leer(proyecto / "app/config.py")
    # La clave de verdad va al .env (al azar); la de ejemplo, al .env.example.
    env = leer(proyecto / ".env")
    clave = next(linea for linea in env.splitlines() if linea.startswith("SECRET_KEY=")).split("=", 1)[1]
    assert len(clave) >= 40 and "cambiar" not in clave
    assert "SECRET_KEY=cambiar-por-una-clave-larga-y-secreta" in leer(proyecto / ".env.example")
    assert "PyJWT~=" in leer(proyecto / "requirements.txt")
    # Las rutas del mismo contrato que la API de Django.
    router = leer(proyecto / "app/cuentas/router.py")
    for ruta in ('"/registro/"', '"/token/"', '"/token/refresh/"', '"/yo/"'):
        assert ruta in router
    # La contraseña se guarda con hash (PBKDF2, como Django), nunca tal cual.
    assert "pbkdf2_hmac" in leer(proyecto / "app/cuentas/seguridad.py")


def test_login_una_sola_vez(proyecto, capsys):
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "login", "acceso"]) == 1
    assert "ya tiene el login" in capsys.readouterr().err


def test_recurso_protegido_necesita_el_login(proyecto, capsys):
    assert main(["nuevo", "recurso", "pedido", "total:decimal", "--protegido"]) == 1
    assert "nuevo login" in capsys.readouterr().err
    assert not (proyecto / "app/pedidos").exists()


def test_recurso_protegido(proyecto):
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "recurso", "pedido", "total:decimal", "--protegido"]) == 0
    router = leer(proyecto / "app/pedidos/router.py")
    assert "from app.cuentas.seguridad import usuario_actual" in router
    assert "PIDE_LOGIN = [Depends(usuario_actual)]" in router
    assert router.count("dependencies=PIDE_LOGIN") == 4  # crear, reemplazar, modificar y eliminar
    assert '@router.get("/", response_model=list[PedidoLeer])' in router  # ver es libre
    assert "def test_sin_login_no_se_puede_crear" in leer(proyecto / "tests/test_pedidos.py")
    assert "Authorization: Bearer {{token}}" in leer(proyecto / "http/pedidos.http")


def test_recurso_sin_protegido_no_cambia(proyecto):
    assert main(["nuevo", "recurso", "nota", "texto"]) == 0
    router = leer(proyecto / "app/notas/router.py")
    assert "PIDE_LOGIN" not in router and "Depends" not in router
    assert "con_login" not in leer(proyecto / "tests/test_notas.py")


@pytest.mark.fastapi
@requiere_fastapi
@pytest.mark.skipif(shutil.which("python") is None and not sys.executable, reason="sin Python")
def test_tests_generados_con_login(proyecto):
    pytest.importorskip("jwt")
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "recurso", "pedido", "cliente", "total:decimal", "--protegido"]) == 0
    assert main(["nuevo", "recurso", "nota", "texto"]) == 0
    resultado = python(proyecto, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "error")
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert "18 passed" in resultado.stdout
