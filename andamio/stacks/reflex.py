"""Stack `reflex`: aplicación web hecha solo con Python, con Reflex.

Las páginas y su estado se escriben en Python. Sirve de las dos formas:
- `crud`: con su propia base de datos (SQLModel + migraciones con Alembic).
- `crud-api` y `servicio`: usando una API hecha con andamio (Django, FastAPI o Express).
"""

from __future__ import annotations

import keyword
import os
import re
import subprocess
import sys
from pathlib import Path

from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.estilos import contexto_tema_reflex, pieza_tema
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack
from andamio.stacks.django import TIPOS, python_del_proyecto
from andamio.stacks.fastapi import _ATRIBUTOS_DE_SQLMODEL, _CAMPO_BASE

# Nombres que el paquete de la aplicación no puede tener: taparían a una librería.
# "assets" es la carpeta pública de Reflex: el paquete quedaría adentro.
_PAQUETES_OCUPADOS = {"reflex", "rxconfig", "alembic", "sqlmodel", "sqlalchemy", "pydantic", "httpx", "tests", "assets"}


def _detectar(raiz: Path) -> bool:
    return (raiz / "rxconfig.py").is_file()


def nombre_app(raiz: Path) -> str:
    """El paquete de la aplicación, según app_name en rxconfig.py."""
    try:
        texto = (raiz / "rxconfig.py").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        texto = ""
    encontrado = re.search(r"""app_name\s*=\s*["']([A-Za-z_]\w*)["']""", texto)
    if not encontrado:
        raise AndamioError(
            "No encontré app_name en rxconfig.py.",
            'Revisá que rxconfig.py tenga la línea: app_name="nombre_de_tu_app"',
        )
    return encontrado.group(1)


def _con_app(contexto=None):
    """Agrega el marcador @@app@@ (el paquete de la aplicación) al contexto de la pieza."""

    def calcular(sol: Solicitud) -> dict[str, str]:
        return {"app": nombre_app(sol.raiz), **(contexto(sol) if contexto else {})}

    return calcular


# --- Campos ----------------------------------------------------------------------------

_ENTRADAS = {
    "str": {},
    "email": {"type": "email"},
    "int": {"type": "number", "step": "1"},
    "decimal": {"type": "number", "step": "0.01"},
    "float": {"type": "number", "step": "any"},
    "date": {"type": "date"},
    "datetime": {"type": "datetime-local"},
}


def _control(estado: str, campo) -> str:
    n = campo.nombre
    cambiar = f'on_change=lambda valor: {estado}.cambiar("{n}", valor),'
    if campo.tipo == "bool":
        return f'rx.checkbox(\n    id="{n}",\n    checked={estado}.datos["{n}"].to(bool),\n    {cambiar}\n)'
    if campo.tipo == "text":
        return f'rx.text_area(\n    id="{n}",\n    value={estado}.datos["{n}"].to(str),\n    {cambiar}\n)'
    atributos = "".join(f'\n    {k}="{v}",' for k, v in _ENTRADAS[campo.tipo].items())
    return f'rx.input(\n    id="{n}",{atributos}\n    value={estado}.datos["{n}"].to(str),\n    {cambiar}\n)'


def _campos_formulario(sol: Solicitud) -> str:
    estado = f"{sol.nombre.pascal}State"
    bloques = []
    for c in sol.campos:
        control = _control(estado, c).replace("\n", "\n    ")
        bloques.append(f'campo(\n    "{c.titulo}",\n    "{c.nombre}",\n    {control},\n),')
    return "\n".join(bloques)


def _desde_modelo(variable: str, c) -> str:
    valor = f"{variable}.{c.nombre}"
    if c.tipo in ("int", "decimal", "float"):
        valor = f"str({valor})"
    elif c.tipo == "date":
        valor = f"{valor}.isoformat()"
    elif c.tipo == "datetime":
        valor = f'{valor}.astimezone().strftime("%Y-%m-%dT%H:%M")'
    return f'"{c.nombre}": {valor},'


def _desde_api(variable: str, c) -> str:
    valor = f'{variable}["{c.nombre}"]'
    if c.tipo in ("int", "decimal", "float"):
        valor = f"str({valor})"
    elif c.tipo == "datetime":
        valor += "[:16]"  # "2026-11-19T10:30:00-03:00" -> "2026-11-19T10:30" (hora local)
    return f'"{c.nombre}": {valor},'


def _contexto_pantalla(sol: Solicitud, desde) -> dict[str, str]:
    campos = sol.campos
    return {
        "valores_vacios": "\n".join(f'"{c.nombre}": {"False" if c.tipo == "bool" else chr(34) * 2},' for c in campos),
        "campos_a_formulario": "\n".join(desde(sol.nombre.snake, c) for c in campos),
        "campos_formulario": _campos_formulario(sol),
        "encabezados": "\n".join(f'rx.table.column_header_cell("{c.titulo}"),' for c in campos),
        "celdas": "\n".join(
            f'rx.table.cell(rx.cond(elemento["{c.nombre}"], "Sí", "No")),' if c.tipo == "bool" else f'rx.table.cell(elemento["{c.nombre}"]),'
            for c in campos
        ),
    }


def _contexto_crud(sol: Solicitud) -> dict[str, str]:
    tipos = {c.tipo for c in sol.campos}
    stdlib = ["from datetime import UTC, date, datetime" if "date" in tipos else "from datetime import UTC, datetime"]
    if "decimal" in tipos:
        stdlib.append("from decimal import Decimal")
    terceros = []
    if "email" in tipos:
        terceros.append("from pydantic import EmailStr")
    if "text" in tipos:
        terceros.append("from sqlalchemy import Text")
    app = nombre_app(sol.raiz)
    return {
        **_contexto_pantalla(sol, _desde_modelo),
        "imports_modelo": "\n".join(stdlib) + "\n" + ("\n" + "\n".join(terceros) if terceros else ""),
        "import_validacion": f"from {app}.validacion import FechaHora" if "datetime" in tipos else "",
        "campos_base": "\n".join(f"{c.nombre}: {_CAMPO_BASE[c.tipo]}" for c in sol.campos),
    }


def _contexto_crud_api(sol: Solicitud) -> dict[str, str]:
    return {**_contexto_pantalla(sol, _desde_api), **_contexto_servicio(sol)}


def _contexto_crud_api_validado(sol: Solicitud) -> dict[str, str]:
    _validar_servicio_completo(sol)
    return _contexto_crud_api(sol)


def _contexto_servicio(sol: Solicitud) -> dict[str, str]:
    return {"campos_doc": "\n".join(f"    {c.nombre}: {TIPOS[c.tipo]}" for c in sol.campos)}


def _campos_reservados(nombre: Nombre) -> dict[str, str]:
    return {n: "es un nombre que usa SQLModel en los modelos" for n in _ATRIBUTOS_DE_SQLMODEL}


_MARCADORES_PANTALLA = {
    "app": "el paquete de la aplicación (app_name de rxconfig.py)",
    "valores_vacios": 'lo que tiene el formulario vacío: "nombre": "",',
    "campos_a_formulario": "pasa un registro a los valores del formulario y de la tabla",
    "campos_formulario": "un campo(...) por campo del formulario, con su control según el tipo",
    "encabezados": "un encabezado de la tabla por campo",
    "celdas": "una celda de la tabla por campo",
}


# --- Migraciones (--migrar) ---------------------------------------------------------------


def _comandos_migracion(sol: Solicitud) -> list[list[str]]:
    if not (sol.raiz / "alembic").is_dir():
        return [["db", "init"]]  # la primera vez: crea las migraciones y las aplica
    return [["db", "makemigrations", "--message", sol.nombre.plural], ["db", "migrate"]]


def _migrar(sol: Solicitud) -> None:
    if not sol.opciones.get("migrar"):
        return
    python = python_del_proyecto(sol.raiz)
    activar = r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate"
    comandos = _comandos_migracion(sol)
    if subprocess.run([python, "-c", "import reflex, sqlmodel"], cwd=sol.raiz, capture_output=True).returncode != 0:
        raise AndamioError(
            f"Los archivos se generaron, pero no se pudo migrar: falta instalar Reflex en {python}.",
            f"Activá el entorno virtual ({activar}), instalá las dependencias (pip install -r requirements.txt) "
            f"y ejecutá: reflex {' '.join(comandos[0])}",
        )
    for argumentos in comandos:
        comando = "reflex " + " ".join(argumentos)
        consola.escribir()
        consola.titulo(f"Ejecutando: {comando}")
        if subprocess.run([python, "-m", "reflex", *argumentos], cwd=sol.raiz).returncode != 0:
            raise AndamioError(
                f"Falló '{comando}'. Los archivos se generaron igual.",
                f"Leé el error de arriba, corregilo y ejecutá de nuevo: {comando}",
            )
    sol.opciones["migrado"] = True


def _pasos_crud(sol: Solicitud) -> list[str]:
    pasos = [] if sol.opciones.get("migrado") else ["reflex " + " ".join(a) for a in _comandos_migracion(sol)]
    return [*pasos, "reflex run", "http://localhost:3000/@@pluralKebab@@"]


# --- Piezas -------------------------------------------------------------------------------


def _registrar(importacion: str, pagina: str, enlace: str) -> tuple[Insercion, ...]:
    """Las líneas que registran una página: el import, app.add_page y el enlace del menú."""
    return (
        Insercion("@@app@@/@@app@@.py", importacion, marcador="imports", descripcion="import", ubicacion="arriba, junto a los otros import"),
        Insercion("@@app@@/@@app@@.py", pagina, marcador="paginas", descripcion="página", ubicacion="después de app = rx.App(...)"),
        Insercion("@@app@@/plantilla.py", enlace, marcador="enlaces", descripcion="enlace en el menú", ubicacion="dentro de la lista ENLACES"),
    )


PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="página con su dirección y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@nombre@@", "ruta /@@nombreKebab@@"),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    contexto=_con_app(),
    marcadores={"app": _MARCADORES_PANTALLA["app"]},
    existe_si=("@@app@@/paginas/@@nombre@@.py",),
    inserciones=_registrar(
        "from @@app@@.paginas.@@nombre@@ import @@nombre@@",
        'app.add_page(@@nombre@@, route="/@@nombreKebab@@", title="@@nombreTitulo@@")',
        '("@@nombreTitulo@@", "/@@nombreKebab@@"),',
    ),
    siguiente_paso=["reflex run", "http://localhost:3000/@@nombreKebab@@"],
)

COMPONENTE = Pieza(
    clave="componente",
    titulo="Componente",
    descripcion="función que arma una parte de la interfaz para reutilizarla",
    ejemplo="Tarjeta",
    formas=("@@nombre@@",),
    contexto=_con_app(),
    marcadores={"app": _MARCADORES_PANTALLA["app"]},
    existe_si=("@@app@@/componentes/@@nombre@@.py",),
    si_no_existe=frozenset({"@@app@@/componentes/__init__.py"}),
    siguiente_paso=["# Usalo en una página:", "from @@app@@.componentes.@@nombre@@ import @@nombre@@"],
)

ESTADO = Pieza(
    clave="estado",
    titulo="Estado",
    descripcion="datos de la aplicación y las acciones que los cambian (rx.State)",
    ejemplo="contador",
    formas=("@@Nombre@@State",),
    ajustar_palabras=_js.sin_sufijo("state", "estado"),
    contexto=_con_app(),
    marcadores={"app": _MARCADORES_PANTALLA["app"]},
    existe_si=("@@app@@/estados/@@nombre@@.py",),
    si_no_existe=frozenset({"@@app@@/estados/__init__.py"}),
    siguiente_paso=[
        "# Usalo en una página:",
        "from @@app@@.estados.@@nombre@@ import @@Nombre@@State",
        'rx.button("Sumar", on_click=@@Nombre@@State.sumar)',
    ],
)

CRUD = Pieza(
    clave="crud",
    lectura=(
        ('@@app@@/modelos/@@nombre@@.py', 'el modelo: la tabla y sus campos'),
        ('@@app@@/paginas/@@plural@@.py', 'el estado (cargar, guardar, eliminar) y la página'),
    ),
    titulo="CRUD con base de datos",
    descripcion="tabla en la base de este proyecto y página para listar, agregar, editar y eliminar",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "ruta /@@pluralKebab@@"),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"migrar"}),
    contexto=_con_app(_contexto_crud),
    campos_reservados=_campos_reservados,
    marcadores={
        **_MARCADORES_PANTALLA,
        "imports_modelo": "import que necesitan los campos (datetime, Decimal, EmailStr...)",
        "import_validacion": "import de FechaHora (si hay fechas con hora)",
        "campos_base": "una línea por campo del modelo: nombre: str = Field(...)",
    },
    existe_si=("@@app@@/paginas/@@plural@@.py", "@@app@@/modelos/@@nombre@@.py"),
    si_no_existe=frozenset({"@@app@@/modelos/__init__.py"}),
    inserciones=_registrar(
        "from @@app@@.paginas.@@plural@@ import @@Nombre@@State, @@plural@@",
        'app.add_page(@@plural@@, route="/@@pluralKebab@@", title="@@titulo@@", on_load=@@Nombre@@State.cargar)',
        '("@@titulo@@", "/@@pluralKebab@@"),',
    ),
    siguiente_paso=_pasos_crud,
    despues=_migrar,
    confirmaciones={"migrar": "¿Crear ahora la tabla en la base de datos (reflex db)?"},
)

_ARCHIVOS_SERVICIO = frozenset({"@@app@@/servicios/__init__.py", "@@app@@/servicios/http.py"})

# --- Servicio con algunas funciones (--solo crear, --solo listar,obtener) ----------------

_FUNCION_PY = re.compile(r"^async def (\w+)\(")


def filtrar_funciones(texto: str, operaciones: tuple[str, ...]) -> str:
    """Deja en el módulo del servicio solo estas funciones (async def ...), con lo que tienen
    abajo hasta la siguiente. Las que no son de OPERACIONES (las de una plantilla propia) quedan."""
    salto = "\r\n" if "\r\n" in texto else "\n"
    bloques: list[tuple[str | None, list[str]]] = [(None, [])]
    for linea in texto.replace("\r\n", "\n").split("\n"):
        funcion = _FUNCION_PY.match(linea)
        if funcion:
            bloques.append((funcion.group(1), []))
        bloques[-1][1].append(linea)
    quedan = [linea for nombre, lineas in bloques if nombre is None or nombre in operaciones or nombre not in _js.OPERACIONES for linea in lineas]
    return salto.join(quedan).rstrip() + salto


def _transformar_servicio(sol: Solicitud, ruta: str, texto: str) -> str:
    """Pieza.transformar: con --solo, el módulo del servicio solo con esas funciones."""
    if not sol.opciones.get("solo") or not ruta.endswith(f"/servicios/{sol.nombre.snake}.py"):
        return texto
    return filtrar_funciones(texto, _js.operaciones_pedidas(sol))


def _funciones_del_servicio(archivo: Path) -> set[str]:
    try:
        lineas = archivo.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError):
        return set(_js.OPERACIONES)  # si no se puede leer, no se controla
    return {m.group(1) for linea in lineas if (m := _FUNCION_PY.match(linea))}


_USA_EL_CRUD = ("listar", "crear", "actualizar", "eliminar")


def _validar_servicio_completo(sol: Solicitud) -> None:
    """crud-api usa el servicio si ya existe: tiene que tener las funciones que llama."""
    archivo = sol.raiz / nombre_app(sol.raiz) / "servicios" / f"{sol.nombre.snake}.py"
    if not archivo.is_file():
        return
    faltan = [op for op in _USA_EL_CRUD if op not in _funciones_del_servicio(archivo)]
    if faltan:
        raise AndamioError(
            f"El servicio {archivo.relative_to(sol.raiz).as_posix()} no tiene {', '.join(faltan)} (se generó con --solo), y la página del crud las usa.",
            "Agregáselas (como en un servicio sin --solo), o borralo y generá el crud de nuevo: lo crea completo.",
        )


def _pasos_servicio(sol: Solicitud) -> list[str]:
    ops = _js.operaciones_pedidas(sol)
    ejemplo = {
        "listar": "registros = await @@nombre@@_api.listar()",
        "obtener": "registro = await @@nombre@@_api.obtener(1)",
        "crear": "nuevo = await @@nombre@@_api.crear({...})",
        "actualizar": "registro = await @@nombre@@_api.actualizar(1, {...})",
        "eliminar": "await @@nombre@@_api.eliminar(1)",
    }[ops[0]]
    pasos = ["# Usalo en un estado (las funciones son async):", "import @@app@@.servicios.@@nombre@@ as @@nombre@@_api", ejemplo]
    if set(_USA_EL_CRUD) <= set(ops):
        pasos += ["# O la página completa que lo usa:", "python -m andamio nuevo crud-api @@nombre@@ (con los mismos campos)"]
    return pasos

CRUD_API = Pieza(
    clave="crud-api",
    lectura=(
        ('@@app@@/servicios/@@nombre@@.py', 'cómo se habla con la API (/api/@@plural@@/)'),
        ('@@app@@/paginas/@@plural@@.py', 'el estado (cargar, guardar, eliminar) y la página'),
    ),
    titulo="CRUD con una API",
    descripcion="página para listar, agregar, editar y eliminar usando una API de andamio",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "ruta /@@pluralKebab@@"),
    usa_campos=True,
    usa_plural=True,
    contexto=_con_app(_contexto_crud_api_validado),
    marcadores={**_MARCADORES_PANTALLA, "campos_doc": "los campos del recurso, con su tipo (en el comentario)"},
    existe_si=("@@app@@/paginas/@@plural@@.py",),
    si_no_existe=_ARCHIVOS_SERVICIO | {"@@app@@/servicios/@@nombre@@.py"},
    inserciones=_registrar(
        "from @@app@@.paginas.@@plural@@ import @@Nombre@@State, @@plural@@",
        'app.add_page(@@plural@@, route="/@@pluralKebab@@", title="@@titulo@@", on_load=@@Nombre@@State.cargar)',
        '("@@titulo@@", "/@@pluralKebab@@"),',
    ),
    siguiente_paso=[
        "reflex run",
        "http://localhost:3000/@@pluralKebab@@",
        "# Necesita la API andando (Django, FastAPI o Express) con el recurso /api/@@plural@@/ y los mismos campos.",
        "# La dirección de la API está en API_URL (archivo .env).",
    ],
)

SERVICIO = Pieza(
    clave="servicio",
    titulo="Servicio",
    descripcion="funciones para usar un recurso de una API de andamio (Django, FastAPI o Express)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@nombre@@_api",),
    usa_campos=True,
    usa_plural=True,
    contexto=_con_app(_contexto_servicio),
    marcadores={"app": _MARCADORES_PANTALLA["app"], "campos_doc": "los campos del recurso, con su tipo (en el comentario)"},
    existe_si=("@@app@@/servicios/@@nombre@@.py",),
    si_no_existe=_ARCHIVOS_SERVICIO,
    opciones=frozenset({"solo"}),
    normalizar_opcion={"solo": _js.normalizar_solo},
    transformar=_transformar_servicio,
    siguiente_paso=_pasos_servicio,
)


def _contexto_proyecto(nombre: Nombre) -> dict[str, str]:
    paquete = nombre.snake
    if paquete in sys.stdlib_module_names:
        raise AndamioError(
            f"Un proyecto de Reflex no se puede llamar '{paquete}': es el nombre de un módulo de Python "
            "y la app no se podría importar.",
            "Elegí otro nombre (por ejemplo, mi-" + nombre.kebab + ").",
        )
    if not paquete.isidentifier() or keyword.iskeyword(paquete) or paquete in _PAQUETES_OCUPADOS:
        raise AndamioError(
            f"Un proyecto de Reflex no se puede llamar '{paquete}': es el nombre del paquete de Python de la app.",
            "Elegí otro nombre (que empiece con una letra y no sea el de una librería, como reflex).",
        )
    return {"activar": r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate"}


TEMA = pieza_tema(
    descripcion="color de acento y modo claro u oscuro de toda la aplicación (rx.theme en rxconfig.py)",
    contexto=_con_app(contexto_tema_reflex),
    marcadores={
        "app": _MARCADORES_PANTALLA["app"],
        "acento_radix": "el color de acento de Radix: violet, green, blue...",
        "apariencia": "inherit (el del sistema), light o dark",
        "modo": "auto, claro u oscuro (--modo)",
    },
    existe_si=("@@app@@/tema.py",),
    inserciones=(
        Insercion(
            "rxconfig.py",
            "from @@app@@.tema import TEMA  # noqa: E402,F811 (nuevo tema: reemplaza al de arriba)",
            marcador="tema",
            descripcion="usa el tema de @@app@@/tema.py",
            ubicacion="antes de config = rx.Config(...), que tiene que usar RadixThemesPlugin(theme=TEMA)",
        ),
    ),
    siguiente_paso=["reflex run", "# Para cambiar el color o el modo, editá @@app@@/tema.py."],
)

STACK = Stack(
    clave="reflex",
    titulo="Reflex (Python)",
    senal="rxconfig.py",
    detectar=_detectar,
    tipos=TIPOS,
    piezas={
        "crud": CRUD,
        "crud-api": CRUD_API,
        "pagina": PAGINA,
        "componente": COMPONENTE,
        "estado": ESTADO,
        "servicio": SERVICIO,
        "tema": TEMA,
    },
    ejemplo_proyecto="mi-app",
    siguiente_paso_proyecto=[
        "cd @@carpeta@@",
        "python -m venv .venv",
        "@@activar@@",
        "pip install -r requirements.txt",
        "reflex run",
        "http://localhost:3000",
    ],
    contexto_proyecto=_contexto_proyecto,
    contexto_env=lambda: {},
)
