"""`andamio base` en los proyectos con Prisma (Express y Next.js full stack).

Cambiar de SQLite a PostgreSQL o MySQL (o volver) no es solo la URL:

- prisma/schema.prisma: el `provider` del datasource.
- src/db (Express) o lib/db (Next.js): el adaptador de Prisma 7 (better-sqlite3, pg o mariadb).
- package.json: la dependencia del adaptador y `pretest`, que prepara la base de los tests.
- scripts/base-de-tests.js: prepara la base de los tests (TEST_DATABASE_URL), que es otra
  base del mismo servidor: los tests vacían las tablas que usan.
- tests/: usan TEST_DATABASE_URL en lugar de test.db (los proyectos de antes se adaptan).
- prisma/migrations: son SQL del motor anterior; se avisa que hay que crearlas de nuevo.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from andamio.nucleo.plan import Manual, Plan

if TYPE_CHECKING:
    from andamio.base_datos import Conexion


@dataclass(frozen=True)
class Adaptador:
    paquete: str
    clase: str
    provider: str  # el de schema.prisma


ADAPTADORES = {
    "sqlite": Adaptador("@prisma/adapter-better-sqlite3", "PrismaBetterSqlite3", "sqlite"),
    "postgres": Adaptador("@prisma/adapter-pg", "PrismaPg", "postgresql"),
    "mysql": Adaptador("@prisma/adapter-mariadb", "PrismaMariaDb", "mysql"),
}
_TITULOS = {"sqlite": "SQLite", "postgres": "PostgreSQL", "mysql": "MySQL"}


@dataclass(frozen=True)
class Proyecto:
    db: tuple[str, ...]  # el archivo de la conexión (el primero que exista)
    url: str  # cómo se lee la URL en ese archivo
    url_sqlite: str  # lo mismo, con SQLite (con su valor por defecto)
    tests: tuple[str, ...]


PROYECTOS = {
    "express": Proyecto(
        db=("src/db.ts", "src/db.js"),
        url="DATABASE_URL",
        url_sqlite="DATABASE_URL",
        tests=("tests/api.ts", "tests/api.js"),
    ),
    "next-fullstack": Proyecto(
        db=("lib/db.ts", "lib/db.js"),
        url="process.env.DATABASE_URL",
        url_sqlite="process.env.DATABASE_URL || 'file:./datos.db'",
        tests=("tests/api.ts", "tests/api.js", "tests/login.test.ts", "tests/login.test.js"),
    ),
}

PRETEST_SQLITE = (
    "node --eval \"require('node:fs').rmSync('test.db', { force: true })\" && prisma generate && prisma db push --url file:./test.db"
)
PRETEST = "prisma generate && node scripts/base-de-tests.js"

SCRIPT_TESTS = """// Lo ejecuta npm test antes de empezar (pretest), y lo agregó: andamio base.
// Prepara la base de los tests (TEST_DATABASE_URL del .env) con las tablas de
// prisma/schema.prisma. Es otra base, no la tuya: cada test vacía las tablas que usa.
import { execSync } from 'node:child_process';
import { rmSync } from 'node:fs';

try {
  process.loadEnvFile();
} catch {
  // Sin .env: SQLite, con test.db.
}
const url = process.env.TEST_DATABASE_URL || 'file:./test.db';
if (url === process.env.DATABASE_URL) {
  console.error('TEST_DATABASE_URL tiene que ser otra base, no la de DATABASE_URL: los tests borran los datos.');
  process.exit(1);
}
if (url.startsWith('file:')) {
  rmSync(url.slice('file:'.length), { force: true });
}
// DATABASE_URL es la que usa prisma.config: para este comando, la de los tests. Crea las
// tablas que falten (si un cambio borraría datos, Prisma lo avisa y no hace nada).
execSync('npx prisma db push', { stdio: 'inherit', env: { ...process.env, DATABASE_URL: url } });
"""

# La línea de los tests de antes, que usaba test.db fijo.
_TEST_VIEJO = re.compile(r"process\.env\.DATABASE_URL = 'file:\./test\.db';")
TEST_NUEVO = "process.env.DATABASE_URL = process.env.TEST_DATABASE_URL || 'file:./test.db';"
_CONTROL_VIEJO = "if (DATABASE_URL !== 'file:./test.db') {"
CONTROL_NUEVO = "if (DATABASE_URL !== (process.env.TEST_DATABASE_URL || 'file:./test.db')) {"
_CARGAR_ENV = """try {
  process.loadEnvFile(); // TEST_DATABASE_URL: la base de los tests
} catch {
  // sin .env
}
"""


def _primero(raiz: Path, rutas: tuple[str, ...]) -> str | None:
    return next((r for r in rutas if (raiz / r).is_file()), None)


def _cambiar_provider(motor: str):
    def cambiar(texto: str) -> str:
        return re.sub(
            r"(datasource\s+\w+\s*\{[^}]*?provider\s*=\s*)\"\w+\"",
            lambda m: f'{m.group(1)}"{ADAPTADORES[motor].provider}"',
            texto,
            count=1,
        )

    return cambiar


def _constructor(motor: str, url: str) -> str:
    adaptador = ADAPTADORES[motor]
    if motor == "sqlite":
        return f"new {adaptador.clase}({{ url: {url} }})"
    if motor == "postgres":
        return f"new {adaptador.clase}({{ connectionString: {url} }})"
    # El driver de MySQL (mariadb) pide la URL con mariadb:// en lugar de mysql://.
    return f"new {adaptador.clase}(String({url}).replace(/^mysql:/, 'mariadb:'))"


_CLASES = "|".join(a.clase for a in ADAPTADORES.values())
_IMPORT = re.compile(rf"import \{{ (?:{_CLASES}) \}} from '@prisma/adapter-[a-z0-9-]+';")
_NEW = re.compile(rf"new (?:{_CLASES})\((?:[^()]|\([^()]*\))*\)")
_DOC = re.compile(r"con Prisma \((?:SQLite|PostgreSQL|MySQL)\)")


def cambiar_db(texto: str, motor: str, proyecto: Proyecto) -> str | None:
    """El archivo de la conexión con el adaptador del motor, o None si no tiene la forma conocida."""
    if not _IMPORT.search(texto) or len(_NEW.findall(texto)) != 1:
        return None
    adaptador = ADAPTADORES[motor]
    texto = _IMPORT.sub(lambda _: f"import {{ {adaptador.clase} }} from '{adaptador.paquete}';", texto, count=1)
    url = proyecto.url_sqlite if motor == "sqlite" else proyecto.url
    texto = _NEW.sub(lambda _: _constructor(motor, url), texto, count=1)
    return _DOC.sub(f"con Prisma ({_TITULOS[motor]})", texto, count=1)


def cambiar_package(texto: str, motor: str) -> str:
    datos = json.loads(texto)
    dependencias = datos.setdefault("dependencies", {})
    version = dependencias.get("@prisma/client") or datos.get("devDependencies", {}).get("prisma") or "7.10.1"
    for adaptador in ADAPTADORES.values():
        dependencias.pop(adaptador.paquete, None)
    dependencias[ADAPTADORES[motor].paquete] = version
    datos["dependencies"] = dict(sorted(dependencias.items()))
    scripts = datos.setdefault("scripts", {})
    if scripts.get("pretest") in (PRETEST_SQLITE, None):
        scripts["pretest"] = PRETEST
    return json.dumps(datos, indent=2, ensure_ascii=False) + "\n"


def cambiar_test(texto: str) -> str:
    if TEST_NUEVO in texto:
        return texto
    texto = texto.replace(_CONTROL_VIEJO, CONTROL_NUEVO)
    if "process.loadEnvFile()" not in texto.split("process.env.DATABASE_URL", 1)[0]:
        texto = _TEST_VIEJO.sub(lambda _: _CARGAR_ENV + TEST_NUEVO, texto, count=1)
    else:
        texto = _TEST_VIEJO.sub(lambda _: TEST_NUEVO, texto, count=1)
    return texto


def provider_de_las_migraciones(raiz: Path) -> str | None:
    try:
        texto = (raiz / "prisma/migrations/migration_lock.toml").read_text(encoding="utf-8")
    except OSError:
        return None
    encontrado = re.search(r'provider\s*=\s*"(\w+)"', texto)
    return encontrado.group(1) if encontrado else None


def planificar(plan: Plan, raiz: Path, clave: str, conexion: Conexion, test: Conexion | None, docker: bool) -> list[str]:
    """Agrega al plan los cambios de Prisma. Devuelve los pasos siguientes."""
    proyecto = PROYECTOS[clave]
    motor = conexion.motor.clave
    titulo = _TITULOS[motor]

    if motor == "sqlite":
        def env_sqlite(texto: str) -> str:
            from andamio.base_datos import fijar_variables

            return fijar_variables(
                texto, {"DATABASE_URL": "file:./datos.db", "TEST_DATABASE_URL": "file:./test.db"}, "Base de datos SQLite (andamio base)."
            )

        plan.modificar(".env", env_sqlite, "DATABASE_URL y TEST_DATABASE_URL con SQLite")

    plan.modificar("prisma/schema.prisma", _cambiar_provider(motor), f'provider = "{ADAPTADORES[motor].provider}"')

    archivo_db = _primero(raiz, proyecto.db)
    if archivo_db:
        nuevo = cambiar_db((raiz / archivo_db).read_text(encoding="utf-8-sig"), motor, proyecto)
        if nuevo is None:
            plan.manuales.append(
                Manual(
                    raiz / archivo_db,
                    f"import {{ {ADAPTADORES[motor].clase} }} from '{ADAPTADORES[motor].paquete}';\n"
                    f"// ...\nnew PrismaClient({{ adapter: {_constructor(motor, proyecto.url_sqlite if motor == 'sqlite' else proyecto.url)} }})",
                    "no tiene la forma que andamio conoce",
                    "en lugar del adaptador que usa ahora (el import y el new Prisma...)",
                )
            )
        else:
            plan.modificar(archivo_db, lambda _: nuevo, f"adaptador de {titulo}")

    plan.modificar("package.json", lambda t: cambiar_package(t, motor), f"{ADAPTADORES[motor].paquete} y pretest")
    plan.crear("scripts/base-de-tests.js", SCRIPT_TESTS, si_no_existe=True)
    for archivo in proyecto.tests:
        if (raiz / archivo).is_file():
            plan.modificar(archivo, cambiar_test, "usa TEST_DATABASE_URL")

    pasos = ["npm install"]
    anterior = provider_de_las_migraciones(raiz)
    if anterior and anterior != ADAPTADORES[motor].provider:
        pasos += [
            f"# las migraciones de prisma/migrations son de {anterior}: no sirven para {titulo}.",
            "# Si no necesitás los datos de antes, borrá la carpeta prisma/migrations y creá una nueva:",
        ]
    pasos += ["npx prisma migrate dev --name inicial", "npm test", "# los tests usan otra base (TEST_DATABASE_URL), no la tuya"]
    return pasos
