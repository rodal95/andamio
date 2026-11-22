"""andamio base: conectar la API a PostgreSQL, MySQL o SQLite (con Docker si se pide)."""

import pytest
from dotenv import dotenv_values

from andamio import base_datos
from andamio.base_datos import leer_url
from andamio.cli import main
from andamio.nucleo.errores import AndamioError


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
    assert "# DATABASE_URL=postgres://usuario:clave@localhost:5432/mi_base" in ejemplo


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
    [("react", "lo hace la API"), ("express", "usa Prisma"), ("python", "no se conecta a otra base")],
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
