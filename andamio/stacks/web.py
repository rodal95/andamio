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


def _enlace(href: str, texto: str, condicion=None, extra: str = "") -> Insercion:
    return Insercion(
        "js/menu.js",
        f"{{ href: '{href}', texto: '{texto}'{extra} }},",
        marcador="enlaces",
        descripcion="enlace en el menú" + (", solo con sesión" if extra else ""),
        ubicacion="dentro de la lista ENLACES",
        comentario="//",
        condicion=condicion,
    )


# --- Login (nuevo login) y páginas que piden ingresar (--protegido) -----------------------


def _con_login(raiz: Path) -> bool:
    return (raiz / "js" / "sesion.js").is_file()


def _protegida(sol: Solicitud) -> bool:
    return bool(sol.opciones.get("protegido"))


def _publica(sol: Solicitud) -> bool:
    return not _protegida(sol)


def _contexto_pagina(sol: Solicitud) -> dict[str, str]:
    if not _protegida(sol):
        return {"proteger": ""}
    if not _con_login(sol.raiz):
        raise AndamioError(
            "--protegido usa la sesión (js/sesion.js), que genera el login, y todavía no está.",
            "Generá primero el login: python -m andamio nuevo login",
        )
    explicacion = ["// Esta página pide ingresar (--protegido): sin sesión, lleva a ingresar.html."] if sol.guia else []
    return {"proteger": "\n".join(["import { pedirIngreso } from '../sesion.js';", "", *explicacion, "await pedirIngreso();"])}


_SERVIR = ["python -m http.server 5173"]

PAGINA = Pieza(
    clave="pagina",
    lectura=(
        ('@@nombreKebab@@.html', 'la página (el HTML)'),
        ('js/paginas/@@nombreKebab@@.js', 'lo que hace la página'),
    ),
    titulo="Página",
    descripcion="archivo .html con su .js y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@nombreKebab@@.html",),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_pagina("@@nombreKebab@@.html"),
    opciones=frozenset({"protegido"}),
    contexto=_contexto_pagina,
    marcadores={"proteger": "con --protegido: pedirIngreso() al principio del .js de la página (vacío si no)"},
    existe_si=("@@nombreKebab@@.html",),
    inserciones=(
        _enlace("@@nombreKebab@@.html", "@@nombreTitulo@@", _publica),
        # Una página protegida: su enlace se ve solo si alguien ingresó (lo dibuja el menú de la sesión).
        _enlace("@@nombreKebab@@.html", "@@nombreTitulo@@", _protegida, ", soloConSesion: true"),
    ),
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
    **_js.OPCION_SOLO,
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
    lectura=(
        ('js/servicios/@@nombreCamel@@Servicio.js', 'cómo se habla con la API (/api/@@plural@@/)'),
        ('@@pluralKebab@@.html', 'la página: la tabla y el formulario'),
        ('js/paginas/@@pluralKebab@@.js', 'lo que hace la página: cargar, guardar, editar y eliminar'),
    ),
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

def _con_registro(sol: Solicitud) -> bool:
    return not sol.opciones.get("sin_registro")


def _contexto_login(sol: Solicitud) -> dict[str, str]:
    registro = _con_registro(sol)
    return {
        "enlace_registro": "zona.append(enlace('registro.html', 'Registrarse'));" if registro else "",
        "y_registrarse": " y Registrarse" if registro else "",
        "pie_ingresar": '<p>¿No tenés cuenta? <a href="registro.html" id="registrate">Registrate</a></p>' if registro else "",
        "importar_sesion": "dibujarSesion, pedirIngreso" if sol.opciones.get("obligatorio") else "dibujarSesion",
    }


def _registro_a_omitir(sol: Solicitud) -> frozenset[str]:
    return frozenset() if _con_registro(sol) else frozenset({"registro.html", "js/paginas/registro.js"})


def _validar_login(raiz: Path, nombre: Nombre) -> None:
    if _con_login(raiz):
        raise AndamioError("El proyecto ya tiene el login (js/sesion.js).", "Para que una página pida ingresar: python -m andamio nuevo pagina Perfil --protegido")
    for archivo in ("ingresar.html", "registro.html"):
        if (raiz / archivo).exists():
            raise AndamioError(f"Ya hay una página {archivo}: el login usa ese nombre.", "Cambiale el nombre a la tuya y generá el login de nuevo.")


LOGIN = Pieza(
    clave="login",
    lectura=(
        ("js/sesion.js", "la sesión: quién ingresó, ingresar, registrarse, salir y pedirIngreso()"),
        ("ingresar.html", "la página para ingresar (con js/paginas/ingresar.js)"),
        ("registro.html", "la página para crear una cuenta (con js/paginas/registro.js)"),
        ("js/menu.js", "el menú: Ingresar, o quién ingresó y Salir (dibujarSesion)"),
    ),
    titulo="Login",
    descripcion="ingresar y crear una cuenta con la API (token JWT), y páginas que piden ingresar (--protegido)",
    ejemplo="",
    nombre_defecto="sesion",
    formas=("js/sesion.js, ingresar.html y registro.html",),
    opciones=frozenset({"sin_registro", "obligatorio"}),
    validar_nombre=_validar_login,
    contexto=_contexto_login,
    marcadores={
        "enlace_registro": "Registrarse en el menú (vacío con --sin-registro)",
        "y_registrarse": "' y Registrarse', para el comentario del menú (vacío con --sin-registro)",
        "pie_ingresar": "el enlace a registro.html debajo del formulario (vacío con --sin-registro)",
        "importar_sesion": "lo que js/menu.js toma de la sesión (pedirIngreso, solo con --obligatorio)",
    },
    existe_si=("js/sesion.js",),
    omitir=_registro_a_omitir,
    inserciones=(
        Insercion("js/menu.js", "import { @@importar_sesion@@ } from './sesion.js';", marcador="imports", descripcion="import de la sesión", ubicacion="arriba de todo", comentario="//"),
        Insercion("js/menu.js", "dibujarSesion(nav, ENLACES);", marcador="menu_sesion", descripcion="la sesión en el menú", ubicacion="en dibujarMenu, antes de barra.replaceChildren(nav)", comentario="//"),
        Insercion(
            "js/menu.js",
            "// Todas las páginas piden ingresar (nuevo login --obligatorio), salvo ingresar y registro.\npedirIngreso();",
            marcador="menu",
            descripcion="todas las páginas piden ingresar",
            ubicacion="al principio de dibujarMenu",
            comentario="//",
            condicion=lambda sol: bool(sol.opciones.get("obligatorio")),
        ),
    ),
    siguiente_paso=[
        "# La API con el login (Django, FastAPI o Express): python -m andamio nuevo login",
        *_SERVIR,
        "http://localhost:5173/ingresar.html",
        "# Para que una página pida ingresar:",
        "python -m andamio nuevo pagina Perfil --protegido",
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
    piezas={"pagina": PAGINA, "componente": COMPONENTE, "servicio": SERVICIO, "crud": CRUD, "login": LOGIN, **ESTILOS},
    ejemplo_proyecto="mi-pagina",
    siguiente_paso_proyecto=["cd @@carpeta@@", *_SERVIR, "http://localhost:5173"],
)
