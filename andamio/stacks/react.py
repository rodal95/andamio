"""Stack `react`: aplicación web con React + Vite + TypeScript."""

from __future__ import annotations

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


def _validar_pagina(raiz, nombre) -> None:
    _js.validar_componente(raiz, nombre)
    _RUTA_PAGINA(raiz, nombre)


def _insercion_app(texto: str, marcador: str, descripcion: str, ubicacion: str, comentario: str) -> Insercion:
    return Insercion("src/App.@@extx@@", texto, marcador=marcador, descripcion=descripcion, ubicacion=ubicacion, comentario=comentario)


PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="página con su ruta y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@Nombre@@Page",),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_pagina,
    marcadores=_js.MARCADORES_EXTENSION,
    existe_si=("src/pages/@@Nombre@@Page",),
    inserciones=(
        _insercion_app("import { @@Nombre@@Page } from './pages/@@Nombre@@Page';", "imports", "import", "arriba, junto a los otros import", "//"),
        _insercion_app('<Route path="/@@nombreKebab@@" element={<@@Nombre@@Page />} />', "rutas", "ruta /@@nombreKebab@@", "dentro de <Routes>", "{/*"),
        _insercion_app('<Link to="/@@nombreKebab@@">@@nombreTitulo@@</Link>', "enlaces", "enlace en el menú", "dentro de <nav>", "{/*"),
    ),
    siguiente_paso=_js.pasos_router(["npm run dev", "http://localhost:5173/@@nombreKebab@@"]),
)

_RUTA_CRUD = _js.validar_ruta_libre(lambda nombre: "/" + "-".join(nombre.plural_palabras))


def _validar_crud(raiz, nombre) -> None:
    _js.validar_componente(raiz, nombre)
    _RUTA_CRUD(raiz, nombre)


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
    marcadores=_js.MARCADORES_CRUD,
    existe_si=("src/pages/@@pluralKebab@@", "src/components/@@Nombre@@Detalle"),
    si_no_existe=frozenset(
        {
            "src/services/http.ts",
            "src/services/http.js",
            "src/services/@@nombreCamel@@Service.ts",
            "src/services/@@nombreCamel@@Service.js",
            "src/hooks/useConsulta.ts",
            "src/hooks/useConsulta.js",
        }
    ),
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
            "# Necesita la API andando (Django o FastAPI), con el recurso /api/@@plural@@/ generado con los mismos campos.",
        ]
    ),
)

SERVICIO = Pieza(
    clave="servicio",
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API (Django o FastAPI)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "@@nombreCamel@@Service"),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_servicio,
    marcadores=_js.MARCADORES_SERVICIO,
    existe_si=("src/services/@@nombreCamel@@Service.@@ext@@",),
    si_no_existe=frozenset({"src/services/http.ts", "src/services/http.js"}),
    siguiente_paso=[
        "# Usalo en un componente:",
        "import { @@nombreCamel@@Service } from './services/@@nombreCamel@@Service';",
        "# Necesita la API andando (Django o FastAPI) con el recurso /api/@@plural@@/",
    ],
)

STACK = Stack(
    clave="react",
    titulo="React + Vite",
    senal="package.json con vite y react",
    detectar=_js.detectar_dependencias("vite", "react"),
    tipos=_js.TIPOS,
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "hook": HOOK, "servicio": SERVICIO, "crud": CRUD},
    ejemplo_proyecto="mi-web",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:5173"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_js.MARCADORES_VARIANTE,
)
