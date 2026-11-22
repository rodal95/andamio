"""Stack `express`: API REST con Express + Prisma (SQLite) + Zod, en TypeScript o JavaScript.

La API cumple el mismo "contrato" que las de Django y FastAPI (rutas /api/<plural>/,
lista como array, decimales como número, errores 400 {campo: [mensajes]}, 404,
204, ?search, ?ordering y filtros), así los servicios y el CRUD de React y React
Native funcionan igual con las tres. Escucha en el puerto 8000, como las otras.
"""

from __future__ import annotations

import re
import secrets
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from andamio.nucleo import consola, ejemplos
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack
from andamio.stacks.django import _VALORES_PRUEBA, TIPOS

# Tipo de cada campo en prisma/schema.prisma.
_PRISMA = {
    "str": "String",
    "text": "String",
    "int": "Int",
    "decimal": "Decimal",
    "float": "Float",
    "bool": "Boolean",
    "date": "DateTime",
    "datetime": "DateTime",
    "email": "String",
}

# Función de src/validacion con la que se valida cada tipo.
_ZOD = {
    "str": "texto",
    "text": "textoLargo",
    "int": "entero",
    "decimal": "decimal",
    "float": "numero",
    "bool": "booleano",
    "date": "fecha",
    "datetime": "fechaHora",
    "email": "correo",
}

_TEXTO = ("str", "text", "email")


def _literal(valor: object) -> str:
    """Un valor como se escribe en JavaScript: 'texto', 10.5, true."""
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, str):
        return "'" + valor.replace("\\", "\\\\").replace("'", "\\'") + "'"
    return repr(valor)


def _valor_prueba(tipo: str, indice: int) -> str:
    valor = _VALORES_PRUEBA[tipo][indice]
    return _literal(float(valor)) if tipo == "decimal" else _literal(valor)


def _modelo_prisma(sol: Solicitud) -> str:
    filas = [("id", "Int", "@id @default(autoincrement())")]
    filas += [(c.nombre, _PRISMA[c.tipo], "@default(false)" if c.tipo == "bool" else "") for c in sol.campos]
    filas += [("creado", "DateTime", "@default(now())"), ("actualizado", "DateTime", "@updatedAt")]
    ancho_nombre = max(len(n) for n, _, _ in filas)
    ancho_tipo = max(len(t) for _, t, _ in filas)
    lineas = [f"  {n:<{ancho_nombre}} {t:<{ancho_tipo}} {a}".rstrip() for n, t, a in filas]
    return "\n".join(
        [f"model {sol.nombre.pascal} {{", *lineas, "", f'  @@map("{sol.nombre.plural}")', "}", ""]
    )


def _busqueda(sol: Solicitud) -> str:
    campos = [c.nombre for c in sol.campos if c.tipo in _TEXTO]
    if not campos:
        return ""
    nota = "// Busca en los campos de texto (en SQLite no distingue mayúsculas, salvo en letras con tilde o ñ)."
    if len(campos) == 1:
        return f"{nota}\n...(search ? {{ {campos[0]}: {{ contains: search }} }} : {{}}),"
    opciones = "\n".join(f"        {{ {c}: {{ contains: search }} }}," for c in campos)
    return f"{nota}\n...(search\n  ? {{\n      OR: [\n{opciones}\n      ],\n    }}\n  : {{}}),"


def _json_campo(variable: str, nombre: str, tipo: str) -> str:
    valor = f"{variable}.{nombre}"
    if tipo == "decimal":
        valor += ".toNumber()"
    elif tipo == "date":
        valor = f"jsonFecha({valor})"
    elif tipo == "datetime":
        valor = f"jsonFechaHora({valor})"
    return f"{nombre}: {valor},"


def _verificacion(sol: Solicitud) -> str:
    campo = sol.campos[0]
    actual = f"res.datos.{campo.nombre}"
    if campo.tipo == "datetime":
        # Vuelve en hora local ("2025-02-20T15:45:00-03:00"): se compara el instante, no el texto.
        esperado = _literal(_VALORES_PRUEBA["datetime"][1])
        return f"assert.equal(new Date({actual}).getTime(), new Date({esperado}).getTime());"
    return f"assert.equal({actual}, {_valor_prueba(campo.tipo, 1)});"


def contexto_recurso(sol: Solicitud) -> dict[str, str]:
    campos = sol.campos
    variable = sol.nombre.camel
    tipos = {c.tipo for c in campos}
    booleanos = [c.nombre for c in campos if c.tipo == "bool"]
    if booleanos:
        # Como en Django: si no se envía un sí/no, se guarda "no" (false).
        por_defecto = ", ".join(f"{n}: campos.{n}.default(false)" for n in booleanos)
        esquema_crear = f"z.object({{ ...campos, {por_defecto} }})"
    else:
        esquema_crear = "z.object(campos)"
    return {
        "modelo_prisma": _modelo_prisma(sol),
        "import_fechas": "jsonFecha, jsonFechaHora" if "date" in tipos else "jsonFechaHora",
        "import_validacion": ", ".join(sorted({_ZOD[t] for t in tipos})),
        "campos_zod": "\n".join(f"{c.nombre}: {_ZOD[c.tipo]}()," for c in campos),
        "esquema_crear": esquema_crear,
        "filtros_zod": "\n".join(f"{c.nombre}: campos.{c.nombre}.optional()," for c in campos if c.tipo != "text"),
        "campos_orden": ", ".join(f"'{n}'" for n in ["id", *(c.nombre for c in campos), "creado", "actualizado"]),
        "campos_json": "\n".join(_json_campo(variable, c.nombre, c.tipo) for c in campos),
        "busqueda": _busqueda(sol),
        "datos_prueba": "\n".join(f"{c.nombre}: {_valor_prueba(c.tipo, 0)}," for c in campos),
        "datos_modificados": "\n".join(f"{c.nombre}: {_valor_prueba(c.tipo, 1)}," for c in campos),
        "verificacion": _verificacion(sol),
    }



def contexto_recurso_api(url_api: str) -> Callable[[Solicitud], dict[str, str]]:
    """El contexto del recurso, más el archivo http/<plural>.http con la dirección de la API."""

    def calcular(sol: Solicitud) -> dict[str, str]:
        return {**contexto_recurso(sol), **ejemplos.contexto_http(sol.campos, url_api, "npm run dev")}

    return calcular


# --- Validación de nombres -------------------------------------------------------------


def _leer(ruta: Path) -> str:
    try:
        return ruta.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return ""


def validar_nombre_recurso(carpeta: str, apps: tuple[str, ...] = ()) -> Callable[[Path, Nombre], None]:
    """Rechaza un recurso si choca con la carpeta del cliente de Prisma, con un modelo que
    ya existe en prisma/schema.prisma o con un router ya registrado en alguna de `apps`."""

    def validar(raiz: Path, nombre: Nombre) -> None:
        motivo = None
        if nombre.plural == "generated":
            motivo = f"es la carpeta del cliente de Prisma ({carpeta}/generated)" if carpeta == "src" else "es la carpeta del cliente de Prisma"
        elif re.search(rf"^\s*model\s+{re.escape(nombre.pascal)}\s*\{{", _leer(raiz / "prisma" / "schema.prisma"), re.M):
            motivo = f"ya existe el modelo {nombre.pascal} en prisma/schema.prisma"
        else:
            for app in apps:
                if f"./{nombre.plural}/router" in _leer(raiz / app):
                    motivo = f"ya está registrado en {app}"
        if motivo:
            raise AndamioError(
                f"No se puede crear el recurso '{nombre.plural}': {motivo}.", "Elegí otro nombre, o indicá otro plural con --plural."
            )

    return validar


def _campos_reservados(nombre: Nombre) -> dict[str, str]:
    return {
        "search": "lo usa la API para buscar (?search=)",
        "ordering": "lo usa la API para ordenar (?ordering=)",
    }


# --- Migración (--migrar) ----------------------------------------------------------------


def _migrar(sol: Solicitud) -> None:
    if not sol.opciones.get("migrar"):
        return
    comando = f"npx prisma migrate dev --name {sol.nombre.plural}"
    npx = shutil.which("npx")
    if npx is None:
        raise AndamioError(
            "Los archivos se generaron, pero no se pudo migrar: no encontré Node.js (el comando npx).",
            f"Instalá Node.js 22.12 o más nuevo, ejecutá npm install y después: {comando}",
        )
    if not (sol.raiz / "node_modules" / "prisma").is_dir():
        raise AndamioError(
            "Los archivos se generaron, pero no se pudo migrar: faltan las dependencias del proyecto.",
            f"Ejecutá npm install y después: {comando}",
        )
    consola.escribir()
    consola.titulo(f"Ejecutando: {comando}")
    resultado = subprocess.run([npx, "prisma", "migrate", "dev", "--name", sol.nombre.plural], cwd=sol.raiz)
    if resultado.returncode != 0:
        raise AndamioError(
            f"Falló '{comando}'. Los archivos del recurso se generaron igual.",
            f"Leé el error de arriba, corregilo y ejecutá de nuevo: {comando}",
        )
    sol.opciones["migrado"] = True


def pasos_recurso(siguientes: list[str]) -> Callable[[Solicitud], list[str]]:
    """La migración (si no se hizo con --migrar), los pasos indicados y cómo ejecutar los tests."""

    def calcular(sol: Solicitud) -> list[str]:
        pasos = [] if sol.opciones.get("migrado") else ["npx prisma migrate dev --name @@plural@@"]
        return [*pasos, *siguientes, "# Los tests del recurso se ejecutan con: npm test"]

    return calcular


# El modelo del recurso, al final de prisma/schema.prisma.
INSERCION_MODELO = Insercion(
    "prisma/schema.prisma",
    "@@modelo_prisma@@",
    marcador="modelos",
    descripcion="modelo @@Nombre@@ (tabla @@plural@@)",
    ubicacion="al final del archivo",
    comentario="//",
)


def _contexto_protegido(sol: Solicitud) -> dict[str, str]:
    """--protegido: crear, modificar y eliminar piden el token (ver es libre, como en Django)."""
    claves = ("import_login", "pide_login", "importar_before", "importar_usar_token", "tests_login")
    if not sol.opciones.get("protegido"):
        return dict.fromkeys(claves, "")
    carpeta = login_generado(sol.raiz)
    if carpeta is None:
        raise AndamioError(
            "--protegido pide el login, y este proyecto todavía no lo tiene.",
            "Generá primero el login: python -m andamio nuevo login",
        )
    ext = _js.MARCADORES_VARIANTE[sol.variante or "ts"]["ext"]
    usuario = f"prueba-{sol.nombre.kebab}"
    explicacion = ["// Crear, modificar y eliminar piden login (--protegido): los tests entran con un usuario."] if sol.guia else []
    tests = [
        "",
        "// --- Login (--protegido) ---------------------------------------------------------",
        *explicacion,
        "let token = '';",
        "",
        "before(async () => {",
        f"  const usuario = {{ username: '{usuario}', password: 'una-clave-larga-123' }};",
        "  await prisma.usuario.deleteMany({ where: { username: usuario.username } });",
        "  await api.post('/api/registro/', usuario);",
        "  token = (await api.post('/api/token/', usuario)).datos.access;",
        "  usarToken(token);",
        "});",
        "",
        "test('sin login no se puede crear', async () => {",
        "  usarToken(null);",
        "  try {",
        "    assert.equal((await api.post(URL, DATOS)).status, 401);",
        "    assert.equal((await api.get(URL)).status, 200); // ver es libre",
        "  } finally {",
        "    usarToken(token);",
        "  }",
        "});",
    ]
    return {
        "import_login": f"import {{ requiereSesion }} from '../{carpeta}/seguridad.{ext}';",
        "pide_login": "requiereSesion, ",
        "importar_before": "before, ",
        "importar_usar_token": ", usarToken",
        "tests_login": "\n".join(tests),
    }


def _contexto_recurso_express(sol: Solicitud) -> dict[str, str]:
    return {**contexto_recurso_api("http://localhost:8000/api")(sol), **_contexto_protegido(sol)}


RECURSO = Pieza(
    clave="recurso",
    lectura=(
        ('prisma/schema.prisma', 'el modelo @@Nombre@@ (la tabla), al final del archivo'),
        ('src/@@plural@@/esquema.@@ext@@', 'qué datos acepta la API (validación con Zod)'),
        ('src/@@plural@@/router.@@ext@@', 'la API: listar, crear, ver, modificar y eliminar'),
        ('tests/@@plural@@.test.@@ext@@', 'los tests: lo que la API tiene que cumplir'),
        ('http/@@plural@@.http', 'peticiones para probar la API a mano'),
    ),
    titulo="Recurso REST",
    descripcion="modelo de Prisma, validación, API (CRUD) y tests",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "ruta /api/@@plural@@/"),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"migrar", "protegido"}),
    contexto=_contexto_recurso_express,
    campos_reservados=_campos_reservados,
    marcadores={
        **_js.MARCADORES_EXTENSION,
        **ejemplos.MARCADORES_HTTP,
        "modelo_prisma": "el model completo para prisma/schema.prisma",
        "import_fechas": "funciones de src/fechas que usa el JSON (jsonFecha solo si hay fechas)",
        "import_validacion": "funciones de src/validacion que usan los campos",
        "campos_zod": "una línea por campo: nombre: texto(),",
        "esquema_crear": "el esquema de creación (los sí/no tienen false por defecto)",
        "filtros_zod": "un filtro opcional por campo, para ?campo=valor",
        "campos_orden": "campos para ?ordering=",
        "campos_json": "una línea por campo de aJson (los decimales y las fechas se convierten)",
        "busqueda": "la búsqueda en los campos de texto (?search=)",
        "datos_prueba": "datos de ejemplo para los tests: nombre: 'Texto de prueba',",
        "datos_modificados": "datos de ejemplo para el test de modificación",
        "verificacion": "lo que controla el test de modificación",
        "import_login": "con --protegido: el import de requiereSesion (del login)",
        "pide_login": "con --protegido: requiereSesion en crear, reemplazar, modificar y eliminar",
        "importar_before": "con --protegido: before, en el import de node:test",
        "importar_usar_token": "con --protegido: usarToken, en el import de ./api",
        "tests_login": "con --protegido: el usuario de los tests y el test del 401 sin login",
    },
    existe_si=("src/@@plural@@",),
    validar_nombre=validar_nombre_recurso("src", ("src/app.ts", "src/app.js")),
    inserciones=(
        INSERCION_MODELO,
        Insercion(
            "src/app.@@ext@@",
            "import { @@pluralCamel@@Docs, @@pluralCamel@@Router } from './@@plural@@/router.@@ext@@';",
            marcador="imports",
            descripcion="import del router",
            ubicacion="arriba, junto a los otros import",
            comentario="//",
        ),
        Insercion(
            "src/app.@@ext@@",
            "app.use('/api/@@plural@@', @@pluralCamel@@Router);",
            marcador="rutas",
            descripcion="rutas /api/@@plural@@/",
            ubicacion="después de app.use(express.json())",
            comentario="//",
        ),
        Insercion(
            "src/app.@@ext@@",
            "@@pluralCamel@@Docs,",
            marcador="docs",
            descripcion="documentación en /docs",
            ubicacion="dentro de la lista recursos",
            comentario="//",
        ),
    ),
    siguiente_paso=pasos_recurso(["npm run dev", "http://localhost:8000/docs"]),
    despues=_migrar,
    confirmaciones={"migrar": "¿Crear ahora la migración de la base de datos (npx prisma migrate dev)?"},
)


# --- Login con JWT (nuevo login): el mismo contrato que la API de Django ---------------

_MODELO_USUARIO = """model Usuario {
  id           Int     @id @default(autoincrement())
  username     String  @unique
  email        String  @default("")
  first_name   String  @default("")
  last_name    String  @default("")
  passwordHash String
  activo       Boolean @default(true)

  @@map("usuarios")
}
"""

_CONFIG_LOGIN = """
// --- Login con JWT (lo agregó: andamio nuevo login) ------------------------------
// Con esta clave se firman los tokens: si alguien la conoce, puede armar tokens válidos.
// Va en el .env (que no se sube a git); cambiala en cada instalación.
export const SECRET_KEY = process.env.SECRET_KEY || 'cambiar-por-una-clave-larga-y-secreta';"""


def login_generado(raiz: Path) -> str | None:
    """La carpeta del login (src/cuentas) si ya se generó, o None."""
    for archivo in ("src/app.ts", "src/app.js"):
        try:
            texto = (raiz / archivo).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        for linea in texto.splitlines():
            # import { cuentasRouter } from './cuentas/router.ts';  (lo agrega nuevo login)
            if linea.startswith("import {") and "/router." in linea and "Docs" not in linea:
                carpeta = linea.split("'./", 1)[1].split("/", 1)[0]
                if any((raiz / "src" / carpeta / f"seguridad.{ext}").is_file() for ext in ("ts", "js")):
                    return carpeta
    return None


def _validar_login(raiz: Path, nombre: Nombre) -> None:
    ya = login_generado(raiz)
    if ya:
        raise AndamioError(
            f"El proyecto ya tiene el login (src/{ya}/).",
            "Para que un recurso pida login al crear, modificar y eliminar: python -m andamio nuevo recurso <nombre> <campos> --protegido",
        )
    validar_nombre_recurso("src", ("src/app.ts", "src/app.js"))(raiz, nombre)


def _contexto_login(sol: Solicitud) -> dict[str, str]:
    return {"secret_key": secrets.token_urlsafe(48), "modelo_usuario": _MODELO_USUARIO}


def _pasos_login(sol: Solicitud) -> list[str]:
    pasos = [] if sol.opciones.get("migrado") else ["npx prisma migrate dev --name @@plural@@"]
    try:
        tiene_jose = '"jose"' in (sol.raiz / "package.json").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        tiene_jose = True
    if not tiene_jose:
        # Los proyectos creados antes no traen jose (la librería de los tokens).
        pasos.insert(0, "npm install jose@6.2.15")
    return [
        *pasos,
        "npm run dev",
        "# Registrate (POST /api/registro/) y pedí un token (POST /api/token/): http/login.http",
        "# Para que un recurso pida login al crear, modificar y eliminar: nuevo recurso ... --protegido",
        "# Los tests del login se ejecutan con: npm test",
    ]


LOGIN = Pieza(
    clave="login",
    lectura=(
        ("prisma/schema.prisma", "el modelo Usuario (la tabla), al final del archivo"),
        ("src/@@plural@@/seguridad.@@ext@@", "cómo se guardan las contraseñas (hash) y cómo se arman y se leen los tokens"),
        ("src/@@plural@@/esquema.@@ext@@", "qué datos piden el registro y el login"),
        ("src/@@plural@@/router.@@ext@@", "registrarse (/api/registro/), el token (/api/token/) y el usuario actual (/api/yo/)"),
        ("http/login.http", "peticiones para registrarse, pedir el token y usarlo"),
        ("tests/@@plural@@.test.@@ext@@", "los tests del login"),
    ),
    titulo="Login con JWT",
    descripcion="registro, token de acceso (JWT) y usuario actual, igual que la API de Django",
    ejemplo="",
    nombre_defecto="cuenta",
    pregunta_nombre="Nombre de la carpeta del login (Enter para cuenta)",
    formas=("src/@@plural@@",),
    opciones=frozenset({"migrar"}),
    validar_nombre=_validar_login,
    contexto=_contexto_login,
    marcadores={
        **_js.MARCADORES_EXTENSION,
        "secret_key": "una clave al azar para firmar los tokens (va al .env)",
        "modelo_usuario": "el model Usuario para prisma/schema.prisma",
    },
    existe_si=("src/@@plural@@",),
    inserciones=(
        Insercion(
            "prisma/schema.prisma", "@@modelo_usuario@@", marcador="modelos", descripcion="modelo Usuario (tabla usuarios)", ubicacion="al final del archivo", comentario="//"
        ),
        Insercion(
            "src/app.@@ext@@",
            "import { @@pluralCamel@@Router } from './@@plural@@/router.@@ext@@';",
            marcador="imports",
            descripcion="import del login",
            ubicacion="arriba, junto a los otros import",
            comentario="//",
        ),
        Insercion(
            "src/app.@@ext@@",
            "app.use('/api', @@pluralCamel@@Router);",
            marcador="rutas",
            descripcion="rutas /api/token/, /api/registro/ y /api/yo/",
            ubicacion="después de app.use(express.json())",
            comentario="//",
        ),
        Insercion("src/config.@@ext@@", _CONFIG_LOGIN, descripcion="SECRET_KEY (al final)"),
        Insercion(".env", "\n# Firma de los tokens del login (nuevo login). Es secreta: no la compartas.\nSECRET_KEY=@@secret_key@@", descripcion="SECRET_KEY", crear_si_falta=True),
        Insercion(".env.example", "\n# Firma de los tokens del login: en el .env, una clave larga y al azar.\nSECRET_KEY=cambiar-por-una-clave-larga-y-secreta", descripcion="SECRET_KEY de ejemplo", crear_si_falta=True),
    ),
    siguiente_paso=_pasos_login,
    despues=_migrar,
    confirmaciones={"migrar": "¿Crear ahora la migración de la base de datos (npx prisma migrate dev)?"},
)


STACK = Stack(
    clave="express",
    titulo="Express + Prisma",
    senal="package.json con express",
    detectar=_js.detectar_dependencias("express"),
    tipos=TIPOS,
    piezas={"recurso": RECURSO, "login": LOGIN},
    ejemplo_proyecto="mi-api",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:8000/docs"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_js.MARCADORES_VARIANTE,
)
