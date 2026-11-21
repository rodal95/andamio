"""Stack `react`: aplicación web con React + Vite + TypeScript."""

from __future__ import annotations

from andamio.estilos import piezas_de_estilos
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Stack

COMPONENTE = Pieza(
    clave="componente",
    titulo="Componente",
    descripcion="componente con sus estilos (.module.css)",
    ejemplo="Tarjeta",
    formas=("pascal",),
    validar_nombre=_js.validar_componente,
    marcadores=_js.MARCADORES_EXTENSION,
    existe_si=("src/components/@@Nombre@@",),
    inserciones=(
        Insercion(
            "src/components/index.@@ext@@",
            "export { @@Nombre@@ } from './@@Nombre@@';",
            descripcion="export de @@Nombre@@",
            comentario="//",
            crear_si_falta=True,
        ),
    ),
    siguiente_paso=["# Usalo en src/App.tsx:", "import { @@Nombre@@ } from './components';"],
)

HOOK = Pieza(
    clave="hook",
    titulo="Hook",
    descripcion="función use... para reutilizar estado y lógica",
    ejemplo="contador",
    formas=("use@@Nombre@@",),
    ajustar_palabras=_js.sin_prefijo_use,
    validar_nombre=_js.validar_hook,
    marcadores=_js.MARCADORES_EXTENSION,
    existe_si=("src/hooks/use@@Nombre@@.@@ext@@",),
    siguiente_paso=["# Usalo en src/App.tsx:", "import { use@@Nombre@@ } from './hooks/use@@Nombre@@';"],
)

_RUTA_PAGINA = _js.validar_ruta_libre(lambda nombre: f"/{nombre.kebab}")


_COMPONENTE_PAGINA = _js.validar_componentes_libres(lambda nombre: [f"{nombre.pascal}Page"])


def _validar_pagina(raiz, nombre) -> None:
    _js.validar_componente(raiz, nombre)
    _RUTA_PAGINA(raiz, nombre)
    _COMPONENTE_PAGINA(raiz, nombre)


def _insercion_app(
    texto: str, marcador: str, descripcion: str, ubicacion: str, comentario: str, condicion=None
) -> Insercion:
    return Insercion(
        "src/App.@@extx@@", texto, marcador=marcador, descripcion=descripcion, ubicacion=ubicacion, comentario=comentario, condicion=condicion
    )


_HOOKS = _js.hooks("src/hooks")  # useConsulta y useFormulario


def _sin_uno(sol) -> bool:
    return not sol.opciones.get("uno")


def _con_form(sol) -> bool:
    return bool(sol.opciones.get("form"))


PAGINA = Pieza(
    clave="pagina",
    lectura=(
        ("@@datos_servicio@@", "las funciones que piden los datos a la API"),
        ("@@datos_hook@@", "el hook que usa el servicio: useConsulta (pide los datos) o useFormulario (crea y edita)"),
        ('src/pages/@@Nombre@@Page/@@Nombre@@Page.@@extx@@', 'la página'),
        ('src/App.@@extx@@', 'su ruta y su enlace en el menú'),
    ),
    titulo="Página",
    descripcion="página con su ruta y su enlace en el menú; con --datos, usa un servicio (lista, --uno o --form)",
    ejemplo="Contacto",
    formas=("@@Nombre@@Page",),
    opciones=frozenset({"datos", "uno", "form"}),
    normalizar_opcion={"datos": _js.normalizar_datos},
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_pagina,
    contexto=_js.contexto_pagina,
    marcadores={**_js.MARCADORES_EXTENSION, **_js.MARCADORES_PAGINA},
    existe_si=("src/pages/@@Nombre@@Page",),
    # Con --datos se crea el hook que usa, y si ya existe (lo generó un crud o un servicio) no se toca.
    si_no_existe=_HOOKS,
    omitir=_js.hooks_a_omitir("src/hooks"),
    inserciones=(
        _insercion_app("import { @@Nombre@@Page } from './pages/@@Nombre@@Page';", "imports", "import", "arriba, junto a los otros import", "//"),
        _insercion_app('<Route path="@@ruta_pagina@@" element={<@@Nombre@@Page />} />', "rutas", "ruta @@ruta_pagina@@", "dentro de <Routes>", "{/*"),
        # El formulario (--form) también edita: la misma página con el id en la ruta.
        _insercion_app(
            '<Route path="@@ruta_pagina@@/:id" element={<@@Nombre@@Page />} />', "rutas", "ruta @@ruta_pagina@@/:id (editar)", "dentro de <Routes>", "{/*", _con_form
        ),
        # Una página de uno solo (--uno) necesita un id en la ruta: no va en el menú.
        _insercion_app('<Link to="/@@nombreKebab@@">@@nombreTitulo@@</Link>', "enlaces", "enlace en el menú", "dentro de <nav>", "{/*", _sin_uno),
    ),
    siguiente_paso=_js.pasos_pagina,
)

_RUTA_CRUD = _js.validar_ruta_libre(lambda nombre: "/" + "-".join(nombre.plural_palabras))


_COMPONENTES_CRUD = _js.validar_componentes_libres(
    lambda nombre: [f"{nombre.pascal}{pagina}Page" for pagina in ("Lista", "Detalle", "Form")]
)


def _validar_crud(raiz, nombre) -> None:
    _js.validar_componente(raiz, nombre)
    _RUTA_CRUD(raiz, nombre)
    _COMPONENTES_CRUD(raiz, nombre)


CRUD = Pieza(
    clave="crud",
    lectura=(
        ('src/services/@@nombreCamel@@Service.@@ext@@', 'cómo se habla con la API (/api/@@plural@@/)'),
        ('src/pages/@@pluralKebab@@/@@Nombre@@ListaPage.@@extx@@', 'la lista'),
        ('src/components/@@Nombre@@Detalle/@@Nombre@@Detalle.@@extx@@', 'muestra uno y avisa con onEditar / onEliminar'),
        ('src/pages/@@pluralKebab@@/@@Nombre@@DetallePage.@@extx@@', 'la página del detalle (con eliminar)'),
        ('src/pages/@@pluralKebab@@/@@Nombre@@FormPage.@@extx@@', 'el formulario para crear y editar'),
        ('src/App.@@extx@@', 'las rutas /@@pluralKebab@@ y el enlace en el menú'),
    ),
    titulo="CRUD completo",
    descripcion="lista, detalle y formulario conectados a la API, con sus rutas",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "ruta /@@pluralKebab@@"),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_crud,
    validar_nombre=_validar_crud,
    marcadores=_js.MARCADORES_CRUD,
    existe_si=("src/pages/@@pluralKebab@@", "src/components/@@Nombre@@Detalle"),
    si_no_existe=frozenset(
        {
            "src/services/http.ts",
            "src/services/http.js",
            "src/services/@@nombreCamel@@Service.ts",
            "src/services/@@nombreCamel@@Service.js",
        }
    )
    | _HOOKS,
    inserciones=(
        _insercion_app(
            "import { @@Nombre@@DetallePage, @@Nombre@@FormPage, @@Nombre@@ListaPage } from './pages/@@pluralKebab@@';",
            "imports",
            "import",
            "arriba, junto a los otros import",
            "//",
        ),
        _insercion_app(
            '<Route path="/@@pluralKebab@@" element={<@@Nombre@@ListaPage />} />\n'
            '<Route path="/@@pluralKebab@@/nuevo" element={<@@Nombre@@FormPage />} />\n'
            '<Route path="/@@pluralKebab@@/:id" element={<@@Nombre@@DetallePage />} />\n'
            '<Route path="/@@pluralKebab@@/:id/editar" element={<@@Nombre@@FormPage />} />',
            "rutas",
            "rutas /@@pluralKebab@@",
            "dentro de <Routes>",
            "{/*",
        ),
        _insercion_app('<Link to="/@@pluralKebab@@">@@titulo@@</Link>', "enlaces", "enlace en el menú", "dentro de <nav>", "{/*"),
        Insercion(
            "src/components/index.@@ext@@",
            "export { @@Nombre@@Detalle } from './@@Nombre@@Detalle';",
            descripcion="export de @@Nombre@@Detalle",
            comentario="//",
            crear_si_falta=True,
        ),
    ),
    siguiente_paso=_js.pasos_router(
        [
            "npm run dev",
            "http://localhost:5173/@@pluralKebab@@",
            "# Necesita la API andando (Django, FastAPI o Express), con el recurso /api/@@plural@@/ generado con los mismos campos.",
        ]
    ),
)

SERVICIO = Pieza(
    clave="servicio",
    lectura=(
        ('src/services/@@nombreCamel@@Service.@@ext@@', 'las funciones para usar /api/@@plural@@/'),
        ('src/services/http.@@ext@@', 'lo común a todas las llamadas: dirección de la API y errores'),
        ('src/hooks/useConsulta.@@ext@@', 'el useEffect para pedir datos desde un componente, con cargando y error'),
        ('src/hooks/useFormulario.@@ext@@', 'los datos de un formulario para crear o editar, con los errores de la API'),
    ),
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API (Django, FastAPI o Express)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "@@nombreCamel@@Service"),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_servicio,
    marcadores=_js.MARCADORES_SERVICIO,
    existe_si=("src/services/@@nombreCamel@@Service.@@ext@@",),
    si_no_existe=frozenset({"src/services/http.ts", "src/services/http.js"}) | _HOOKS,
    siguiente_paso=[
        "# Una página que lo usa (lista, o uno solo con --uno):",
        "python -m andamio nuevo pagina @@Nombre@@Lista --datos @@nombre@@",
        "python -m andamio nuevo pagina @@Nombre@@Detalle --datos @@nombre@@ --uno",
        "python -m andamio nuevo pagina @@Nombre@@Editar --datos @@nombre@@ --form",
        "# O a mano, en un componente:",
        "import { useConsulta } from './hooks/useConsulta';",
        "import { @@nombreCamel@@Service } from './services/@@nombreCamel@@Service';",
        "const { datos, cargando, error } = useConsulta(@@nombreCamel@@Service.listar);",
        "# Necesita la API andando (Django, FastAPI o Express) con el recurso /api/@@plural@@/",
    ],
)

ESTILOS = piezas_de_estilos(
    "src",
    lambda ruta: Insercion(
        "src/main.@@extx@@",
        f"import './{ruta}';",
        marcador="estilos",
        descripcion="import del CSS",
        ubicacion="junto a import './index.css'",
        comentario="//",
    ),
    'En JSX: className="...".',
    _js.MARCADORES_EXTENSION,
)

STACK = Stack(
    clave="react",
    titulo="React + Vite",
    senal="package.json con vite y react",
    detectar=_js.detectar_dependencias("vite", "react"),
    tipos=_js.TIPOS_CON_RELACIONES,
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "hook": HOOK, "servicio": SERVICIO, "crud": CRUD, **ESTILOS},
    ejemplo_proyecto="mi-web",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:5173"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_js.MARCADORES_VARIANTE,
)
