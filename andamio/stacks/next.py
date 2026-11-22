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

from andamio.estilos import piezas_de_estilos
from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre, pluralizar
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


def _enlace(texto: str, condicion=None) -> Insercion:
    """El enlace en el menú (components/Navbar). En los proyectos anteriores, sin Navbar, el
    menú está en app/layout."""
    return Insercion(
        "components/Navbar/Navbar.@@extx@@",
        texto,
        marcador="enlaces",
        descripcion="enlace en el menú",
        ubicacion="dentro de <nav>",
        comentario="{/*",
        condicion=condicion,
        alternativa=Insercion(
            "app/layout.@@extx@@", texto, marcador="enlaces", descripcion="enlace en el menú", ubicacion="dentro de <nav>", comentario="{/*"
        ),
    )


# --- --protegido (pagina y crud): un layout de la carpeta con RutaProtegida, del login ------


def _protegido(sol: Solicitud) -> bool:
    return bool(sol.opciones.get("protegido"))


def _publico(sol: Solicitud) -> bool:
    return not _protegido(sol)


def _validar_protegido(sol: Solicitud) -> None:
    if _protegido(sol) and not any((sol.raiz / "sesion" / f"RutaProtegida.{ext}").is_file() for ext in ("tsx", "jsx")):
        raise AndamioError(
            "--protegido usa RutaProtegida (sesion/), que genera el login, y todavía no está.",
            f"Generá primero el login: {consola.programa()} nuevo login",
        )


def _lectura_protegido(sol: Solicitud, carpeta: str) -> str:
    """Para el orden de lectura: el layout de --protegido (vacío si no se pidió)."""
    return f"{carpeta}/layout.{_js.MARCADORES_VARIANTE[sol.variante or 'ts']['extx']}" if _protegido(sol) else ""


def _contexto_pagina(sol: Solicitud) -> dict[str, str]:
    _validar_protegido(sol)
    return {"lectura_protegido": _lectura_protegido(sol, f"app/{sol.nombre.kebab}")}


def _contexto_crud(sol: Solicitud) -> dict[str, str]:
    _validar_protegido(sol)
    # contexto_crud es el de React (con <RutaProtegida> en las rutas de App): acá se protege
    # con un layout, así que se calcula sin --protegido.
    contexto = _js.contexto_crud(dataclasses.replace(sol, opciones={**sol.opciones, "protegido": False}))
    contexto["lectura_protegido"] = _lectura_protegido(sol, f"app/{'-'.join(sol.nombre.plural_palabras)}/nuevo")
    return contexto


_MARCADOR_LECTURA = {"lectura_protegido": "con --protegido: el layout que pide ingresar, para el orden de lectura (vacío si no)"}


def _layouts_a_omitir(*rutas: str):
    """Pieza.omitir: los layout.* de --protegido, si no se pidió."""

    def omitir(sol: Solicitud) -> frozenset[str]:
        return frozenset() if _protegido(sol) else frozenset(f"{r}/layout.{x}" for r in rutas for x in ("tsx", "jsx"))

    return omitir


def _enlace_con_sesion(texto: str) -> Insercion:
    """El enlace de una página --protegido: en el menú de la sesión (solo se ve si alguien
    ingresó). Si MenuSesion no tiene el marcador, en el menú."""
    return Insercion(
        "sesion/MenuSesion.@@extx@@",
        texto,
        marcador="enlaces_sesion",
        descripcion="enlace en el menú, solo con sesión",
        ubicacion="dentro de MenuSesion, antes del nombre del usuario",
        comentario="{/*",
        condicion=_protegido,
        alternativa=_enlace(texto),
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
    lectura=(
        ('app/@@nombreKebab@@/page.@@extx@@', 'la página (/@@nombreKebab@@)'),
        ('@@lectura_protegido@@', 'con --protegido: la envuelve con RutaProtegida (pide ingresar)'),
        ('components/Navbar/Navbar.@@extx@@', 'el enlace en el menú'),
    ),
    titulo="Página",
    descripcion="página con su ruta y su enlace en el menú",
    ejemplo="Contacto",
    formas=("@@Nombre@@Page", "ruta /@@nombreKebab@@"),
    ajustar_palabras=_js.sin_sufijo("page", "pagina"),
    validar_nombre=_validar_pagina,
    opciones=frozenset({"protegido"}),
    contexto=_contexto_pagina,
    marcadores={**_MARCADORES, **_MARCADOR_LECTURA},
    existe_si=("app/@@nombreKebab@@",),
    omitir=_layouts_a_omitir("app/@@nombreKebab@@"),
    inserciones=(
        _enlace('<Link href="/@@nombreKebab@@">@@nombreTitulo@@</Link>', _publico),
        _enlace_con_sesion('<Link href="/@@nombreKebab@@">@@nombreTitulo@@</Link>'),
    ),
    siguiente_paso=["npm run dev", "http://localhost:3000/@@nombreKebab@@"],
)

SERVICIO = Pieza(
    clave="servicio",
    lectura=(
        ('services/@@nombreCamel@@Service.@@ext@@', 'las funciones para usar /api/@@plural@@/'),
        ('services/http.@@ext@@', 'lo común a todas las llamadas: dirección de la API y errores'),
    ),
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
    **_js.OPCION_SOLO,
    siguiente_paso=[
        "# Usalo en un componente que empiece con 'use client':",
        "import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';",
        "# Necesita la API andando (Django, FastAPI o Express) con el recurso /api/@@plural@@/",
    ],
)

CRUD = Pieza(
    clave="crud",
    lectura=(
        ('services/@@nombreCamel@@Service.@@ext@@', 'cómo se habla con la API (/api/@@plural@@/)'),
        ('app/@@pluralKebab@@/page.@@extx@@', 'la lista (/@@pluralKebab@@)'),
        ('components/@@Nombre@@Detalle/@@Nombre@@Detalle.@@extx@@', 'muestra uno y avisa con onEditar / onEliminar'),
        ('app/@@pluralKebab@@/[id]/page.@@extx@@', 'la página del detalle (con eliminar)'),
        ('app/@@pluralKebab@@/@@Nombre@@Formulario.@@extx@@', 'el formulario, que usan nuevo y editar'),
        ('@@lectura_protegido@@', 'con --protegido: agregar y editar piden ingresar (RutaProtegida)'),
    ),
    titulo="CRUD completo",
    descripcion="lista, detalle y formulario conectados a la API, con sus rutas",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "ruta /@@pluralKebab@@"),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"protegido"}),
    contexto=_contexto_crud,
    validar_nombre=_validar_crud,
    marcadores={**_js.MARCADORES_CRUD, **_MARCADORES, **_MARCADOR_LECTURA},
    existe_si=("app/@@pluralKebab@@", "components/@@Nombre@@Detalle"),
    omitir=_layouts_a_omitir("app/@@pluralKebab@@/nuevo", "app/@@pluralKebab@@/[id]/editar"),
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


# --- Login (nuevo login): contra la API de Django, FastAPI o Express ----------------------


def _con_registro(sol: Solicitud) -> bool:
    return not sol.opciones.get("sin_registro")


def _obligatorio(sol: Solicitud) -> bool:
    return bool(sol.opciones.get("obligatorio"))


def _http_del_proyecto(sol: Solicitud) -> str:
    """El services/http del proyecto ("" si no se puede leer; si no existe, el que se crea)."""
    ext = _js.MARCADORES_VARIANTE[sol.variante or "ts"]["ext"]
    try:
        return (sol.raiz / "services" / f"http.{ext}").read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return "leerToken alVencerLaSesion"
    except (OSError, UnicodeDecodeError):
        return ""


def _validar_obligatorio(sol: Solicitud) -> None:
    """--obligatorio pide ingresar en el Layout: hace falta el de los proyectos nuevos."""
    ext = _js.MARCADORES_VARIANTE[sol.variante or "ts"]["extx"]
    try:
        texto = (sol.raiz / "components" / "Layout" / f"Layout.{ext}").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        texto = ""
    if "andamio:layout" not in texto or "andamio:directivas" not in texto:
        raise AndamioError(
            f"--obligatorio pide ingresar en el Layout (components/Layout/Layout.{ext}), y este proyecto no lo tiene.",
            "Los proyectos de Next.js creados con andamio 1.7 o más nuevo lo traen (Navbar, Footer y Layout). "
            f"En este, protegé las páginas de a una: {consola.programa()} nuevo pagina Perfil --protegido",
        )


def _contexto_login(sol: Solicitud) -> dict[str, str]:
    if _obligatorio(sol):
        _validar_obligatorio(sol)
    http = _http_del_proyecto(sol)
    ext = _js.MARCADORES_VARIANTE[sol.variante or "ts"]["ext"]
    if "leerToken" not in http:
        raise AndamioError(
            f"Tu services/http.{ext} es de una versión anterior: no guarda ni manda el token del login.",
            f"Agregale leerToken y el encabezado Authorization como en un proyecto nuevo ({consola.programa()} crear next prueba), "
            "o borralo y generá el login de nuevo.",
        )
    avisa = "alVencerLaSesion" in http
    registro = _con_registro(sol)
    explicacion = (
        ["// Si la API responde 401 a un pedido con el token (venció), se cierra la sesión: las", "// páginas protegidas llevan a /ingresar."]
        if sol.guia
        else []
    )
    return {
        "importar_http": "alVencerLaSesion, leerToken" if avisa else "leerToken",
        "al_vencer": "\n".join([*explicacion, "alVencerLaSesion(() => cambiar({ usuario: null, cargando: false }));", ""]) if avisa else "",
        "importar_link": "import Link from 'next/link';" if registro else "",
        "pie_ingresar": "\n".join(
            ["<p>", "  ¿No tenés cuenta? <Link href={{ pathname: '/registro', query: { desde: destino } }}>Registrate</Link>", "</p>"]
        )
        if registro
        else "",
        "enlace_registro": '<Link href="/registro">Registrarse</Link>' if registro else "",
        "y_registrarse": " y Registrarse" if registro else "",
        "lectura_layout": f"components/Layout/Layout.{_js.MARCADORES_VARIANTE[sol.variante or 'ts']['extx']}" if _obligatorio(sol) else "",
        "guardia_layout": "\n".join(
            (["// Toda la app pide ingresar (nuevo login --obligatorio): sin sesión, solo se ven /ingresar", "// y /registro, sin el menú ni el pie."] if sol.guia else [])
            + [
                "const { esDelLogin, pedirIngreso } = useLoginObligatorio();",
                "if (esDelLogin) {",
                "  return <main className={styles.contenido}>{children}</main>;",
                "}",
                "if (pedirIngreso) {",
                "  return pedirIngreso;",
                "}",
                "",
            ]
        ),
    }


def _validar_login(raiz: Path, nombre: Nombre) -> None:
    if nombre.snake != "sesion":
        raise AndamioError(
            "En Next.js el login no lleva nombre: genera sesion/ y las páginas /ingresar y /registro.",
            f"Ejemplo: {consola.programa()} nuevo login",
        )
    for carpeta in ("ingresar", "registro"):
        if (raiz / "app" / carpeta).exists():
            raise AndamioError(f"Ya hay una página en app/{carpeta}: el login usa esa ruta.", "Cambiale el nombre a la tuya y generá el login de nuevo.")


def _registro_a_omitir(sol: Solicitud) -> frozenset[str]:
    if _con_registro(sol):
        return frozenset()
    return frozenset(f"app/registro/{a}" for a in ("page.tsx", "page.jsx", "FormularioRegistro.tsx", "FormularioRegistro.jsx", "registro.module.css"))


def _pasos_login(sol: Solicitud) -> list[str]:
    pasos = [
        "# La API con el login (Django, FastAPI o Express, en su carpeta): python -m andamio nuevo login",
        "npm run dev",
        "http://localhost:3000/ingresar",
        "# Para que una página pida ingresar:",
        f"{consola.programa()} nuevo pagina Perfil --protegido",
    ]
    if "alVencerLaSesion" not in _http_del_proyecto(sol):
        pasos += [
            "# Tu services/http es de una versión anterior: cuando el token vence (60 minutos), las",
            "# páginas muestran el error 401 en lugar de volver a pedir el ingreso. Para eso, agregale",
            "# alVencerLaSesion y el control del 401, como en un proyecto nuevo.",
        ]
    return pasos


def _insercion_layout(texto: str, marcador: str, descripcion: str, ubicacion: str) -> Insercion:
    return Insercion(
        "components/Layout/Layout.@@extx@@", texto, marcador=marcador, descripcion=descripcion, ubicacion=ubicacion, comentario="//", condicion=_obligatorio
    )


LOGIN = Pieza(
    clave="login",
    lectura=(
        ("services/authService.@@ext@@", "pide el token a la API, crea usuarios y pregunta quién ingresó (/api/yo/)"),
        ("sesion/sesion.@@ext@@", "la sesión: useSesion() (quién ingresó), ingresar, registrarse y salir"),
        ("sesion/RutaProtegida.@@extx@@", "si nadie ingresó, lleva a /ingresar (y después vuelve)"),
        ("@@lectura_layout@@", "con --obligatorio: pide ingresar antes de mostrar el menú, el pie y la página"),
        ("app/ingresar/page.@@extx@@", "la página /ingresar (del servidor: lee ?desde=)"),
        ("app/ingresar/FormularioIngreso.@@extx@@", "el formulario para ingresar (del navegador)"),
        ("app/registro/FormularioRegistro.@@extx@@", "el formulario para crear una cuenta"),
        ("sesion/MenuSesion.@@extx@@", "Ingresar, o quién ingresó y Salir, en el menú"),
        ("services/http.@@ext@@", "guarda el token y lo manda en cada pedido; un 401 cierra la sesión"),
    ),
    titulo="Login",
    descripcion="ingresar y crear una cuenta con la API (token JWT), y páginas que piden ingresar (--protegido)",
    ejemplo="",
    nombre_defecto="sesion",
    formas=("@@nombre@@/ (rutas /ingresar y /registro)",),
    opciones=frozenset({"sin_registro", "obligatorio"}),
    validar_nombre=_validar_login,
    contexto=_contexto_login,
    marcadores={
        **_MARCADORES,
        "importar_http": "lo que la sesión toma de services/http (alVencerLaSesion, si el http lo tiene)",
        "al_vencer": "cerrar la sesión cuando la API responde 401 (vacío con un http anterior)",
        "importar_link": "el import de Link en el formulario de ingreso (vacío con --sin-registro)",
        "pie_ingresar": "el enlace a /registro debajo del formulario (vacío con --sin-registro)",
        "enlace_registro": "Registrarse en el menú (vacío con --sin-registro)",
        "y_registrarse": "' y Registrarse', para el comentario del menú (vacío con --sin-registro)",
        "lectura_layout": "con --obligatorio: el Layout, para el orden de lectura (vacío si no)",
        "guardia_layout": "con --obligatorio: el Layout muestra /ingresar si nadie ingresó (useLoginObligatorio)",
    },
    existe_si=("sesion",),
    si_no_existe=frozenset({"services/http.ts", "services/http.js"}),
    omitir=_registro_a_omitir,
    inserciones=(
        Insercion(
            "components/Navbar/Navbar.@@extx@@",
            "import { MenuSesion } from '@/sesion';",
            marcador="imports_navbar",
            descripcion="import de MenuSesion",
            ubicacion="arriba, junto a los otros import",
            comentario="//",
            alternativa=Insercion(
                "app/layout.@@extx@@", "import { MenuSesion } from '@/sesion';", marcador="estilos", descripcion="import de MenuSesion", ubicacion="arriba, junto a los otros import", comentario="//"
            ),
        ),
        dataclasses.replace(_enlace("<MenuSesion />"), descripcion="la sesión en el menú"),
        # Con --obligatorio, el Layout pasa a ser del navegador ('use client') y pide ingresar.
        _insercion_layout("'use client';", "directivas", "el Layout es del navegador ('use client')", "en la primera línea del archivo"),
        _insercion_layout("import { useLoginObligatorio } from '@/sesion';", "imports_layout", "import de useLoginObligatorio", "arriba, junto a los otros import"),
        _insercion_layout("@@guardia_layout@@", "layout", "toda la app pide ingresar", "al principio de la función Layout, antes del return"),
    ),
    siguiente_paso=_pasos_login,
)


def _marcadores_variante(api: str) -> dict[str, dict[str, str]]:
    return {v: {**marcadores, "api_por_defecto": api} for v, marcadores in _js.MARCADORES_VARIANTE.items()}


ESTILOS = piezas_de_estilos(
    "app",
    lambda ruta: Insercion(
        "app/layout.@@extx@@",
        f"import './{ruta}';",
        marcador="estilos",
        descripcion="import del CSS",
        ubicacion="junto a import './globals.css'",
        comentario="//",
    ),
    'En JSX: className="...".',
    _js.MARCADORES_EXTENSION,
)

STACK = Stack(
    clave="next",
    titulo="Next.js (frontend)",
    senal="package.json con next",
    detectar=_js.detectar_dependencias("next"),
    tipos=_js.TIPOS,
    piezas={"componente": COMPONENTE, "pagina": PAGINA, "hook": HOOK, "servicio": SERVICIO, "crud": CRUD, "login": LOGIN, **ESTILOS},
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
        # Si el plural no es el automático, el recurso tiene que usar el mismo (si no, la API
        # queda en otra ruta y las páginas reciben 404).
        plural = f" --plural {sol.nombre.plural}" if sol.nombre.plural_palabras != tuple(pluralizar(sol.nombre.palabras)) else ""
        pasos = [
            "# Las páginas usan la API de este proyecto. Si todavía no generaste el recurso:",
            f"python -m andamio nuevo recurso {sol.nombre.snake} {campos}{plural} --migrar",
            *pasos,
        ]
    return pasos


RECURSO = dataclasses.replace(
    express.RECURSO,
    descripcion="API en app/api/ (Route Handlers), modelo de Prisma, validación y tests",
    existe_si=("app/api/@@plural@@",),
    opciones=frozenset({"migrar"}),  # --protegido: cuando Next full stack tenga su login
    contexto=express.contexto_recurso_api("http://localhost:3000/api"),
    lectura=(
        ("prisma/schema.prisma", "el modelo @@Nombre@@ (la tabla), al final del archivo"),
        ("app/api/@@plural@@/esquema.@@ext@@", "qué datos acepta la API (validación con Zod)"),
        ("app/api/@@plural@@/route.@@ext@@", "listar y crear (/api/@@plural@@/)"),
        ("app/api/@@plural@@/[id]/route.@@ext@@", "ver, modificar y eliminar uno (/api/@@plural@@/3/)"),
        ("tests/@@plural@@.test.@@ext@@", "los tests: lo que la API tiene que cumplir"),
        ("http/@@plural@@.http", "peticiones para probar la API a mano"),
    ),
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
        **ESTILOS,
    },
    ejemplo_proyecto="mi-app",
    siguiente_paso_proyecto=["cd @@carpeta@@", "npm install", "npm run dev", "http://localhost:3000"],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_marcadores_variante("/api"),
    extiende="next",
)
