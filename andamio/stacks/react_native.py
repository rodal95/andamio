"""Stack `react-native`: aplicación móvil con Expo + Expo Router + TypeScript."""

from __future__ import annotations

from pathlib import Path

from andamio.estilos import contexto_tema_js, pieza_tema
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

_HOOKS = _js.hooks("hooks")  # useConsulta y useFormulario

PANTALLA = Pieza(
    clave="pantalla",
    lectura=(
        ("@@datos_servicio@@", "las funciones que piden los datos a la API"),
        ("@@datos_hook@@", "el hook que usa el servicio: useConsulta (pide los datos) o useFormulario (crea y edita)"),
        ("app/@@ruta_pantalla@@.@@extx@@", "la pantalla"),
    ),
    titulo="Pantalla",
    descripcion="pantalla de Expo Router (un archivo en app/ es una ruta); con --datos, usa un servicio (lista, --uno o --form)",
    ejemplo="detalle-producto",
    formas=("@@nombreKebab@@", "@@Nombre@@Pantalla"),
    opciones=frozenset({"carpeta", "datos", "uno", "form", "protegido"}),
    normalizar_opcion={"carpeta": _js.normalizar_carpeta, "datos": _js.normalizar_datos},
    ajustar_palabras=_js.sin_sufijo("pantalla", "screen"),
    contexto=_js.contexto_pantalla,
    marcadores=_js.MARCADORES_PANTALLA,
    existe_si=("app/@@ruta_pantalla@@.@@extx@@",),
    # Con --datos se crea el hook que usa, y si ya existe (lo generó un servicio) no se toca.
    si_no_existe=_HOOKS,
    omitir=_js.hooks_a_omitir("hooks", "services"),
    siguiente_paso=[
        "npx expo start",
        "# Para abrirla desde otra pantalla:",
        "import { router } from 'expo-router';",
        "router.push('@@url_abrir@@');",
    ],
)

COMPONENTE = Pieza(
    clave="componente",
    titulo="Componente",
    descripcion="componente con StyleSheet",
    ejemplo="Tarjeta",
    formas=("pascal",),
    validar_nombre=_js.validar_componente,
    marcadores=_js.MARCADORES_EXTENSION,
    existe_si=("components/@@Nombre@@.@@extx@@",),
    inserciones=(
        Insercion(
            "components/index.@@ext@@",
            "export { @@Nombre@@ } from './@@Nombre@@';",
            descripcion="export de @@Nombre@@",
            comentario="//",
            crear_si_falta=True,
        ),
    ),
    siguiente_paso=["# Usalo en una pantalla:", "import { @@Nombre@@ } from '@/components';"],
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
    existe_si=("hooks/use@@Nombre@@.@@ext@@",),
    siguiente_paso=["# Usalo en una pantalla:", "import { use@@Nombre@@ } from '@/hooks/use@@Nombre@@';"],
)

SERVICIO = Pieza(
    clave="servicio",
    lectura=(
        ('services/@@nombreCamel@@Service.@@ext@@', 'las funciones para usar /api/@@plural@@/'),
        ('services/http.@@ext@@', 'lo común a todas las llamadas: dirección de la API y errores'),
        ('hooks/useConsulta.@@ext@@', 'el useEffect para pedir datos desde una pantalla, con cargando y error'),
        ('hooks/useFormulario.@@ext@@', 'los datos de un formulario para crear o editar, con los errores de la API'),
    ),
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API (Django, FastAPI o Express)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "@@nombreCamel@@Service"),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_servicio,
    marcadores=_js.MARCADORES_SERVICIO,
    existe_si=("services/@@nombreCamel@@Service.@@ext@@",),
    si_no_existe=frozenset({"services/http.ts", "services/http.js"}) | _HOOKS,
    omitir=_js.hooks_del_servicio("hooks"),
    **_js.OPCION_SOLO,
    siguiente_paso=_js.pasos_servicio(
        "pantalla",
        ("@@pluralKebab@@", "@@nombreKebab@@", "editar-@@nombreKebab@@", "@@nombreKebab@@"),
        [
            "# O a mano, en una pantalla:",
            "import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';",
            "# La dirección de la API está en EXPO_PUBLIC_API_URL (archivo .env); leé services/http.ts",
        ],
    ),
)

# --- Login (nuevo login): el mismo contrato que las APIs de andamio -----------------------


def _con_registro(sol: Solicitud) -> bool:
    return not sol.opciones.get("sin_registro")


def _contexto_login(sol: Solicitud) -> dict[str, str]:
    ext = _js.MARCADORES_VARIANTE[sol.variante or "ts"]["ext"]
    try:
        http = (sol.raiz / "services" / f"http.{ext}").read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        http = "usarToken"  # se crea ahora (y lo tiene)
    except (OSError, UnicodeDecodeError):
        http = ""
    if "usarToken" not in http:
        raise AndamioError(
            f"Tu services/http.{ext} es de una versión anterior: no manda el token del login.",
            "Agregale usarToken y el encabezado Authorization como en un proyecto nuevo "
            "(python -m andamio crear react-native prueba), o borralo y generá el login de nuevo.",
        )
    ts = ext == "ts"
    registro = _con_registro(sol)
    href = " as Href" if ts else ""
    return {
        "router_ingresar": ("type Href, " if ts else "") + ("Link, " if registro else "") + "router, Stack, useLocalSearchParams",
        "a_registro": "\n".join(
            ["// A /registro sin perder a dónde volver después.", f"const aRegistro = {{ pathname: '/registro', params: {{ desde }} }}{href};"]
        )
        if registro
        else "",
        "pie_ingresar": "\n".join(["<Link href={aRegistro} style={styles.enlace}>", "  ¿No tenés cuenta? Registrate", "</Link>"]) if registro else "",
    }


def _registro_a_omitir(sol: Solicitud) -> frozenset[str]:
    return frozenset() if _con_registro(sol) else frozenset({"app/registro.tsx", "app/registro.jsx"})


def _validar_login(raiz: Path, nombre: Nombre) -> None:
    if nombre.snake != "sesion":
        raise AndamioError("En React Native el login no lleva nombre: genera sesion/ y las pantallas /ingresar y /registro.", "Ejemplo: python -m andamio nuevo login")
    for archivo in ("app/ingresar.tsx", "app/ingresar.jsx", "app/registro.tsx", "app/registro.jsx"):
        if (raiz / archivo).exists():
            raise AndamioError(f"Ya hay una pantalla {archivo}: el login usa esa ruta.", "Cambiale el nombre a la tuya y generá el login de nuevo.")


LOGIN = Pieza(
    clave="login",
    lectura=(
        ("services/authService.@@ext@@", "pide el token a la API, crea usuarios y pregunta quién ingresó (/api/yo/)"),
        ("sesion/almacen.@@ext@@", "dónde queda guardado el token: SecureStore (cifrado) en el celular"),
        ("sesion/sesion.@@ext@@", "la sesión: useSesion() (quién ingresó), ingresar, registrarse y salir"),
        ("sesion/usePedirIngreso.@@extx@@", "para las pantallas que piden ingresar: si nadie ingresó, a /ingresar"),
        ("app/ingresar.@@extx@@", "la pantalla para ingresar"),
        ("app/registro.@@extx@@", "la pantalla para crear una cuenta"),
        ("components/BotonSesion.@@extx@@", "Ingresar o Salir, para la barra de arriba"),
    ),
    titulo="Login",
    descripcion="ingresar y crear una cuenta con la API (token JWT, guardado cifrado), y pantallas que piden ingresar (--protegido)",
    ejemplo="",
    nombre_defecto="sesion",
    formas=("@@nombre@@/ (pantallas /ingresar y /registro)",),
    opciones=frozenset({"sin_registro"}),
    validar_nombre=_validar_login,
    contexto=_contexto_login,
    marcadores={
        **_js.MARCADORES_EXTENSION,
        "router_ingresar": "lo que la pantalla de ingreso toma de expo-router (Link, solo con registro)",
        "a_registro": "la dirección de /registro con ?desde= (vacío con --sin-registro)",
        "pie_ingresar": "el enlace a /registro debajo del formulario (vacío con --sin-registro)",
    },
    existe_si=("sesion",),
    si_no_existe=frozenset({"services/http.ts", "services/http.js"}),
    omitir=_registro_a_omitir,
    inserciones=(
        # Ingresar / Salir en la barra de arriba de todas las pantallas.
        Insercion(
            "app/_layout.@@extx@@",
            "import { BotonSesion } from '@/components/BotonSesion';",
            marcador="imports",
            descripcion="import de BotonSesion",
            ubicacion="arriba, junto a los otros import",
            comentario="//",
        ),
        Insercion(
            "app/_layout.@@extx@@",
            "headerRight: () => <BotonSesion />,",
            marcador="opciones",
            descripcion="el botón Ingresar / Salir en la barra de arriba",
            ubicacion="en las opciones del <Stack>: <Stack screenOptions={{ headerRight: () => <BotonSesion /> }} />",
            comentario="//",
        ),
    ),
    siguiente_paso=[
        "# Si el proyecto es de antes: npx expo install expo-secure-store",
        "# La API con el login (Django, FastAPI o Express): python -m andamio nuevo login",
        "npx expo start",
        "# Para que una pantalla pida ingresar:",
        "python -m andamio nuevo pantalla perfil --protegido",
    ],
)

TEMA = pieza_tema(
    descripcion="colores claro y oscuro de la app y el hook useTema()",
    contexto=contexto_tema_js,
    marcadores={
        **_js.MARCADORES_EXTENSION,
        "colores_claro": "los colores del modo claro: acento: '#2563eb',",
        "colores_oscuro": "los colores del modo oscuro",
        "modo": "auto, claro u oscuro (--modo)",
    },
    existe_si=("constants/tema.@@ext@@",),
    siguiente_paso=[
        "# Usalo en una pantalla o componente:",
        "import { useTema } from '@/constants/tema';",
        "const tema = useTema();   // tema.acento, tema.fondo, tema.texto, tema.superficie...",
    ],
)

STACK = Stack(
    clave="react-native",
    titulo="React Native + Expo",
    senal="package.json con expo",
    detectar=_js.detectar_dependencias("expo"),
    tipos=_js.TIPOS_CON_RELACIONES,
    piezas={"pantalla": PANTALLA, "componente": COMPONENTE, "hook": HOOK, "servicio": SERVICIO, "login": LOGIN, "tema": TEMA},
    ejemplo_proyecto="mi-app",
    siguiente_paso_proyecto=[
        "cd @@carpeta@@",
        "npm install",
        "npx expo start",
        "# Apretá a para abrirla en el emulador de Android, w para el navegador, o escaneá el QR con Expo Go.",
    ],
    contexto_env=lambda: {},
    variantes=_js.VARIANTES,
    detectar_variante=_js.detectar_variante,
    marcadores_variante=_js.MARCADORES_VARIANTE,
)
