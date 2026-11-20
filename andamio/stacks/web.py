"""Stack `web`: página web con HTML, CSS y JavaScript, sin instalar nada (ni Node ni npm).

Cada página es un .html con su .js (módulos de JavaScript: import/export). El menú está
en js/menu.js, así se escribe una sola vez. Se ve con:  python -m http.server 5173
"""

from __future__ import annotations

from pathlib import Path

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.estilos import piezas_de_estilos
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

TIPOS = _js.TIPOS

_PASOS_NUMERICOS = {"int": "1", "decimal": "0.01", "float": "any"}
_TIPO_INPUT = {"email": "email", "date": "date", "datetime": "datetime-local"}


def _detectar(raiz: Path) -> bool:
    return (raiz / "index.html").is_file() and (raiz / "js" / "menu.js").is_file()


def _campo_formulario(campo) -> list[str]:
    n = campo.nombre
    if campo.tipo == "bool":
        control = f'<input type="checkbox" id="{n}" name="{n}" />'
    elif campo.tipo == "text":
        control = f'<textarea id="{n}" name="{n}" rows="3"></textarea>'
    elif campo.tipo in _PASOS_NUMERICOS:
        control = f'<input type="number" step="{_PASOS_NUMERICOS[campo.tipo]}" id="{n}" name="{n}" />'
    else:
        control = f'<input type="{_TIPO_INPUT.get(campo.tipo, "text")}" id="{n}" name="{n}" />'
    return [
        '<div class="campo">',
        f'  <label for="{n}">{campo.titulo}</label>',
        f"  {control}",
        f'  <small class="error" id="error-{n}"></small>',
        "</div>",
    ]


def _contexto_crud(sol: Solicitud) -> dict[str, str]:
    contexto = _js.contexto_servicio(sol)
    en_tabla = [c for c in sol.campos if c.tipo != "text"] or sol.campos
    formulario: list[str] = []
    for campo in sol.campos:
        formulario += _campo_formulario(campo)
    contexto.update(
        verbose_plural=" ".join(sol.nombre.plural_palabras),
        campos_formulario="\n".join(formulario),
        campos_tipos="\n".join(f"{c.nombre}: '{c.tipo}'," for c in sol.campos),
        columnas=", ".join(f"'{c.nombre}'" for c in en_tabla),
        columnas_encabezado="\n".join(f"<th>{c.titulo}</th>" for c in en_tabla),
    )
    return contexto


def _validar_pagina(ruta: str):
    def validar(raiz: Path, nombre: Nombre) -> None:
        archivo = ruta.replace("@@nombreKebab@@", nombre.kebab).replace("@@pluralKebab@@", "-".join(nombre.plural_palabras))
        if archivo == "index.html":
            raise AndamioError("index.html es la página de inicio.", "Elegí otro nombre para la página.")
        try:
            menu = (raiz / "js" / "menu.js").read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            return
        if f"href: '{archivo}'" in menu:
            raise AndamioError(f"Ya hay una página {archivo} en el menú (js/menu.js).", "Elegí otro nombre.")

    return validar


def _enlace(href: str, texto: str) -> Insercion:
    return Insercion(
        "js/menu.js",
        f"{{ href: '{href}', texto: '{texto}' }},",
        marcador="enlaces",
        descripcion="enlace en el menú",
        ubicacion="dentro de la lista ENLACES",
        comentario="//",
    )


_SERVIR = ["python -m http.server 5173"]

PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="archivo .html con su .js y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@nombreKebab@@.html",),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_pagina("@@nombreKebab@@.html"),
    existe_si=("@@nombreKebab@@.html",),
    inserciones=(_enlace("@@nombreKebab@@.html", "@@nombreTitulo@@"),),
    siguiente_paso=[*_SERVIR, "http://localhost:5173/@@nombreKebab@@.html"],
)

COMPONENTE = Pieza(
    clave="componente",
    titulo="Componente",
    descripcion="función que crea una parte de la página, con su CSS",
    ejemplo="Tarjeta",
    formas=("crear@@Nombre@@", "js/componentes/@@nombreKebab@@.js"),
    existe_si=("js/componentes/@@nombreKebab@@.js",),
    inserciones=(
        Insercion(
            "css/estilos.css",
            '@import url("componentes/@@nombreKebab@@.css");',
            marcador="componentes",
            descripcion="import de sus estilos",
            ubicacion="arriba de todo (los @import van antes que cualquier otra regla)",
            comentario="/*",
        ),
    ),
    siguiente_paso=[
        "# Usalo en el .js de una página:",
        "import { crear@@Nombre@@ } from '../componentes/@@nombreKebab@@.js';",
    ],
)

SERVICIO = Pieza(
    clave="servicio",
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API (Django, FastAPI, Express o Next.js)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@nombreCamel@@Servicio",),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_servicio,
    marcadores=_js.MARCADORES_SERVICIO,
    existe_si=("js/servicios/@@nombreCamel@@Servicio.js",),
    siguiente_paso=[
        "# Usalo en el .js de una página:",
        "import { @@nombreCamel@@Servicio } from '../servicios/@@nombreCamel@@Servicio.js';",
        "# Necesita la API andando con el recurso /api/@@plural@@/ (la dirección está en js/config.js).",
    ],
)

# Cada campo del formulario usa los id "<campo>" y "error-<campo>"; no pueden repetir
# los id fijos de la página (getElementById devolvería otro elemento).
_IDS_DE_LA_PAGINA = {
    "estado": "es el id del mensaje de estado de la página (Cargando...)",
    "filas": "es el id del cuerpo de la tabla",
    "formulario": "es el id del formulario",
    "cancelar": "es el id del botón Cancelar",
    "general": "su mensaje de error usaría el id error-general, que ya usa la página",
}


def _campos_reservados_crud(nombre: Nombre) -> dict[str, str]:
    return dict(_IDS_DE_LA_PAGINA)


CRUD = Pieza(
    clave="crud",
    titulo="CRUD completo",
    descripcion="página con la lista y el formulario para agregar, editar y eliminar usando la API",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@pluralKebab@@.html", "@@nombreCamel@@Servicio"),
    usa_campos=True,
    usa_plural=True,
    contexto=_contexto_crud,
    campos_reservados=_campos_reservados_crud,
    validar_nombre=_validar_pagina("@@pluralKebab@@.html"),
    marcadores={
        **_js.MARCADORES_SERVICIO,
        "verbose_plural": "plural en minúsculas y con espacios",
        "campos_formulario": "un <div class=\"campo\"> con su <label>, su control y su error, por campo",
        "campos_tipos": "el tipo de cada campo para leer el formulario: precio: 'decimal',",
        "columnas": "los campos que se muestran en la tabla",
        "columnas_encabezado": "un <th> por columna",
    },
    existe_si=("@@pluralKebab@@.html", "js/paginas/@@pluralKebab@@.js"),
    si_no_existe=frozenset({"js/servicios/@@nombreCamel@@Servicio.js"}),
    inserciones=(_enlace("@@pluralKebab@@.html", "@@titulo@@"),),
    siguiente_paso=[
        *_SERVIR,
        "http://localhost:5173/@@pluralKebab@@.html",
        "# Necesita la API andando (Django, FastAPI, Express o Next.js full stack) con el recurso /api/@@plural@@/ generado con los mismos campos.",
    ],
)

ESTILOS = piezas_de_estilos(
    "css",
    lambda ruta: Insercion(
        "css/estilos.css",
        f'@import url("{ruta}");',
        marcador="componentes",
        descripcion="import del CSS",
        ubicacion="arriba de todo (los @import van antes que cualquier otra regla)",
        comentario="/*",
    ),
    'Usá las clases en tu HTML: class="...".',
)

STACK = Stack(
    clave="web",
    titulo="HTML + CSS + JavaScript",
    senal="index.html y js/menu.js",
    detectar=_detectar,
    tipos=TIPOS,
    piezas={"pagina": PAGINA, "componente": COMPONENTE, "servicio": SERVICIO, "crud": CRUD, **ESTILOS},
    ejemplo_proyecto="mi-pagina",
    siguiente_paso_proyecto=["cd @@carpeta@@", *_SERVIR, "http://localhost:5173"],
)
