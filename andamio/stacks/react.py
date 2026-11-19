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

PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="página con sus estilos",
    ejemplo="Productos",
    formas=("@@Nombre@@Page",),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_js.validar_componente,
    marcadores=_js.MARCADORES_EXTENSION,
    existe_si=("src/pages/@@Nombre@@Page",),
    siguiente_paso=["# Mostrala en src/App.tsx:", "import { @@Nombre@@Page } from './pages/@@Nombre@@Page';"],
)

SERVICIO = Pieza(
    clave="servicio",
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API de Django",
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
        "# Necesita la API de Django andando (python manage.py runserver) con el recurso /api/@@plural@@/",
    ],
)

STACK = Stack(
    clave="react",
    titulo="React + Vite",
    senal="package.json con vite y react",
    detectar=_js.detectar_dependencias("vite", "react"),
    tipos=_js.TIPOS,
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "hook": HOOK, "servicio": SERVICIO},
    ejemplo_proyecto="mi-web",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:5173"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_js.MARCADORES_VARIANTE,
)
