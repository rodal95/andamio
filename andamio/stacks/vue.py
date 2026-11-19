"""Stack `vue`: aplicación web con Vue 3 + Vite + Vue Router, en JavaScript."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre, titulo
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

_VACIOS = {"str": "''", "text": "''", "email": "''", "date": "''", "datetime": "''", "int": "0", "decimal": "0", "float": "0", "bool": "false"}
_PASOS_NUMERICOS = {"int": "1", "decimal": "0.01", "float": "any"}
_TIPO_INPUT = {"email": "email", "date": "date", "datetime": "datetime-local"}

_COMPONENTES_OCUPADOS = {"App", "RouterLink", "RouterView", "Transition", "KeepAlive", "Teleport", "Suspense", "Component", "Slot"}
_COMPOSABLES_DE_VUE = {"useRoute", "useRouter", "useLink", "useAttrs", "useSlots", "useId", "useModel", "useTemplateRef", "useCssModule"}


def _validar_componente(raiz: Path, nombre: Nombre) -> None:
    if nombre.pascal in _COMPONENTES_OCUPADOS:
        raise AndamioError(f"'{nombre.pascal}' ya lo usa Vue o el proyecto.", "Elegí otro nombre.")


def _validar_composable(raiz: Path, nombre: Nombre) -> None:
    if f"use{nombre.pascal}" in _COMPOSABLES_DE_VUE:
        raise AndamioError(f"'use{nombre.pascal}' ya existe en Vue; si creás otro se confunden.", "Elegí otro nombre.")


def _leer_router(raiz: Path) -> str:
    try:
        return (raiz / "src" / "router.js").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return ""


def _validar_ruta(ruta: Callable[[Nombre], str]) -> Callable[[Path, Nombre], None]:
    def validar(raiz: Path, nombre: Nombre) -> None:
        _validar_componente(raiz, nombre)
        camino = ruta(nombre)
        if f"path: '{camino}'" in _leer_router(raiz):
            raise AndamioError(f"Ya hay una página en la ruta {camino} (src/router.js).", "Elegí otro nombre, o borrá esa ruta.")

    return validar


def _campo_formulario(campo) -> list[str]:
    n = campo.nombre
    if campo.tipo == "bool":
        control = f'<input v-model="datos.{n}" type="checkbox" />'
    elif campo.tipo == "text":
        control = f'<textarea v-model="datos.{n}" rows="3" required></textarea>'
    elif campo.tipo in _PASOS_NUMERICOS:
        control = f'<input v-model.number="datos.{n}" type="number" step="{_PASOS_NUMERICOS[campo.tipo]}" required />'
    else:
        control = f'<input v-model="datos.{n}" type="{_TIPO_INPUT.get(campo.tipo, "text")}" required />'
    return [
        '<label class="campo">',
        f"  {campo.titulo}",
        f"  {control}",
        f"  <small v-if=\"errores.{n}\" class=\"error\">{{{{ errores.{n}.join(' ') }}}}</small>",
        "</label>",
    ]


def _contexto_crud(sol: Solicitud) -> dict[str, str]:
    contexto = _js.contexto_servicio(sol)
    variable = sol.nombre.camel
    para_texto = next((c for c in sol.campos if c.tipo in ("str", "email")), None)
    detalle, formulario = [], []
    for c in sol.campos:
        valor = f"{variable}.{c.nombre}"
        detalle += [f"<dt>{c.titulo}</dt>", f"<dd>{{{{ {valor} ? 'Sí' : 'No' }}}}</dd>" if c.tipo == "bool" else f"<dd>{{{{ {valor} }}}}</dd>"]
        formulario += _campo_formulario(c)
    contexto.update(
        verbose_plural=" ".join(sol.nombre.plural_palabras),
        texto_item=f"item.{para_texto.nombre}" if para_texto else f"`{titulo(list(sol.nombre.palabras))} ${{item.id}}`",
        campos_detalle="\n".join(detalle),
        valores_vacios="\n".join(f"{c.nombre}: {_VACIOS[c.tipo]}," for c in sol.campos),
        # datetime-local espera "2025-03-15T10:30": se cortan los segundos y la zona horaria.
        campos_copiar="\n".join(f"{c.nombre}: registro.{c.nombre}{'.slice(0, 16)' if c.tipo == 'datetime' else ''}," for c in sol.campos),
        campos_formulario="\n".join(formulario),
    )
    return contexto


def _insercion(texto: str, marcador: str, descripcion: str, ubicacion: str) -> Insercion:
    archivo, comentario = ("src/App.vue", "<!--") if marcador == "enlaces" else ("src/router.js", "//")
    return Insercion(archivo, texto, marcador=marcador, descripcion=descripcion, ubicacion=ubicacion, comentario=comentario)


COMPONENTE = Pieza(
    clave="componente",
    titulo="Componente",
    descripcion="componente .vue con props, slot y sus estilos",
    ejemplo="Tarjeta",
    formas=("@@Nombre@@.vue",),
    validar_nombre=_validar_componente,
    existe_si=("src/components/@@Nombre@@.vue",),
    siguiente_paso=["# Usalo en una página (dentro de <script setup>):", "import @@Nombre@@ from '@/components/@@Nombre@@.vue';"],
)

PAGINA = Pieza(
    clave="pagina",
    titulo="Página",
    descripcion="página con su ruta y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@Nombre@@Page.vue", "ruta /@@nombreKebab@@"),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_ruta(lambda n: f"/{n.kebab}"),
    existe_si=("src/pages/@@Nombre@@Page.vue",),
    inserciones=(
        _insercion("import @@Nombre@@Page from './pages/@@Nombre@@Page.vue';", "imports", "import", "arriba, junto a los otros import"),
        _insercion("{ path: '/@@nombreKebab@@', component: @@Nombre@@Page },", "rutas", "ruta /@@nombreKebab@@", "dentro de la lista routes"),
        _insercion('<RouterLink to="/@@nombreKebab@@">@@nombreTitulo@@</RouterLink>', "enlaces", "enlace en el menú", "dentro de <nav>"),
    ),
    siguiente_paso=["npm run dev", "http://localhost:5173/@@nombreKebab@@"],
)

COMPOSABLE = Pieza(
    clave="composable",
    titulo="Composable",
    descripcion="función use... para reutilizar estado y lógica (como un hook de React)",
    ejemplo="contador",
    formas=("use@@Nombre@@",),
    ajustar_palabras=_js.sin_prefijo_use,
    validar_nombre=_validar_composable,
    existe_si=("src/composables/use@@Nombre@@.js",),
    siguiente_paso=["# Usalo en un componente (dentro de <script setup>):", "import { use@@Nombre@@ } from '@/composables/use@@Nombre@@';"],
)

SERVICIO = Pieza(
    clave="servicio",
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API (Django, FastAPI, Express o Next.js)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@nombreCamel@@Service",),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_servicio,
    marcadores=_js.MARCADORES_SERVICIO,
    existe_si=("src/services/@@nombreCamel@@Service.js",),
    si_no_existe=frozenset({"src/services/http.js"}),
    siguiente_paso=[
        "# Usalo en un componente:",
        "import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';",
        "# Necesita la API andando con el recurso /api/@@plural@@/ (VITE_API_URL en el .env).",
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
    contexto=_contexto_crud,
    validar_nombre=_validar_ruta(lambda n: "/" + "-".join(n.plural_palabras)),
    marcadores={
        **_js.MARCADORES_SERVICIO,
        "verbose_plural": "plural en minúsculas y con espacios",
        "texto_item": "lo que se muestra de cada registro en la lista: item.nombre",
        "campos_detalle": "un <dt> y un <dd> por campo",
        "valores_vacios": "valores iniciales del formulario: nombre: '',",
        "campos_copiar": "copia un registro de la API a los datos del formulario",
        "campos_formulario": "un <label> con su control (v-model) y su error, por campo",
    },
    existe_si=("src/pages/@@pluralKebab@@",),
    si_no_existe=frozenset({"src/services/http.js", "src/services/@@nombreCamel@@Service.js"}),
    inserciones=(
        _insercion(
            "import @@Nombre@@ListaPage from './pages/@@pluralKebab@@/@@Nombre@@ListaPage.vue';\n"
            "import @@Nombre@@DetallePage from './pages/@@pluralKebab@@/@@Nombre@@DetallePage.vue';\n"
            "import @@Nombre@@FormPage from './pages/@@pluralKebab@@/@@Nombre@@FormPage.vue';",
            "imports",
            "import",
            "arriba, junto a los otros import",
        ),
        _insercion(
            "{ path: '/@@pluralKebab@@', component: @@Nombre@@ListaPage },\n"
            "{ path: '/@@pluralKebab@@/nuevo', component: @@Nombre@@FormPage },\n"
            "{ path: '/@@pluralKebab@@/:id', component: @@Nombre@@DetallePage },\n"
            "{ path: '/@@pluralKebab@@/:id/editar', component: @@Nombre@@FormPage },",
            "rutas",
            "rutas /@@pluralKebab@@",
            "dentro de la lista routes",
        ),
        _insercion('<RouterLink to="/@@pluralKebab@@">@@titulo@@</RouterLink>', "enlaces", "enlace en el menú", "dentro de <nav>"),
    ),
    siguiente_paso=[
        "npm run dev",
        "http://localhost:5173/@@pluralKebab@@",
        "# Necesita la API andando (Django, FastAPI, Express o Next.js full stack), con el recurso /api/@@plural@@/ generado con los mismos campos.",
    ],
)

STACK = Stack(
    clave="vue",
    titulo="Vue + Vite",
    senal="package.json con vite y vue",
    detectar=_js.detectar_dependencias("vite", "vue"),
    tipos=_js.TIPOS,
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "composable": COMPOSABLE, "servicio": SERVICIO, "crud": CRUD},
    ejemplo_proyecto="mi-web",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:5173"],
    contexto_env=lambda: {},
)
