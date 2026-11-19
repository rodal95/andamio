"""Stack `fastapi`: API REST con FastAPI + SQLModel.

La API cumple el mismo "contrato" que la de Django (rutas /api/<plural>/ con barra
final, lista como array, decimales como número, errores 400 {campo: [mensajes]}),
así los servicios y el CRUD de React y React Native funcionan igual con las dos.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack
from andamio.stacks.django import _VALORES_PRUEBA, TIPOS

_TIPO_PYTHON = {
    "str": "str",
    "text": "str",
    "int": "int",
    "decimal": "Decimal",
    "float": "float",
    "bool": "bool",
    "date": "date",
    "datetime": "FechaHora",  # app/tipos.py: sin zona horaria se toma como hora local
    "email": "EmailStr",
}

# Cómo se declara cada campo en el modelo base (obligatorio) y en el de modificación (opcional).
_CAMPO_BASE = {
    "str": "str = Field(min_length=1, max_length=200)",
    "text": "str = Field(min_length=1, sa_type=Text)",
    "int": "int",
    "decimal": "Decimal = Field(max_digits=10, decimal_places=2)",
    "float": "float",
    "bool": "bool = False",
    "date": "date",
    "datetime": "FechaHora",
    "email": "EmailStr = Field(max_length=254)",
}

_CAMPO_OPCIONAL = {
    "str": "str | None = Field(default=None, min_length=1, max_length=200)",
    "text": "str | None = Field(default=None, min_length=1)",
    "decimal": "Decimal | None = Field(default=None, max_digits=10, decimal_places=2)",
    "email": "EmailStr | None = Field(default=None, max_length=254)",
}

_TEXTO = ("str", "text", "email")


def _detectar(raiz: Path) -> bool:
    requisitos = raiz / "requirements.txt"
    if not ((raiz / "app" / "main.py").is_file() and requisitos.is_file()):
        return False
    try:
        return "fastapi" in requisitos.read_text(encoding="utf-8-sig").lower()
    except (OSError, UnicodeDecodeError):
        return False


def _literal(valor: object) -> str:
    return json.dumps(valor, ensure_ascii=False) if isinstance(valor, str) else repr(valor)


def _valor_json(tipo: str, valor: object) -> str:
    """Cómo aparece en el JSON de la respuesta (los decimales vuelven como número)."""
    return repr(float(valor)) if tipo == "decimal" else _literal(valor)


def _contexto_recurso(sol: Solicitud) -> dict[str, str]:
    campos = sol.campos
    modelo = sol.nombre.pascal
    tipos = {c.tipo for c in campos}

    # import del modelo
    stdlib = ["from datetime import date, datetime" if "date" in tipos else "from datetime import datetime"]
    if "decimal" in tipos:
        stdlib.append("from decimal import Decimal")
    terceros = []
    if "email" in tipos:
        terceros.append("from pydantic import EmailStr")
    if "text" in tipos:
        terceros.append("from sqlalchemy import Text")
    imports_modelo = "\n".join(stdlib) + "\n" + ("\n" + "\n".join(terceros) if terceros else "")

    # import del router (tipos de los filtros)
    filtrables = [c for c in campos if c.tipo != "text"]
    usados = {_TIPO_PYTHON[c.tipo] for c in filtrables}
    stdlib_router = []
    if "date" in usados:
        stdlib_router.append("from datetime import date")
    if "Decimal" in usados:
        stdlib_router.append("from decimal import Decimal")
    busqueda = [c for c in campos if c.tipo in _TEXTO]
    import_sqlmodel = "from sqlmodel import col, or_, select" if len(busqueda) > 1 else "from sqlmodel import col, select"
    imports_router = "\n".join(stdlib_router) + "\n" if stdlib_router else ""

    filtros = []
    for c in filtrables:
        filtros += [f"if {c.nombre} is not None:", f"    consulta = consulta.where({modelo}.{c.nombre} == {c.nombre})"]
    bloque_busqueda = ""
    if len(busqueda) == 1:
        bloque_busqueda = f"if search:\n    consulta = consulta.where(col({modelo}.{busqueda[0].nombre}).icontains(search))"
    elif busqueda:
        condiciones = "".join(f"\n            col({modelo}.{c.nombre}).icontains(search)," for c in busqueda)
        bloque_busqueda = f"if search:\n    consulta = consulta.where(\n        or_({condiciones}\n        )\n    )"

    verificado = campos[0]
    esperado = _valor_json(verificado.tipo, _VALORES_PRUEBA[verificado.tipo][1])
    imports_test = ""
    if verificado.tipo == "datetime":
        # Vuelve en hora local ("2025-02-20T15:45:00-03:00"): se compara el instante, no el texto.
        imports_test = "from datetime import datetime, timezone\n"
        verificacion = (
            f'assert datetime.fromisoformat(respuesta.json()["{verificado.nombre}"]) == '
            "datetime(2025, 2, 20, 18, 45, tzinfo=timezone.utc)"
        )
    else:
        verificacion = f'assert respuesta.json()["{verificado.nombre}"] == {esperado}'
    tipos_modelo = ["DecimalNumero"] if "decimal" in tipos else []

    return {
        "imports_modelo": imports_modelo,
        "import_tipos": "from app.tipos import " + ", ".join([*tipos_modelo, "FechaHora", "ahora"]),
        "campos_base": "\n".join(f"{c.nombre}: {_CAMPO_BASE[c.tipo]}" for c in campos),
        "campos_opcionales": "\n".join(
            f"{c.nombre}: {_CAMPO_OPCIONAL.get(c.tipo, _TIPO_PYTHON[c.tipo] + ' | None = None')}" for c in campos
        ),
        "campos_leer": "\n".join(f"{c.nombre}: DecimalNumero  # sale como número en el JSON" for c in campos if c.tipo == "decimal"),
        "imports_router": imports_router,
        "import_sqlmodel": import_sqlmodel,
        "import_tipos_router": "from app.tipos import FechaHora, ahora" if "FechaHora" in usados else "from app.tipos import ahora",
        "campos_orden": "\n".join(
            f'"{n}": {modelo}.{n},' for n in ["id", *(c.nombre for c in campos), "creado", "actualizado"]
        ),
        "parametros_filtro": "\n".join(f"{c.nombre}: {_TIPO_PYTHON[c.tipo].replace('EmailStr', 'str')} | None = None," for c in filtrables),
        "filtros": "\n".join(filtros),
        "bloque_busqueda": bloque_busqueda,
        "datos_prueba": "\n".join(f'"{c.nombre}": {_literal(_VALORES_PRUEBA[c.tipo][0])},' for c in campos),
        "datos_modificados": "\n".join(f'"{c.nombre}": {_literal(_VALORES_PRUEBA[c.tipo][1])},' for c in campos),
        "verificacion": verificacion,
        "imports_test": imports_test,
    }


# --- Validación de nombres -------------------------------------------------------------

_MODULOS_DEL_PROYECTO = {
    "db": "ya existe app/db.py",
    "config": "ya existe app/config.py",
    "main": "ya existe app/main.py",
    "tipos": "ya existe app/tipos.py",
    "errores": "ya existe app/errores.py",
    "tests": "es la carpeta de los tests",
}


def _validar_nombre(raiz: Path, nombre: Nombre) -> None:
    motivo = _MODULOS_DEL_PROYECTO.get(nombre.plural)
    if motivo is None:
        try:
            if f"app.{nombre.plural}.router" in (raiz / "app" / "main.py").read_text(encoding="utf-8-sig"):
                motivo = "ya está registrado en app/main.py"
        except (OSError, UnicodeDecodeError):
            pass
    if motivo:
        raise AndamioError(f"No se puede crear el recurso '{nombre.plural}': {motivo}.", "Elegí otro nombre, o indicá otro plural con --plural.")


# Atributos de los modelos de SQLModel (y Pydantic): un campo con ese nombre los tapa.
_ATRIBUTOS_DE_SQLMODEL = (
    "metadata", "registry", "sqlmodel_update",
    "copy", "dict", "json", "schema", "schema_json", "construct", "validate",
    "parse_obj", "parse_raw", "parse_file", "from_orm", "update_forward_refs",
    "model_config", "model_fields", "model_computed_fields", "model_extra", "model_fields_set",
    "model_construct", "model_copy", "model_dump", "model_dump_json", "model_json_schema",
    "model_parametrized_name", "model_post_init", "model_rebuild",
    "model_validate", "model_validate_json", "model_validate_strings",
)


def _campos_reservados(nombre: Nombre) -> dict[str, str]:
    # Los campos también son parámetros de la lista (?campo=valor) y atributos de SQLModel.
    reservados = {n: "es un nombre que usa SQLModel en los modelos" for n in _ATRIBUTOS_DE_SQLMODEL}
    for n in ("sesion", "consulta", "campo", "columna", "datos", "cambios", "router", "app"):
        reservados[n] = "lo usa el código generado"
    reservados["search"] = "lo usa la API para buscar (?search=)"
    reservados["ordering"] = "lo usa la API para ordenar (?ordering=)"
    reservados[f"id_{nombre.snake}"] = "es el nombre que se usa para el id"
    return reservados


RECURSO = Pieza(
    clave="recurso",
    titulo="Recurso REST",
    descripcion="modelo, API (CRUD) y tests",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("pascal", "snake"),
    usa_campos=True,
    usa_plural=True,
    contexto=_contexto_recurso,
    campos_reservados=_campos_reservados,
    marcadores={
        "imports_modelo": "import que necesitan los campos (datetime, Decimal, EmailStr...)",
        "import_tipos": "import de app.tipos (DecimalNumero solo si hay decimales)",
        "campos_base": "una línea por campo del modelo: nombre: str = Field(...)",
        "campos_opcionales": "los mismos campos, opcionales (para PATCH)",
        "campos_leer": "campos que cambian al leer (los decimales salen como número)",
        "imports_router": "import que necesitan los filtros (date, datetime, Decimal)",
        "import_sqlmodel": "import de sqlmodel (or_ solo si se busca en varios campos de texto)",
        "import_tipos_router": "import de app.tipos (FechaHora solo si hay fechas con hora)",
        "campos_orden": "campos para ?ordering=",
        "parametros_filtro": "un parámetro de la lista por campo, para ?campo=valor",
        "filtros": "un if por campo filtrable",
        "bloque_busqueda": "la búsqueda en los campos de texto (?search=)",
        "datos_prueba": 'datos de ejemplo para los tests: "nombre": "Texto de prueba",',
        "datos_modificados": "datos de ejemplo para el test de modificación",
        "verificacion": "lo que controla el test de modificación",
        "imports_test": "import que necesita esa verificación (si hace falta)",
    },
    existe_si=("app/@@plural@@",),
    inserciones=(
        Insercion(
            "app/main.py",
            "from app.@@plural@@.router import router as @@plural@@_router",
            marcador="imports",
            descripcion="import del router",
            ubicacion="arriba, junto a los otros import",
        ),
        Insercion(
            "app/main.py",
            "app.include_router(@@plural@@_router)",
            marcador="routers",
            descripcion="rutas /api/@@plural@@/",
            ubicacion="después de app.add_exception_handler(...)",
        ),
    ),
    siguiente_paso=[
        "python -m uvicorn app.main:app --reload",
        "http://127.0.0.1:8000/docs",
        "# Los tests del recurso se ejecutan con: python -m pytest",
    ],
)


def _activar() -> str:
    return r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate"


STACK = Stack(
    clave="fastapi",
    titulo="FastAPI",
    senal="app/main.py y requirements.txt con fastapi",
    detectar=_detectar,
    tipos=TIPOS,
    piezas={"recurso": RECURSO},
    ejemplo_proyecto="mi-api",
    siguiente_paso_proyecto=[
        "cd @@carpeta@@",
        "python -m venv .venv",
        "@@activar@@",
        "pip install -r requirements.txt",
        "python -m uvicorn app.main:app --reload",
        "http://127.0.0.1:8000/docs",
    ],
    contexto_proyecto=lambda nombre: {"activar": _activar()},
    contexto_env=lambda: {},
    validar_nombre=_validar_nombre,
)
