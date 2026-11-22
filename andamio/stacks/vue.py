"""Stack `vue`: aplicación web con Vue 3 + Vite + Vue Router, en JavaScript."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre, titulo
from andamio.estilos import piezas_de_estilos
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
        # --protegido: crear y editar piden ingresar (la lista y el detalle son libres, como en Django).
        meta_protegida=_meta_protegida(sol),
    )
    return contexto


def _insercion(texto: str, marcador: str, descripcion: str, ubicacion: str, condicion=None) -> Insercion:
    if marcador == "enlaces":
        # El menú está en TheNavbar.vue; en los proyectos anteriores (sin TheNavbar), en App.vue.
        return Insercion(
            "src/components/TheNavbar.vue",
            texto,
            marcador="enlaces",
            descripcion=descripcion,
            ubicacion=ubicacion,
            comentario="<!--",
            condicion=condicion,
            alternativa=Insercion("src/App.vue", texto, marcador="enlaces", descripcion=descripcion, ubicacion=ubicacion, comentario="<!--", condicion=condicion),
        )
    return Insercion("src/router.js", texto, marcador=marcador, descripcion=descripcion, ubicacion=ubicacion, comentario="//", condicion=condicion)


# --- Páginas protegidas (--protegido) y login (nuevo login) ---------------------------------


def _con_login(raiz: Path) -> bool:
    return (raiz / "src" / "sesion" / "sesion.js").is_file()


def _meta_protegida(sol: Solicitud) -> str:
    """--protegido: la ruta lleva meta: { protegida: true } (el router pide ingresar)."""
    if not sol.opciones.get("protegido"):
        return ""
    if not _con_login(sol.raiz):
        raise AndamioError(
            "--protegido usa la sesión (src/sesion/), que genera el login, y todavía no está.",
            "Generá primero el login: python -m andamio nuevo login",
        )
    return ", meta: { protegida: true }"


def _contexto_pagina(sol: Solicitud) -> dict[str, str]:
    return {"meta_protegida": _meta_protegida(sol)}


def _enlace_publico(sol: Solicitud) -> bool:
    return not sol.opciones.get("protegido")


def _enlace_con_sesion(sol: Solicitud) -> bool:
    return bool(sol.opciones.get("protegido"))


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
    lectura=(
        ('src/pages/@@Nombre@@Page.vue', 'la página'),
        ('src/router.js', 'su ruta'),
    ),
    titulo="Página",
    descripcion="página con su ruta y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@Nombre@@Page.vue", "ruta /@@nombreKebab@@"),
    opciones=frozenset({"protegido"}),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_ruta(lambda n: f"/{n.kebab}"),
    contexto=_contexto_pagina,
    marcadores={"meta_protegida": "con --protegido: meta: { protegida: true } en la ruta (vacío si no)"},
    existe_si=("src/pages/@@Nombre@@Page.vue",),
    inserciones=(
        _insercion("import @@Nombre@@Page from './pages/@@Nombre@@Page.vue';", "imports", "import", "arriba, junto a los otros import"),
        _insercion("{ path: '/@@nombreKebab@@', component: @@Nombre@@Page@@meta_protegida@@ },", "rutas", "ruta /@@nombreKebab@@", "dentro de la lista routes"),
        _insercion('<RouterLink to="/@@nombreKebab@@">@@nombreTitulo@@</RouterLink>', "enlaces", "enlace en el menú", "dentro de <nav>", _enlace_publico),
        # Una página protegida: su enlace se ve solo si alguien ingresó (en el menú de la sesión).
        Insercion(
            "src/components/MenuSesion.vue",
            '<RouterLink to="/@@nombreKebab@@">@@nombreTitulo@@</RouterLink>',
            marcador="enlaces_sesion",
            descripcion="enlace en el menú, solo con sesión",
            ubicacion="dentro de MenuSesion, antes del nombre del usuario",
            comentario="<!--",
            condicion=_enlace_con_sesion,
            alternativa=_insercion('<RouterLink to="/@@nombreKebab@@">@@nombreTitulo@@</RouterLink>', "enlaces", "enlace en el menú", "dentro de <nav>"),
        ),
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
    lectura=(
        ('src/services/@@nombreCamel@@Service.js', 'las funciones para usar /api/@@plural@@/'),
        ('src/services/http.js', 'lo común a todas las llamadas: dirección de la API y errores'),
    ),
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
    **_js.OPCION_SOLO,
    siguiente_paso=[
        "# Usalo en un componente:",
        "import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';",
        "# Necesita la API andando con el recurso /api/@@plural@@/ (VITE_API_URL en el .env).",
    ],
)

CRUD = Pieza(
    clave="crud",
    lectura=(
        ('src/services/@@nombreCamel@@Service.js', 'cómo se habla con la API (/api/@@plural@@/)'),
        ('src/pages/@@pluralKebab@@/@@Nombre@@ListaPage.vue', 'la lista'),
        ('src/pages/@@pluralKebab@@/@@Nombre@@DetallePage.vue', 'el detalle (con eliminar)'),
        ('src/pages/@@pluralKebab@@/@@Nombre@@FormPage.vue', 'el formulario para crear y editar'),
        ('src/router.js', 'las rutas /@@pluralKebab@@'),
    ),
    titulo="CRUD completo",
    descripcion="lista, detalle y formulario conectados a la API, con sus rutas",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "ruta /@@pluralKebab@@"),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"protegido"}),
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
        "meta_protegida": "con --protegido: meta: { protegida: true } en las rutas de crear y editar",
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
            "{ path: '/@@pluralKebab@@/nuevo', component: @@Nombre@@FormPage@@meta_protegida@@ },\n"
            "{ path: '/@@pluralKebab@@/:id', component: @@Nombre@@DetallePage },\n"
            "{ path: '/@@pluralKebab@@/:id/editar', component: @@Nombre@@FormPage@@meta_protegida@@ },",
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

def _con_registro(sol: Solicitud) -> bool:
    return not sol.opciones.get("sin_registro")


def _contexto_login(sol: Solicitud) -> dict[str, str]:
    registro = _con_registro(sol)
    try:
        avisa = "alVencerLaSesion" in (sol.raiz / "src" / "services" / "http.js").read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        avisa = True  # se crea ahora (y avisa)
    except (OSError, UnicodeDecodeError):
        avisa = False
    explicacion = ["// Si la API responde 401 a un pedido con el token (venció), se cierra la sesión."] if sol.guia else []
    obligatorio = bool(sol.opciones.get("obligatorio"))
    if obligatorio:
        regla = [
            "// Todas las páginas piden ingresar (nuevo login --obligatorio), salvo las de meta.publica.",
            "if (!destino.meta.publica && !sesion.usuario) {",
        ]
    else:
        regla = ["// Las páginas con meta: { protegida: true } (nuevo pagina X --protegido) piden ingresar.", "if (destino.meta.protegida && !sesion.usuario) {"]
    guardia = [
        "",
        "// Antes de cada página: espera a saber si hay sesión, y si la página pide ingresar y nadie",
        "// ingresó, lleva a /ingresar (y después vuelve: ?desde=).",
        "router.beforeEach(async (destino) => {",
        "  await sesionLista();",
        *[f"  {linea}" for linea in regla],
        "    return { path: '/ingresar', query: { desde: destino.fullPath } };",
        "  }",
        "  return true;",
        "});",
    ]
    meta = "meta: { publica: true, sinMenu: true }" if obligatorio else "meta: { publica: true }"
    return {
        "importar_http": "alVencerLaSesion, leerToken" if avisa else "leerToken",
        "al_vencer": "\n".join([*explicacion, "alVencerLaSesion(() => {", "  estado.usuario = null;", "});", ""]) if avisa else "",
        "router_ingresar": "RouterLink, useRoute, useRouter" if registro else "useRoute, useRouter",
        "pie_ingresar": "<p>¿No tenés cuenta? <RouterLink :to=\"{ path: '/registro', query: ruta.query }\">Registrate</RouterLink></p>" if registro else "",
        "enlace_registro": '<RouterLink to="/registro">Registrarse</RouterLink>' if registro else "",
        "y_registrarse": " y Registrarse" if registro else "",
        "guardia_router": "\n".join(guardia),
        "meta_publica": meta,
    }


def _registro_a_omitir(sol: Solicitud) -> frozenset[str]:
    return frozenset() if _con_registro(sol) else frozenset({"src/pages/RegistroPage.vue"})


def _validar_login(raiz: Path, nombre: Nombre) -> None:
    if nombre.snake != "sesion":
        raise AndamioError(
            "En Vue el login no lleva nombre: genera src/sesion/ y las páginas /ingresar y /registro.",
            "Ejemplo: python -m andamio nuevo login",
        )
    if _con_login(raiz):
        raise AndamioError("El proyecto ya tiene el login (src/sesion/).", "Para que una página pida ingresar: python -m andamio nuevo pagina Perfil --protegido")


LOGIN = Pieza(
    clave="login",
    lectura=(
        ("src/services/authService.js", "pide el token a la API, crea usuarios y pregunta quién ingresó (/api/yo/)"),
        ("src/sesion/sesion.js", "la sesión: sesion.usuario (quién ingresó), ingresar, registrarse y salir"),
        ("src/router.js", "las rutas /ingresar y /registro, y el control antes de cada página (al final)"),
        ("src/pages/IngresarPage.vue", "el formulario para ingresar"),
        ("src/pages/RegistroPage.vue", "el formulario para crear una cuenta"),
        ("src/components/MenuSesion.vue", "Ingresar, o quién ingresó y Salir, en el menú"),
        ("src/services/http.js", "guarda el token y lo manda en cada pedido; un 401 cierra la sesión"),
    ),
    titulo="Login",
    descripcion="ingresar y crear una cuenta con la API (token JWT), y páginas que piden ingresar (--protegido)",
    ejemplo="",
    nombre_defecto="sesion",
    formas=("src/@@nombre@@/ (rutas /ingresar y /registro)",),
    opciones=frozenset({"sin_registro", "obligatorio"}),
    validar_nombre=_validar_login,
    contexto=_contexto_login,
    marcadores={
        "importar_http": "lo que la sesión toma de http: leerToken (y alVencerLaSesion, si http lo tiene)",
        "al_vencer": "cerrar la sesión cuando la API responde 401 (vacío si http es de una versión anterior)",
        "router_ingresar": "lo que IngresarPage toma de vue-router (RouterLink, solo con registro)",
        "pie_ingresar": "el enlace a /registro debajo del formulario (vacío con --sin-registro)",
        "enlace_registro": "Registrarse en el menú (vacío con --sin-registro)",
        "y_registrarse": "' y Registrarse', para el comentario del menú (vacío con --sin-registro)",
        "guardia_router": "router.beforeEach: espera la sesión y pide ingresar donde corresponde",
        "meta_publica": "el meta de /ingresar y /registro (con --obligatorio, también sinMenu: se ven solas)",
    },
    existe_si=("src/sesion",),
    si_no_existe=frozenset({"src/services/http.js"}),
    omitir=_registro_a_omitir,
    inserciones=(
        _insercion("import { sesion, sesionLista } from './sesion/sesion';", "imports", "import de la sesión", "arriba, junto a los otros import"),
        _insercion("import IngresarPage from './pages/IngresarPage.vue';", "imports", "import de IngresarPage", "arriba, junto a los otros import"),
        _insercion("import RegistroPage from './pages/RegistroPage.vue';", "imports", "import de RegistroPage", "arriba, junto a los otros import", _con_registro),
        _insercion("{ path: '/ingresar', component: IngresarPage, @@meta_publica@@ },", "rutas", "ruta /ingresar", "dentro de la lista routes"),
        _insercion("{ path: '/registro', component: RegistroPage, @@meta_publica@@ },", "rutas", "ruta /registro", "dentro de la lista routes", _con_registro),
        Insercion("src/router.js", "@@guardia_router@@", descripcion="el control antes de cada página (al final)"),
        Insercion(
            "src/components/TheNavbar.vue",
            "import MenuSesion from './MenuSesion.vue';",
            marcador="imports_navbar",
            descripcion="import de MenuSesion",
            ubicacion="en <script setup>, junto a los otros import",
            comentario="//",
            alternativa=Insercion(
                "src/App.vue",
                "import MenuSesion from './components/MenuSesion.vue';",
                marcador="imports_app",
                descripcion="import de MenuSesion",
                ubicacion="en <script setup> de App.vue, junto a los otros import",
                comentario="//",
            ),
        ),
        _insercion("<MenuSesion />", "enlaces", "la sesión en el menú", "dentro de <nav>"),
    ),
    siguiente_paso=[
        "# La API con el login (Django, FastAPI o Express): python -m andamio nuevo login",
        "npm run dev",
        "http://localhost:5173/ingresar",
        "# Para que una página pida ingresar:",
        "python -m andamio nuevo pagina Perfil --protegido",
    ],
)

ESTILOS = piezas_de_estilos(
    "src",
    lambda ruta: Insercion(
        "src/main.js",
        f"import './{ruta}';",
        marcador="estilos",
        descripcion="import del CSS",
        ubicacion="junto a import './estilos.css'",
        comentario="//",
    ),
    'Usá las clases en tus componentes: class="...".',
)

STACK = Stack(
    clave="vue",
    titulo="Vue + Vite",
    senal="package.json con vite y vue",
    detectar=_js.detectar_dependencias("vite", "vue"),
    tipos=_js.TIPOS,
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "composable": COMPOSABLE, "servicio": SERVICIO, "crud": CRUD, "login": LOGIN, **ESTILOS},
    ejemplo_proyecto="mi-web",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:5173"],
    contexto_env=lambda: {},
)
