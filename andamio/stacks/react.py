"""Stack `react`: aplicación web con React + Vite + TypeScript."""

from __future__ import annotations

from pathlib import Path

from andamio.estilos import piezas_de_estilos
from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

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


# Con --protegido (pagina o crud): RutaProtegida, que generó el login. Si ya está importado
# (otra página protegida), no se repite.
_IMPORT_RUTA_PROTEGIDA = _insercion_app(
    "import { RutaProtegida } from './sesion';", "imports", "import de RutaProtegida", "arriba, junto a los otros import", "//", _js.con_protegido
)


def _sin_uno(sol) -> bool:
    return not sol.opciones.get("uno")


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
    opciones=frozenset({"datos", "uno", "form", "protegido"}),
    normalizar_opcion={"datos": _js.normalizar_datos},
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_pagina,
    contexto=_js.contexto_pagina,
    marcadores={**_js.MARCADORES_EXTENSION, **_js.MARCADORES_PAGINA},
    existe_si=("src/pages/@@Nombre@@Page",),
    # Con --datos se crea el hook que usa, y si ya existe (lo generó un crud o un servicio) no se toca.
    si_no_existe=_HOOKS,
    omitir=_js.hooks_a_omitir("src/hooks", "src/services"),
    inserciones=(
        _insercion_app("import { @@Nombre@@Page } from './pages/@@Nombre@@Page';", "imports", "import", "arriba, junto a los otros import", "//"),
        _IMPORT_RUTA_PROTEGIDA,
        _insercion_app('<Route path="@@ruta_pagina@@" element={@@elemento_pagina@@} />', "rutas", "ruta @@ruta_pagina@@", "dentro de <Routes>", "{/*"),
        # El formulario (--form) también edita: la misma página con el id en la ruta. Salvo
        # que el servicio no tenga obtener o actualizar (--solo crear): entonces solo envía.
        _insercion_app(
            '<Route path="@@ruta_pagina@@/:id" element={@@elemento_pagina@@} />',
            "rutas",
            "ruta @@ruta_pagina@@/:id (editar)",
            "dentro de <Routes>",
            "{/*",
            _js.form_edita,
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
    # --protegido: nuevo y editar piden ingresar (como en Django: ver es libre).
    opciones=frozenset({"protegido"}),
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
        _IMPORT_RUTA_PROTEGIDA,
        _insercion_app(
            '<Route path="/@@pluralKebab@@" element={<@@Nombre@@ListaPage />} />\n'
            '<Route path="/@@pluralKebab@@/nuevo" element={@@elemento_form@@} />\n'
            '<Route path="/@@pluralKebab@@/:id" element={<@@Nombre@@DetallePage />} />\n'
            '<Route path="/@@pluralKebab@@/:id/editar" element={@@elemento_form@@} />',
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
    # Con --solo crear (ej.: un formulario de contacto) no hacen falta los hooks.
    omitir=_js.hooks_del_servicio("src/hooks"),
    **_js.OPCION_SOLO,
    siguiente_paso=_js.pasos_servicio(
        "pagina",
        ("@@Nombre@@Lista", "@@Nombre@@Detalle", "@@Nombre@@Editar", "@@Nombre@@"),
        [
            "# O a mano, en un componente:",
            "import { @@nombreCamel@@Service } from './services/@@nombreCamel@@Service';",
            "# Necesita la API andando (Django, FastAPI o Express) con el recurso /api/@@plural@@/",
        ],
        con_listar=[
            "import { useConsulta } from './hooks/useConsulta';",
            "const { datos, cargando, error } = useConsulta(@@nombreCamel@@Service.listar);",
        ],
    ),
)

# --- Login (contra la API de Django: python -m andamio nuevo login) ---------------------


def _http_avisa_vencimiento(sol: Solicitud) -> bool:
    """Si src/services/http avisa cuando el token vence (las versiones anteriores, no).
    Si no existe, se crea ahora (y avisa)."""
    ext = _js.MARCADORES_VARIANTE[sol.variante or "ts"]["ext"]
    try:
        return "alVencerLaSesion" in (sol.raiz / "src" / "services" / f"http.{ext}").read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return True
    except (OSError, UnicodeDecodeError):
        return False


def _con_registro(sol: Solicitud) -> bool:
    return not sol.opciones.get("sin_registro")


def _contexto_login(sol: Solicitud) -> dict[str, str]:
    registro = _con_registro(sol)
    avisa = _http_avisa_vencimiento(sol)
    explicacion = (
        ["// Si la API responde 401 a un pedido con el token (venció), se cierra la sesión: las", "// páginas protegidas llevan a /ingresar."]
        if sol.guia
        else []
    )
    return {
        "importar_http": "alVencerLaSesion, leerToken" if avisa else "leerToken",
        "al_vencer": "\n".join([*explicacion, "alVencerLaSesion(() => cambiar({ usuario: null, cargando: false }));", ""]) if avisa else "",
        "router_ingresar": "Link, Navigate, useLocation" if registro else "Navigate, useLocation",
        "pie_ingresar": "\n".join(["<p>", "  ¿No tenés cuenta?{' '}", "  <Link to=\"/registro\" state={{ desde }}>", "    Registrate", "  </Link>", "</p>"])
        if registro
        else "",
        "enlace_registro": '<Link to="/registro">Registrarse</Link>' if registro else "",
        "y_registrarse": " y Registrarse" if registro else "",
    }


def _validar_login(raiz: Path, nombre: Nombre) -> None:
    if nombre.snake != "sesion":
        raise AndamioError(
            "En React el login no lleva nombre: genera src/sesion/ y las páginas /ingresar y /registro.",
            f"Ejemplo: {consola.programa()} nuevo login",
        )
    _RUTAS_LOGIN(raiz, nombre)
    _COMPONENTES_LOGIN(raiz, nombre)


_RUTAS_LOGIN = _js.validar_ruta_libre(lambda nombre: "/ingresar")
_COMPONENTES_LOGIN = _js.validar_componentes_libres(lambda nombre: ["IngresarPage", "RegistroPage", "MenuSesion", "RutaProtegida"])


def _registro_a_omitir(sol: Solicitud) -> frozenset[str]:
    if _con_registro(sol):
        return frozenset()
    return frozenset(
        f"src/pages/RegistroPage/{archivo}"
        for archivo in ("RegistroPage.tsx", "RegistroPage.jsx", "RegistroPage.module.css", "index.ts", "index.js")
    )


def _pasos_login(sol: Solicitud) -> list[str]:
    pasos = [
        "# La API de Django con el login (en la carpeta de la API): python -m andamio nuevo login",
        "npm run dev",
        "http://localhost:5173/ingresar",
        "# Para que una página pida ingresar:",
        "python -m andamio nuevo pagina Perfil --protegido",
    ]
    if not _http_avisa_vencimiento(sol):
        pasos += [
            "# Tu src/services/http es de una versión anterior: cuando el token vence (60 minutos),",
            "# las páginas muestran el error 401 en lugar de volver a pedir el ingreso. Para eso, agregale",
            "# alVencerLaSesion y el control del 401, como en un proyecto nuevo (python -m andamio crear react prueba).",
        ]
    return pasos


LOGIN = Pieza(
    clave="login",
    lectura=(
        ("src/services/authService.@@ext@@", "pide el token a la API, crea usuarios y pregunta quién ingresó (/api/yo/)"),
        ("src/sesion/sesion.@@ext@@", "la sesión: useSesion() (quién ingresó), ingresar, registrarse y salir"),
        ("src/sesion/RutaProtegida.@@extx@@", "si nadie ingresó, lleva a /ingresar (y después vuelve)"),
        ("src/pages/IngresarPage/IngresarPage.@@extx@@", "el formulario para ingresar"),
        ("src/pages/RegistroPage/RegistroPage.@@extx@@", "el formulario para crear una cuenta"),
        ("src/sesion/MenuSesion.@@extx@@", "Ingresar, o quién ingresó y Salir, en el menú"),
        ("src/services/http.@@ext@@", "guarda el token y lo manda en cada pedido; un 401 cierra la sesión"),
        ("src/App.@@extx@@", "las rutas /ingresar y /registro, y la sesión en el menú"),
    ),
    titulo="Login",
    descripcion="ingresar y crear una cuenta con la API de Django (token JWT), y rutas protegidas (--protegido)",
    ejemplo="",
    nombre_defecto="sesion",
    formas=("src/@@nombre@@/ (rutas /ingresar y /registro)",),
    opciones=frozenset({"sin_registro"}),
    validar_nombre=_validar_login,
    contexto=_contexto_login,
    marcadores={
        **_js.MARCADORES_EXTENSION,
        "importar_http": "lo que la sesión toma de http: leerToken (y alVencerLaSesion, si http lo tiene)",
        "al_vencer": "cerrar la sesión cuando la API responde 401 (vacío si http es de una versión anterior)",
        "router_ingresar": "lo que IngresarPage toma de react-router (Link, solo con registro)",
        "pie_ingresar": "el enlace a /registro debajo del formulario (vacío con --sin-registro)",
        "enlace_registro": "Registrarse en el menú (vacío con --sin-registro)",
        "y_registrarse": "' y Registrarse', para el comentario del menú (vacío con --sin-registro)",
    },
    existe_si=("src/sesion",),
    si_no_existe=frozenset({"src/services/http.ts", "src/services/http.js"}),
    omitir=_registro_a_omitir,
    inserciones=(
        _insercion_app("import { IngresarPage } from './pages/IngresarPage';", "imports", "import de IngresarPage", "arriba, junto a los otros import", "//"),
        _insercion_app(
            "import { RegistroPage } from './pages/RegistroPage';", "imports", "import de RegistroPage", "arriba, junto a los otros import", "//", _con_registro
        ),
        _insercion_app("import { MenuSesion } from './sesion';", "imports", "import de MenuSesion", "arriba, junto a los otros import", "//"),
        _insercion_app('<Route path="/ingresar" element={<IngresarPage />} />', "rutas", "ruta /ingresar", "dentro de <Routes>", "{/*"),
        _insercion_app('<Route path="/registro" element={<RegistroPage />} />', "rutas", "ruta /registro", "dentro de <Routes>", "{/*", _con_registro),
        _insercion_app("<MenuSesion />", "enlaces", "la sesión en el menú", "dentro de <nav>", "{/*"),
    ),
    siguiente_paso=_pasos_login,
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
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "hook": HOOK, "servicio": SERVICIO, "crud": CRUD, "login": LOGIN, **ESTILOS},
    ejemplo_proyecto="mi-web",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:5173"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_js.MARCADORES_VARIANTE,
)
