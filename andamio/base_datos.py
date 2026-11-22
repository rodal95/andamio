"""`andamio base`: conecta el proyecto a una base de datos (PostgreSQL, MySQL o SQLite).

Pide los datos según el motor (o toma la URL de conexión ya armada) y configura el
backend detectado:

- Django (API y con plantillas): DATABASE_URL en el .env (lo lee dj-database-url) y el driver.
- FastAPI: DATABASE_URL en el .env con el formato de SQLAlchemy y el driver.
- Reflex: REFLEX_DB_URL en el .env (Reflex la usa en lugar del db_url de rxconfig.py).

Con --docker, además genera docker-compose.yml con la base, con los mismos datos del .env:
la base se levanta con `docker compose up -d`.

Nunca se escribe una contraseña en un archivo que se sube a git: van solo al .env.
"""

from __future__ import annotations

import getpass
import re
import secrets
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from andamio import acciones
from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.plan import Plan
from andamio.stacks.base import Stack

COMPOSE = "docker-compose.yml"


@dataclass(frozen=True)
class Motor:
    clave: str
    titulo: str
    puerto: int
    usuario: str  # el usuario por defecto de una base que ya existe
    imagen: str  # la imagen de Docker


MOTORES = {
    "postgres": Motor("postgres", "PostgreSQL", 5432, "postgres", "postgres:17"),
    "mysql": Motor("mysql", "MySQL", 3306, "root", "mysql:8.4"),
    "sqlite": Motor("sqlite", "SQLite", 0, "", ""),
}

# Cómo se escribe el motor al principio de una URL: postgres://, mysql+pymysql://...
_ESQUEMAS = {"postgres": "postgres", "postgresql": "postgres", "mysql": "mysql", "mariadb": "mysql", "sqlite": "sqlite"}

_ALIAS_MOTOR = {"postgresql": "postgres", "pg": "postgres", "mariadb": "mysql"}


@dataclass(frozen=True)
class Backend:
    """Cómo se configura la base en un tipo de proyecto."""

    variable: str  # la variable del .env
    esquemas: dict[str, str]  # motor -> cómo empieza la URL
    drivers: dict[str, tuple[str, str]]  # motor -> (línea de requirements.txt, para qué)
    pasos: tuple[str, ...]  # después de instalar el driver y levantar la base
    defecto: str  # qué se usa sin la variable
    prisma: str = ""  # "express" o "next-fullstack": se configura Prisma (ver base_prisma.py)


_DRIVERS_SQLALCHEMY = {
    "postgres": ("psycopg[binary]~=3.3.9", "PostgreSQL"),
    "mysql": ("PyMySQL~=1.2.4", "MySQL"),
}

BACKENDS = {
    "django": Backend(
        variable="DATABASE_URL",
        esquemas={"postgres": "postgres", "mysql": "mysql"},
        # mysqlclient es el driver que Django recomienda (en Linux necesita: sudo apt install
        # pkg-config libmysqlclient-dev; en Windows se instala sin nada más).
        drivers={"postgres": ("psycopg[binary]~=3.3.9", "PostgreSQL"), "mysql": ("mysqlclient~=2.3.2", "MySQL")},
        pasos=("python manage.py migrate",),
        defecto="SQLite (db.sqlite3)",
    ),
    "fastapi": Backend(
        variable="DATABASE_URL",
        esquemas={"postgres": "postgresql+psycopg", "mysql": "mysql+pymysql"},
        drivers=_DRIVERS_SQLALCHEMY,
        pasos=("python -m uvicorn app.main:app --reload", "# al arrancar, la API crea las tablas que falten"),
        defecto="SQLite (datos.db)",
    ),
    "reflex": Backend(
        variable="REFLEX_DB_URL",
        esquemas={"postgres": "postgresql+psycopg", "mysql": "mysql+pymysql"},
        drivers=_DRIVERS_SQLALCHEMY,
        pasos=("reflex db migrate", "# si el proyecto todavía no tiene la carpeta alembic/: reflex db init"),
        defecto="SQLite (datos.db, el db_url de rxconfig.py)",
    ),
}
BACKENDS["django-web"] = BACKENDS["django"]

# Express y Next.js full stack: Prisma. Las URL son las que entiende Prisma (postgresql://, mysql://).
for _clave in ("express", "next-fullstack"):
    BACKENDS[_clave] = Backend(
        variable="DATABASE_URL",
        esquemas={"postgres": "postgresql", "mysql": "mysql"},
        drivers={},
        pasos=(),
        defecto="SQLite (datos.db)",
        prisma=_clave,
    )


@dataclass
class Conexion:
    motor: Motor
    host: str = "localhost"
    puerto: int = 0
    nombre: str = ""
    usuario: str = ""
    clave: str = ""
    opciones: str = ""  # lo que va después de ? en la URL (ej.: sslmode=require)

    def url(self, esquema: str) -> str:
        credenciales = quote(self.usuario, safe="")
        if self.clave:
            credenciales += ":" + quote(self.clave, safe="")
        host = f"[{self.host}]" if ":" in self.host else self.host
        url = f"{esquema}://{credenciales}@{host}:{self.puerto}/{quote(self.nombre, safe='')}"
        return url + (f"?{self.opciones}" if self.opciones else "")

    def oculta(self, esquema: str) -> str:
        """La URL sin la contraseña, para mostrarla en pantalla."""
        url = Conexion(self.motor, self.host, self.puerto, self.nombre, self.usuario, "", self.opciones).url(esquema)
        return url.replace("@", ":****@", 1) if self.clave else url


# --- Lectura y validación de los datos -----------------------------------------


def motor_por_clave(texto: str) -> Motor:
    clave = texto.strip().lower()
    clave = _ALIAS_MOTOR.get(clave, clave)
    if clave not in MOTORES:
        raise AndamioError(f"No conozco la base '{texto}'.", "Opciones: postgres, mysql o sqlite")
    return MOTORES[clave]


def leer_url(texto: str) -> Conexion:
    """Los datos de una URL como postgres://usuario:clave@host:5432/base?sslmode=require.

    La contraseña puede venir sin codificar (con #, @, / o espacios): el servidor es lo que
    sigue a la última @, así que se acepta igual.
    """
    ejemplo = "Ejemplo: postgres://usuario:clave@localhost:5432/mi_base"
    texto = texto.strip()
    encontrado = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*)://(.*)$", texto, re.DOTALL)
    esquema = encontrado.group(1).split("+", 1)[0].lower() if encontrado else ""
    if esquema not in _ESQUEMAS:
        raise AndamioError(
            f"La URL tiene que empezar con el tipo de base (postgres://, mysql://...), y empieza con '{texto[:20]}'.", ejemplo
        )
    motor = MOTORES[_ESQUEMAS[esquema]]
    if motor.clave == "sqlite":
        raise AndamioError("Para SQLite no hace falta una URL.", f"Escribí: {consola.programa()} base sqlite")
    resto = encontrado.group(2)
    credenciales, arroba, servidor = resto.rpartition("@")
    if not arroba:
        credenciales, servidor = "", resto
    servidor, _, opciones = servidor.partition("?")
    servidor, _, nombre = servidor.partition("/")
    usuario, _, clave = credenciales.partition(":")
    try:
        partes = urlsplit(f"//{servidor}")
        host, puerto = partes.hostname, partes.port
    except ValueError as e:
        raise AndamioError(f"La URL no es válida: {e}.", ejemplo) from None
    nombre = unquote(nombre.strip("/"))
    if not host or not nombre:
        raise AndamioError(
            "A la URL le falta el servidor o el nombre de la base.",
            "Tiene que ser como: postgres://usuario:clave@servidor:5432/nombre_de_la_base",
        )
    return Conexion(
        motor,
        host=host,
        puerto=puerto or motor.puerto,
        nombre=nombre,
        usuario=unquote(usuario) or motor.usuario,
        clave=unquote(clave),
        opciones=opciones,
    )


def _validar_puerto(texto: str) -> int:
    if not texto.strip().isdigit() or not 1 <= int(texto) <= 65535:
        raise AndamioError(f"El puerto tiene que ser un número del 1 al 65535, y es '{texto}'.")
    return int(texto)


def _validar_identificador(que: str):
    def validar(texto: str) -> str:
        texto = texto.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,62}", texto):
            raise AndamioError(
                f"El {que} '{texto}' no sirve: solo letras sin tilde, números y _ (y que no empiece con número).",
                "Ejemplo: mi_tienda",
            )
        return texto

    return validar


def nombre_sugerido(raiz: Path) -> str:
    """El nombre de la base a partir de la carpeta del proyecto: "Mi Tienda" -> mi_tienda."""
    import unicodedata

    texto = unicodedata.normalize("NFKD", raiz.name).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^A-Za-z0-9]+", "_", texto).strip("_").lower()
    if not texto or texto[0].isdigit():
        texto = "base_" + texto
    return texto[:63]


def puerto_en_uso(host: str, puerto: int, espera: float = 1.5) -> bool:
    """Si algo responde en host:puerto (una base en marcha, por ejemplo)."""
    try:
        with socket.create_connection((host, puerto), timeout=espera):
            return True
    except OSError:
        return False


# --- Cambios en los archivos ---------------------------------------------------


def _valor_env(valor: str) -> str:
    """El valor para el .env. Con caracteres raros va entre comillas simples: así ni
    python-dotenv ni Docker Compose interpretan $ o # dentro de la contraseña."""
    if re.fullmatch(r"[A-Za-z0-9_.:/@%+?=&\-\[\]]*", valor):
        return valor
    if "'" in valor or "\n" in valor:
        raise AndamioError("La contraseña no puede tener comillas simples (') ni saltos de línea.")
    return f"'{valor}'"


def fijar_variables(texto: str, valores: dict[str, str], comentario: str) -> str:
    """Cambia cada NOMBRE=... del .env; las que no están se agregan juntas al final,
    con un comentario arriba."""
    faltan = []
    for nombre, valor in valores.items():
        linea = f"{nombre}={_valor_env(valor)}"
        patron = re.compile(rf"^[ \t]*(export[ \t]+)?{re.escape(nombre)}[ \t]*=.*$", re.MULTILINE)
        if patron.search(texto):
            texto = patron.sub(lambda _, linea=linea: linea, texto, count=1)
        else:
            faltan.append(linea)
    if not faltan:
        return texto
    separador = "" if not texto or texto.endswith("\n") else "\n"
    return f"{texto}{separador}\n# {comentario}\n" + "\n".join(faltan) + "\n"


def fijar_variable(texto: str, nombre: str, valor: str, comentario: str) -> str:
    return fijar_variables(texto, {nombre: valor}, comentario)


def comentar_variable(texto: str, nombre: str) -> str:
    """NOMBRE=... pasa a ser # NOMBRE=... (vuelve el valor por defecto)."""
    patron = re.compile(rf"^([ \t]*(?:export[ \t]+)?{re.escape(nombre)}[ \t]*=.*)$", re.MULTILINE)
    return patron.sub(r"# \1", texto)


def compose(motor: Motor) -> str:
    cabecera = f"""# La base de datos para desarrollar, en Docker (la agregó: andamio base --docker).
#   Levantarla:   docker compose up -d
#   Ver si está:  docker compose ps
#   Pararla:      docker compose stop       (los datos quedan guardados)
#   Borrar todo:  docker compose down -v    (¡borra también los datos!)
# Los datos de conexión salen del .env: DB_NOMBRE, DB_USUARIO, DB_CLAVE y DB_PUERTO.
# Solo se puede usar desde esta PC (127.0.0.1): no queda abierta a la red.
"""
    if motor.clave == "postgres":
        return cabecera + f"""
services:
  base:
    image: {motor.imagen}
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${{DB_NOMBRE}}
      POSTGRES_USER: ${{DB_USUARIO}}
      POSTGRES_PASSWORD: ${{DB_CLAVE}}
    ports:
      - "127.0.0.1:${{DB_PUERTO}}:5432"
    volumes:
      - datos:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${{POSTGRES_USER}} -d $${{POSTGRES_DB}}"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  datos:
"""
    return cabecera + f"""
services:
  base:
    image: {motor.imagen}
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: ${{DB_NOMBRE}}
      MYSQL_USER: ${{DB_USUARIO}}
      MYSQL_PASSWORD: ${{DB_CLAVE}}
      MYSQL_ROOT_PASSWORD: ${{DB_CLAVE_ROOT}}
    ports:
      - "127.0.0.1:${{DB_PUERTO}}:3306"
    volumes:
      - datos:/var/lib/mysql
    configs:
      - source: permisos
        target: /docker-entrypoint-initdb.d/permisos.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "127.0.0.1", "--silent"]
      interval: 5s
      timeout: 5s
      retries: 20

# Al crear la base, el usuario recibe permiso para crear otras: Prisma (migrate dev) arma
# una base temporal para calcular las migraciones, y los tests usan su propia base.
configs:
  permisos:
    content: |
      GRANT ALL PRIVILEGES ON *.* TO '${{DB_USUARIO}}'@'%';

volumes:
  datos:
"""


# --- El comando ----------------------------------------------------------------


def _backend(stack: Stack) -> Backend:
    if stack.clave in BACKENDS:
        return BACKENDS[stack.clave]
    if stack.clave == "python":
        raise AndamioError(
            "El proyecto de Python con consola usa SQLite (sqlite3, que viene con Python): no se conecta a otra base.",
            "Para una base como PostgreSQL, creá una API: andamio crear django mi-api (o fastapi).",
        )
    raise AndamioError(
        f"Un proyecto {stack.titulo} no se conecta directo a una base de datos: lo hace la API (el backend).",
        "Entrá a la carpeta de tu API (Django, FastAPI, Express, Next.js full stack o Reflex) y ejecutá ahí: andamio base",
    )


def _preguntar(texto: str, defecto: str, validar=None):
    respuesta = consola.preguntar(f"{texto} (Enter para {defecto or 'dejarlo vacío'})", permitir_vacio=True)
    respuesta = respuesta or defecto
    return validar(respuesta) if validar else respuesta


def _preguntar_clave(texto: str) -> str:
    if sys.stdin.isatty():
        try:
            return getpass.getpass(f"{texto}: ")
        except EOFError:
            from andamio.nucleo.errores import Cancelado

            raise Cancelado() from None
    return consola.leer(f"{texto}: ")


def _puerto_libre(desde: int) -> int:
    puerto = desde
    while puerto_en_uso("127.0.0.1", puerto, espera=0.3) and puerto < desde + 20:
        puerto += 1
    return puerto


def _interactivo(raiz: Path) -> tuple[Conexion, bool]:
    """Pregunta el motor y los datos. Devuelve (conexión, con docker)."""
    motor = consola.elegir(
        "¿Qué base de datos vas a usar?",
        [
            (MOTORES["postgres"], "PostgreSQL (recomendada)"),
            (MOTORES["mysql"], "MySQL"),
            (MOTORES["sqlite"], "SQLite: volver a la base por defecto (un archivo, sin instalar nada)"),
        ],
    )
    if motor.clave == "sqlite":
        return Conexion(motor), False
    consola.escribir()
    donde = consola.elegir(
        f"¿Dónde está la base {motor.titulo}?",
        [
            ("docker", "Crearla en esta PC con Docker (recomendado para desarrollar)"),
            ("url", "Ya la tengo: pego la URL de conexión (la que da Railway, Render, Supabase...)"),
            ("datos", "Ya la tengo: escribo los datos (servidor, puerto, usuario...)"),
        ],
    )
    consola.escribir()
    if donde == "url":
        def validar(texto: str) -> Conexion:
            conexion = leer_url(texto)
            if conexion.motor != motor:
                raise AndamioError(f"Es una URL de {conexion.motor.titulo}, y elegiste {motor.titulo}.")
            return conexion

        return consola.preguntar("URL de conexión", validar, ejemplo=f"{motor.clave}://usuario:clave@servidor:{motor.puerto}/base"), False
    nombre = _preguntar("Nombre de la base", nombre_sugerido(raiz), _validar_identificador("nombre de la base"))
    if donde == "docker":
        puerto = _puerto_libre(motor.puerto)
        if puerto != motor.puerto:
            consola.aviso(f"El puerto {motor.puerto} ya está en uso en tu PC (¿otra base?): se sugiere el {puerto}.")
        puerto = _preguntar("Puerto en tu PC", str(puerto), _validar_puerto)
        usuario = _preguntar("Usuario", "app", _validar_identificador("usuario"))
        return Conexion(motor, "localhost", puerto, nombre, usuario, secrets.token_urlsafe(18)), True
    host = _preguntar("Servidor (host)", "localhost")
    puerto = _preguntar("Puerto", str(motor.puerto), _validar_puerto)
    usuario = _preguntar("Usuario", motor.usuario)
    clave = _preguntar_clave("Contraseña (no se muestra al escribir)")
    return Conexion(motor, host, puerto, nombre, usuario, clave), False


def _desde_opciones(raiz: Path, opciones: dict) -> tuple[Conexion, bool]:
    docker = bool(opciones.get("docker"))
    if opciones.get("url"):
        if docker:
            raise AndamioError("--docker crea una base nueva: no se usa con --url (que es de una base que ya existe).")
        conexion = leer_url(opciones["url"])
        if opciones.get("motor") and motor_por_clave(opciones["motor"]) != conexion.motor:
            raise AndamioError(f"La URL es de {conexion.motor.titulo}, y --motor dice {opciones['motor']}.")
        return conexion, False
    motor = motor_por_clave(opciones["motor"])
    if motor.clave == "sqlite":
        if docker:
            raise AndamioError("SQLite es un archivo: no necesita Docker.")
        return Conexion(motor), False
    puerto = _validar_puerto(str(opciones["puerto"])) if opciones.get("puerto") else motor.puerto
    nombre = _validar_identificador("nombre de la base")(opciones.get("nombre") or nombre_sugerido(raiz))
    if docker:
        usuario = _validar_identificador("usuario")(opciones.get("usuario") or "app")
        if motor.clave == "mysql" and usuario == "root":
            raise AndamioError("En la base de Docker, el usuario no puede ser root (MySQL ya lo crea aparte).", "Usá otro, o dejalo vacío para usar app")
        clave = opciones.get("clave") or secrets.token_urlsafe(18)
        return Conexion(motor, "localhost", puerto, nombre, usuario, clave), True
    return Conexion(
        motor,
        opciones.get("host") or "localhost",
        puerto,
        nombre,
        opciones.get("usuario") or motor.usuario,
        opciones.get("clave") or "",
    ), False


def _leer_env(raiz: Path, nombre: str) -> str | None:
    try:
        texto = (raiz / ".env").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None
    encontrado = re.search(rf"^[ \t]*{re.escape(nombre)}[ \t]*=[ \t]*'?([^'\n]*)'?[ \t]*$", texto, re.MULTILINE)
    return encontrado.group(1) if encontrado else None


def conexion_de_tests(conexion: Conexion) -> Conexion:
    """La base para los tests: otra en el mismo servidor, con el mismo usuario (los tests
    vacían las tablas que usan). En la base de Docker, el usuario puede crear bases."""
    return Conexion(conexion.motor, conexion.host, conexion.puerto, f"{conexion.nombre}_test", conexion.usuario, conexion.clave, conexion.opciones)


def planificar(raiz: Path, backend: Backend, conexion: Conexion, docker: bool) -> tuple[Plan, list[str]]:
    plan = Plan(raiz)
    pasos: list[str] = []
    motor = conexion.motor
    if not (raiz / ".env").exists() and (raiz / ".env.example").exists():
        raise AndamioError("Falta el archivo .env.", "Copiá .env.example con el nombre .env y volvé a ejecutar el comando.")
    if motor.clave == "sqlite":
        if backend.prisma:
            from andamio import base_prisma

            return plan, base_prisma.planificar(plan, raiz, backend.prisma, conexion, None, docker)
        plan.modificar(".env", lambda t: comentar_variable(t, backend.variable), f"sin {backend.variable}: vuelve a {backend.defecto}")
        return plan, pasos

    url = conexion.url(backend.esquemas[motor.clave])
    comentario = f"Base de datos {motor.titulo} (andamio base). Es privada: no la compartas."
    valores = {backend.variable: url}
    test = conexion_de_tests(conexion) if backend.prisma else None
    if test is not None:
        valores["TEST_DATABASE_URL"] = test.url(backend.esquemas[motor.clave])

    def cambiar_env(texto: str) -> str:
        if docker:
            docker_env = {"DB_NOMBRE": conexion.nombre, "DB_USUARIO": conexion.usuario, "DB_CLAVE": conexion.clave, "DB_PUERTO": str(conexion.puerto)}
            if motor.clave == "mysql":
                docker_env["DB_CLAVE_ROOT"] = _leer_env(raiz, "DB_CLAVE_ROOT") or secrets.token_urlsafe(18)
            texto = fijar_variables(texto, docker_env, "La base de Docker (docker-compose.yml) se crea con estos datos.")
        texto = fijar_variables(texto, valores, comentario)
        return texto

    if not plan.modificar(".env", cambiar_env, ", ".join(valores)):
        plan.crear(".env", cambiar_env(""))

    def cambiar_ejemplo(texto: str) -> str:
        # En .env.example va un ejemplo sin datos reales: se sube a git.
        if docker:
            # Los mismos datos que el compose (con la contraseña de ejemplo): copiando
            # .env.example a .env y cambiando la contraseña, todo coincide.
            ejemplo = Conexion(motor, "localhost", conexion.puerto, conexion.nombre, conexion.usuario, "cambiar-por-una-clave").url(backend.esquemas[motor.clave])
        else:
            ejemplo = Conexion(motor, "localhost", motor.puerto, "mi_base", "usuario", "clave").url(backend.esquemas[motor.clave])
        if docker:
            docker_env = {"DB_NOMBRE": conexion.nombre, "DB_USUARIO": conexion.usuario, "DB_CLAVE": "cambiar-por-una-clave", "DB_PUERTO": str(conexion.puerto)}
            if motor.clave == "mysql":
                docker_env["DB_CLAVE_ROOT"] = "cambiar-por-otra-clave"
            texto = fijar_variables(texto, docker_env, "La base de Docker (docker-compose.yml) se crea con estos datos.")
        lineas = {backend.variable: ejemplo}
        if test is not None:
            base_ejemplo = ejemplo.rsplit("/", 1)
            lineas["TEST_DATABASE_URL"] = f"{base_ejemplo[0]}/{base_ejemplo[1].split('?')[0]}_test"
        for variable, valor in lineas.items():
            # Con Prisma no hay un valor por defecto que sirva: la variable queda activa.
            linea = f"{variable}={valor}" if backend.prisma else f"# {variable}={valor}"
            patron = re.compile(rf"^#?[ \t]*{variable}[ \t]*=.*$", re.MULTILINE)
            if patron.search(texto):
                texto = patron.sub(lambda _, linea=linea: linea, texto, count=1)
            else:
                separador = "" if not texto or texto.endswith("\n") else "\n"
                texto = f"{texto}{separador}\n# Base de datos {motor.titulo} (andamio base). El valor real va en el .env.\n{linea}\n"
        return texto

    plan.modificar(".env.example", cambiar_ejemplo, f"ejemplo de {backend.variable}")
    if docker:
        plan.crear(COMPOSE, compose(motor))

    if backend.prisma:
        from andamio import base_prisma

        pasos_prisma = base_prisma.planificar(plan, raiz, backend.prisma, conexion, test, docker)
        if docker:
            pasos_prisma[1:1] = ["docker compose up -d", "# la primera vez descarga la imagen; esperá a que docker compose ps diga (healthy)"]
        return plan, pasos_prisma

    driver, para = backend.drivers[motor.clave]
    paquete = re.split(r"[~=<>\[]", driver, maxsplit=1)[0].lower()
    if (raiz / "requirements.txt").exists():
        actual = (raiz / "requirements.txt").read_text(encoding="utf-8-sig").lower()
        if not re.search(rf"^{re.escape(paquete)}\b", actual, re.MULTILINE):
            plan.insertar("requirements.txt", f"\n# Driver de {para} (andamio base).\n{driver}", descripcion=f"driver de {para}")

    pasos.append("pip install -r requirements.txt")
    if motor.clave == "mysql" and paquete == "mysqlclient":
        pasos.append("# en Linux, mysqlclient necesita antes: sudo apt install pkg-config libmysqlclient-dev")
    if docker:
        pasos += ["docker compose up -d", "# la primera vez descarga la imagen; esperá a que docker compose ps diga (healthy)"]
    pasos += list(backend.pasos)
    return plan, pasos


def base(cwd: Path, opciones: dict, simular: bool = False) -> int:
    stack, raiz = acciones.proyecto_actual(cwd)
    backend = _backend(stack)
    interactivo = not opciones.get("motor") and not opciones.get("url")
    conexion, docker = _interactivo(raiz) if interactivo else _desde_opciones(raiz, opciones)
    if docker and ((raiz / COMPOSE).exists() or (raiz / "compose.yaml").exists() or (raiz / "compose.yml").exists()):
        raise AndamioError(
            "El proyecto ya tiene un archivo de Docker Compose: no lo sobrescribo.",
            "Agregale la base a mano, o conectate a una que ya exista con: andamio base --url <url>",
        )
    plan, pasos = planificar(raiz, backend, conexion, docker)

    consola.escribir()
    consola.escribir(f"Proyecto {stack.titulo} en {consola.color(str(raiz), 'negrita')}")
    if conexion.motor.clave == "sqlite":
        consola.escribir(f"Base de datos: {consola.color(backend.defecto, 'negrita')}")
    else:
        destino = "en Docker" if docker else f"en {conexion.host}:{conexion.puerto}"
        consola.escribir(f"Base de datos: {consola.color(conexion.motor.titulo, 'negrita')} {destino}")
        consola.escribir(f"Conexión: {conexion.oculta(backend.esquemas[conexion.motor.clave])}")

    if not acciones._cerrar(plan, simular, interactivo, "¿Hacer los cambios?"):
        return 0
    if conexion.motor.clave != "sqlite":
        consola.escribir()
        if docker:
            if puerto_en_uso("127.0.0.1", conexion.puerto, espera=0.5):
                consola.aviso(
                    f"Ya hay algo escuchando en el puerto {conexion.puerto}: si no es esta base, docker compose up va a fallar. "
                    f"Cambiá DB_PUERTO y el puerto de {backend.variable} en el .env."
                )
        elif puerto_en_uso(conexion.host, conexion.puerto):
            consola.exito(f"La base responde en {conexion.host}:{conexion.puerto}.")
        else:
            consola.aviso(
                f"No responde nada en {conexion.host}:{conexion.puerto}. ¿Está en marcha la base? "
                "¿Son correctos el servidor y el puerto? (la configuración quedó guardada igual)"
            )
    acciones.mostrar_pasos(pasos)
    return 0
