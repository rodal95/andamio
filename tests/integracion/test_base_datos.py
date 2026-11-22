"""andamio base: conectar la API a PostgreSQL, MySQL o SQLite (con Docker si se pide)."""

import json

import pytest
from dotenv import dotenv_values

from andamio import base_datos
from andamio.base_datos import leer_url
from andamio.cli import main
from andamio.nucleo.errores import AndamioError

from .node import NPM, ejecutar, npm_install, requiere_node, resultado_de_node_test


@pytest.fixture(autouse=True)
def _sin_red(monkeypatch):
    """Que no intente conectarse a nada de verdad."""
    monkeypatch.setattr(base_datos, "puerto_en_uso", lambda *a, **k: False)


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def crear(en_carpeta, monkeypatch, tipo):
    assert main(["crear", tipo, "Mi Tienda"]) == 0
    raiz = en_carpeta / "mi-tienda"
    monkeypatch.chdir(raiz)
    return raiz


def test_django_postgres_en_docker(en_carpeta, monkeypatch):
    raiz = crear(en_carpeta, monkeypatch, "django")
    assert main(["base", "postgres", "--docker"]) == 0
    env = dotenv_values(raiz / ".env")
    assert env["DB_NOMBRE"] == "mi_tienda" and env["DB_USUARIO"] == "app" and env["DB_PUERTO"] == "5432"
    assert len(env["DB_CLAVE"]) >= 20  # al azar
    assert env["DATABASE_URL"] == f"postgres://app:{env['DB_CLAVE']}@localhost:5432/mi_tienda"
    compose = leer(raiz / "docker-compose.yml")
    assert "image: postgres:17" in compose and "${DB_CLAVE}" in compose and '"127.0.0.1:${DB_PUERTO}:5432"' in compose
    assert "psycopg[binary]" in leer(raiz / "requirements.txt")
    # La contraseña real no va al .env.example (se sube a git).
    ejemplo = leer(raiz / ".env.example")
    assert env["DB_CLAVE"] not in ejemplo and "DB_CLAVE=cambiar-por-una-clave" in ejemplo
    assert "# DATABASE_URL=postgres://app:cambiar-por-una-clave@localhost:5432/mi_tienda" in ejemplo


def test_no_sobrescribe_el_compose_ni_repite_el_driver(en_carpeta, monkeypatch, capsys):
    raiz = crear(en_carpeta, monkeypatch, "django")
    assert main(["base", "postgres", "--docker"]) == 0
    assert main(["base", "postgres", "--docker"]) == 1
    assert "ya tiene un archivo de Docker Compose" in capsys.readouterr().err
    assert main(["base", "--url", "postgres://u:c@otra:5432/base"]) == 0
    assert leer(raiz / "requirements.txt").count("psycopg") == 1
    assert dotenv_values(raiz / ".env")["DATABASE_URL"] == "postgres://u:c@otra:5432/base"


def test_fastapi_url_con_una_clave_sin_codificar(en_carpeta, monkeypatch):
    make_url = pytest.importorskip("sqlalchemy.engine").make_url
    raiz = crear(en_carpeta, monkeypatch, "fastapi")
    assert main(["base", "--url", "postgresql://ana:p@ss w#rd$1@db.ejemplo.com:6543/tienda?sslmode=require"]) == 0
    url = make_url(dotenv_values(raiz / ".env")["DATABASE_URL"])
    assert url.drivername == "postgresql+psycopg"
    assert (url.username, url.password, url.host, url.port, url.database) == ("ana", "p@ss w#rd$1", "db.ejemplo.com", 6543, "tienda")
    assert url.query == {"sslmode": "require"}
    assert "p@ss" not in leer(raiz / ".env.example")


def test_reflex_mysql_en_docker(en_carpeta, monkeypatch):
    raiz = crear(en_carpeta, monkeypatch, "reflex")
    assert main(["base", "mysql", "--docker", "--puerto", "3307", "--nombre", "tienda"]) == 0
    env = dotenv_values(raiz / ".env")
    assert env["REFLEX_DB_URL"] == f"mysql+pymysql://app:{env['DB_CLAVE']}@localhost:3307/tienda"
    assert env["DB_CLAVE_ROOT"] and env["DB_CLAVE_ROOT"] != env["DB_CLAVE"]
    assert "MYSQL_ROOT_PASSWORD: ${DB_CLAVE_ROOT}" in leer(raiz / "docker-compose.yml")
    assert "PyMySQL" in leer(raiz / "requirements.txt")


def test_django_mysql_usa_mysqlclient(en_carpeta, monkeypatch, capsys):
    raiz = crear(en_carpeta, monkeypatch, "django")
    assert main(["base", "mysql", "--host", "10.0.0.5", "--usuario", "root", "--clave", "x y", "--nombre", "tienda"]) == 0
    assert "mysqlclient" in leer(raiz / "requirements.txt")
    assert dotenv_values(raiz / ".env")["DATABASE_URL"] == "mysql://root:x%20y@10.0.0.5:3306/tienda"
    assert "libmysqlclient-dev" in capsys.readouterr().out


def test_volver_a_sqlite(en_carpeta, monkeypatch):
    raiz = crear(en_carpeta, monkeypatch, "fastapi")
    assert main(["base", "--url", "postgresql://u:c@localhost/tienda"]) == 0
    assert main(["base", "sqlite"]) == 0
    assert "DATABASE_URL" not in dotenv_values(raiz / ".env")


def test_simular_no_toca_nada(en_carpeta, monkeypatch):
    raiz = crear(en_carpeta, monkeypatch, "django")
    antes = leer(raiz / ".env")
    assert main(["base", "postgres", "--docker", "--simular"]) == 0
    assert leer(raiz / ".env") == antes and not (raiz / "docker-compose.yml").exists()


def test_preguntando_los_datos(en_carpeta, monkeypatch, respuestas):
    raiz = crear(en_carpeta, monkeypatch, "django")
    # PostgreSQL, "escribo los datos", nombre, servidor, puerto y usuario por defecto, contraseña, confirmar.
    respuestas(["1", "3", "", "", "", "", "secreta", "s"])
    assert main(["base"]) == 0
    assert dotenv_values(raiz / ".env")["DATABASE_URL"] == "postgres://postgres:secreta@localhost:5432/mi_tienda"


@pytest.mark.parametrize(
    "tipo, mensaje",
    [("react", "lo hace la API"), ("vue", "lo hace la API"), ("python", "no se conecta a otra base")],
)
def test_proyectos_que_no_se_conectan(en_carpeta, monkeypatch, capsys, tipo, mensaje):
    crear(en_carpeta, monkeypatch, tipo)
    assert main(["base", "postgres"]) == 1
    assert mensaje in capsys.readouterr().err


@pytest.mark.parametrize(
    "url, error",
    [("http://x/y", "tipo de base"), ("postgres://usuario@servidor", "falta el servidor o el nombre"), ("sqlite:///a.db", "SQLite"), ("mysql://u@h:99999/b", "no es válida")],
)
def test_urls_que_no_sirven(url, error):
    with pytest.raises(AndamioError, match=error):
        leer_url(url)


def test_url_de_mysql_y_mariadb():
    conexion = leer_url("mariadb://root@localhost/tienda")
    assert (conexion.motor.clave, conexion.puerto, conexion.usuario, conexion.clave) == ("mysql", 3306, "root", "")


# --- Prisma: Express y Next.js full stack ---------------------------------------


@pytest.mark.parametrize("tipo, variante, db", [("express", "ts", "src/db.ts"), ("express", "js", "src/db.js"), ("next-fullstack", "ts", "lib/db.ts"), ("next-fullstack", "js", "lib/db.js")])
def test_prisma_postgres_en_docker(en_carpeta, monkeypatch, tipo, variante, db):
    assert main(["crear", tipo, "Mi Tienda", "--variante", variante]) == 0
    raiz = en_carpeta / "mi-tienda"
    monkeypatch.chdir(raiz)
    assert main(["base", "postgres", "--docker"]) == 0
    env = dotenv_values(raiz / ".env")
    assert env["DATABASE_URL"] == f"postgresql://app:{env['DB_CLAVE']}@localhost:5432/mi_tienda"
    assert env["TEST_DATABASE_URL"] == f"postgresql://app:{env['DB_CLAVE']}@localhost:5432/mi_tienda_test"
    assert 'provider = "postgresql"' in leer(raiz / "prisma/schema.prisma")
    conexion = leer(raiz / db)
    assert "import { PrismaPg } from '@prisma/adapter-pg';" in conexion and "new PrismaPg({ connectionString: " in conexion
    assert "BetterSqlite3" not in conexion and "con Prisma (PostgreSQL)" in conexion
    paquete = json.loads(leer(raiz / "package.json"))
    assert "@prisma/adapter-pg" in paquete["dependencies"] and "@prisma/adapter-better-sqlite3" not in paquete["dependencies"]
    assert paquete["dependencies"]["@prisma/adapter-pg"] == paquete["dependencies"]["@prisma/client"]
    assert paquete["scripts"]["pretest"] == "prisma generate && node scripts/base-de-tests.js"
    assert (raiz / "scripts/base-de-tests.js").is_file()
    api = leer(raiz / f"tests/api.{variante}")
    assert "process.env.DATABASE_URL = process.env.TEST_DATABASE_URL || 'file:./test.db';" in api
    assert "'file:./test.db';" not in api.replace("|| 'file:./test.db'", "")
    # .env.example: con Prisma la variable queda activa, con los datos del compose y sin la clave real.
    ejemplo = leer(raiz / ".env.example")
    assert "DATABASE_URL=postgresql://app:cambiar-por-una-clave@localhost:5432/mi_tienda\n" in ejemplo
    assert env["DB_CLAVE"] not in ejemplo


def test_prisma_mysql_y_volver_a_sqlite(en_carpeta, monkeypatch):
    raiz = crear(en_carpeta, monkeypatch, "express")
    assert main(["nuevo", "login"]) == 0
    assert main(["base", "mysql", "--docker"]) == 0
    env = dotenv_values(raiz / ".env")
    # El mismo usuario: en Docker tiene permiso para crear bases (la de los tests y la de Prisma).
    assert env["TEST_DATABASE_URL"] == f"mysql://app:{env['DB_CLAVE']}@localhost:3306/mi_tienda_test"
    assert "GRANT ALL PRIVILEGES ON *.* TO '${DB_USUARIO}'@'%';" in leer(raiz / "docker-compose.yml")
    conexion = leer(raiz / "src/db.ts")
    assert "new PrismaMariaDb(String(DATABASE_URL).replace(/^mysql:/, 'mariadb:'))" in conexion
    assert "@prisma/adapter-mariadb" in leer(raiz / "package.json")

    assert main(["base", "sqlite"]) == 0
    env = dotenv_values(raiz / ".env")
    assert env["DATABASE_URL"] == "file:./datos.db" and env["TEST_DATABASE_URL"] == "file:./test.db"
    assert 'provider = "sqlite"' in leer(raiz / "prisma/schema.prisma")
    assert "new PrismaBetterSqlite3({ url: DATABASE_URL })" in leer(raiz / "src/db.ts")
    paquete = json.loads(leer(raiz / "package.json"))
    assert set(paquete["dependencies"]) & {"@prisma/adapter-pg", "@prisma/adapter-mariadb"} == set()
    assert "@prisma/adapter-better-sqlite3" in paquete["dependencies"]


def test_prisma_avisa_que_las_migraciones_son_de_otro_motor(en_carpeta, monkeypatch, capsys):
    raiz = crear(en_carpeta, monkeypatch, "next-fullstack")
    (raiz / "prisma/migrations").mkdir()
    (raiz / "prisma/migrations/migration_lock.toml").write_text('provider = "sqlite"\n', encoding="utf-8")
    assert main(["base", "--url", "postgresql://u:c@localhost:5432/tienda"]) == 0
    assert "las migraciones de prisma/migrations son de sqlite" in capsys.readouterr().out


def test_prisma_con_una_conexion_cambiada_a_mano(en_carpeta, monkeypatch, capsys):
    raiz = crear(en_carpeta, monkeypatch, "express")
    (raiz / "src/db.ts").write_text("export const prisma = crearMiConexion();\n", encoding="utf-8")
    assert main(["base", "postgres", "--url", "postgresql://u:c@localhost:5432/tienda"]) == 0
    salida = capsys.readouterr().out
    assert "No se pudo modificar src/db.ts" in salida and "new PrismaPg({ connectionString: DATABASE_URL })" in salida
    assert leer(raiz / "src/db.ts") == "export const prisma = crearMiConexion();\n"


@pytest.mark.lento
@requiere_node
def test_express_con_cada_base_instala_y_compila(en_carpeta, monkeypatch):
    """Con PostgreSQL y MySQL: los adaptadores se instalan y el código compila (tsc). De vuelta
    en SQLite, npm test prepara la base con scripts/base-de-tests.js y pasa."""
    raiz = crear(en_carpeta, monkeypatch, "express")
    assert main(["nuevo", "recurso", "producto", "nombre", "precio:decimal"]) == 0
    assert main(["nuevo", "login"]) == 0
    for argumentos in (["--url", "postgresql://u:c@localhost:5432/tienda"], ["--url", "mysql://u:c@localhost:3306/tienda"]):
        assert main(["base", *argumentos]) == 0
        npm_install(raiz)
        ejecutar([NPM, "run", "tipos"], raiz)
    assert main(["base", "sqlite"]) == 0
    npm_install(raiz)
    resultado = ejecutar([NPM, "test"], raiz)
    assert "base-de-tests.js" in resultado.stdout
    pasaron, fallaron = resultado_de_node_test(resultado.stdout)
    assert pasaron > 10 and fallaron == 0, resultado.stdout[-3000:]
