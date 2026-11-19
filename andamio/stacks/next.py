"""Stacks de Next.js (App Router), en TypeScript o JavaScript.

- `next`: frontend que usa una API hecha con andamio (Django, FastAPI o Express).
- `next-fullstack`: la misma aplicación, con su propia API (Route Handlers en app/api/)
  y base de datos (Prisma + SQLite). La API cumple el mismo contrato que las otras,
  así que también la pueden usar React o React Native.

`next-fullstack` extiende `next`: su proyecto suma archivos al de `next`, y las piezas de
interfaz (componente, página, hook, servicio y CRUD) usan las mismas plantillas.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks import _js, express
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

_MARCADORES = {**_js.MARCADORES_EXTENSION, "api_por_defecto": "dirección de la API si no hay NEXT_PUBLIC_API_URL"}

# Carpetas de app/ que no pueden ser una página: api es la de la API (Route Handlers).
_RUTAS_RESERVADAS = {"api": "app/api es la carpeta de la API (Route Handlers)"}


def _validar_ruta(carpeta: str) -> None:
    if carpeta in _RUTAS_RESERVADAS:
        raise AndamioError(f"No se puede crear la página /{carpeta}: {_RUTAS_RESERVADAS[carpeta]}.", "Elegí otro nombre.")


def _validar_pagina(raiz: Path, nombre: Nombre) -> None:
    _js.validar_componente(raiz, nombre)
    _validar_ruta(nombre.kebab)


def _validar_crud(raiz: Path, nombre: Nombre) -> None:
    _js.validar_componente(raiz, nombre)
    _validar_ruta("-".join(nombre.plural_palabras))


def _enlace(texto: str) -> Insercion:
    return Insercion(
        "app/layout.@@extx@@",
        texto,
        marcador="enlaces",
        descripcion="enlace en el menú",
        ubicacion="dentro de <nav>",
        comentario="{/*",
    )


def _export(componente: str) -> Insercion:
    return Insercion(
        "components/index.@@ext@@",
        f"export {{ {componente} }} from './{componente}';",
        descripcion=f"export de {componente}",
        comentario="//",
        crear_si_falta=True,
    )


COMPONENTE = Pieza(
    clave="componente",
    titulo="Componente",
    descripcion="componente con sus estilos (.module.css)",
    ejemplo="Tarjeta",
    formas=("pascal",),
    validar_nombre=_js.validar_componente,
    marcadores=_MARCADORES,
    existe_si=("components/@@Nombre@@",),
    inserciones=(_export("@@Nombre@@"),),
    siguiente_paso=["# Usalo en una página:", "import { @@Nombre@@ } from '@/components';"],
)

HOOK = Pieza(
    clave="hook",
    titulo="Hook",
    descripcion="función use... para reutilizar estado y lógica",
    ejemplo="contador",
    formas=("use@@Nombre@@",),
    ajustar_palabras=_js.sin_prefijo_use,
    validar_nombre=_js.validar_hook,
    marcadores=_MARCADORES,
    existe_si=("hooks/use@@Nombre@@.@@ext@@",),
    siguiente_paso=[
        "# Usalo en un componente que empiece con 'use client':",
        "import { use@@Nombre@@ } from '@/hooks/use@@Nombre@@';",
    ],
)

PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="página con su ruta y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@Nombre@@Page", "ruta /@@nombreKebab@@"),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_pagina,
    marcadores=_MARCADORES,
    existe_si=("app/@@nombreKebab@@",),
    inserciones=(_enlace('<Link href="/@@nombreKebab@@">@@nombreTitulo@@</Link>'),),
    siguiente_paso=["npm run dev", "http://localhost:3000/@@nombreKebab@@"],
)

SERVICIO = Pieza(
    clave="servicio",
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API (Django, FastAPI o Express)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "@@nombreCamel@@Service"),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_servicio,
    marcadores={**_js.MARCADORES_SERVICIO, **_MARCADORES},
    existe_si=("services/@@nombreCamel@@Service.@@ext@@",),
    si_no_existe=frozenset({"services/http.ts", "services/http.js"}),
    siguiente_paso=[
        "# Usalo en un componente que empiece con 'use client':",
        "import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';",
        "# Necesita la API andando (Django, FastAPI o Express) con el recurso /api/@@plural@@/",
    ],
)

CRUD = Pieza(
    clave="crud",
    titulo="CRUD completo",
    descripcion="lista, detalle y formulario conectados a la API, con sus rutas",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "ruta /@@pluralKebab@@"),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_crud,
    validar_nombre=_validar_crud,
    marcadores={**_js.MARCADORES_CRUD, **_MARCADORES},
    existe_si=("app/@@pluralKebab@@", "components/@@Nombre@@Detalle"),
    si_no_existe=frozenset(
        {
            "services/http.ts",
            "services/http.js",
            "services/@@nombreCamel@@Service.ts",
            "services/@@nombreCamel@@Service.js",
            "hooks/useConsulta.ts",
            "hooks/useConsulta.js",
        }
    ),
    inserciones=(_enlace('<Link href="/@@pluralKebab@@">@@titulo@@</Link>'), _export("@@Nombre@@Detalle")),
    siguiente_paso=[
        "npm run dev",
        "http://localhost:3000/@@pluralKebab@@",
        "# Necesita la API andando (Django, FastAPI o Express), con el recurso /api/@@plural@@/ generado con los mismos campos.",
    ],
)


def _marcadores_variante(api: str) -> dict[str, dict[str, str]]:
    return {v: {**marcadores, "api_por_defecto": api} for v, marcadores in _js.MARCADORES_VARIANTE.items()}


STACK = Stack(
    clave="next",
    titulo="Next.js (frontend)",
    senal="package.json con next",
    detectar=_js.detectar_dependencias("next"),
    tipos=_js.TIPOS,
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "hook": HOOK, "servicio": SERVICIO, "crud": CRUD},
    ejemplo_proyecto="mi-web",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:3000"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_marcadores_variante("http://localhost:8000/api"),
)


# --- Full stack: la API y la base de datos en el mismo proyecto ---------------------------


def _pasos_crud_fullstack(sol: Solicitud) -> list[str]:
    pasos = ["npm run dev", "http://localhost:3000/@@pluralKebab@@"]
    if not (sol.raiz / "app" / "api" / sol.nombre.plural).is_dir():
        campos = " ".join(f"{c.nombre}:{c.tipo}" for c in sol.campos)
        pasos = [
            "# Las páginas usan la API de este proyecto. Si todavía no generaste el recurso:",
            f"python -m andamio nuevo recurso {sol.nombre.snake} {campos} --migrar",
            *pasos,
        ]
    return pasos


RECURSO = dataclasses.replace(
    express.RECURSO,
    descripcion="API en app/api/ (Route Handlers), modelo de Prisma, validación y tests",
    existe_si=("app/api/@@plural@@",),
    validar_nombre=express.validar_nombre_recurso("app/api"),
    inserciones=(express.INSERCION_MODELO,),
    siguiente_paso=express.pasos_recurso(["npm run dev", "http://localhost:3000/api/@@plural@@/"]),
)

STACK_FULLSTACK = Stack(
    clave="next-fullstack",
    titulo="Next.js full stack",
    senal="package.json con next y @prisma/client",
    detectar=_js.detectar_dependencias("next", "@prisma/client"),
    tipos=_js.TIPOS,
    piezas={
        "recurso": RECURSO,
        "crud": dataclasses.replace(CRUD, siguiente_paso=_pasos_crud_fullstack),
        "pagina": PAGINA,
        "componente": COMPONENTE,
        "hook": HOOK,
        "servicio": dataclasses.replace(
            SERVICIO,
            descripcion="funciones para usar un recurso de la API de este proyecto",
            siguiente_paso=SERVICIO.siguiente_paso[:2],
        ),
    },
    ejemplo_proyecto="mi-app",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:3000"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_marcadores_variante("/api"),
    extiende="next",
)
