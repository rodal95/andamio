"""Stack `react-native`: aplicación móvil con Expo + Expo Router + TypeScript."""

from __future__ import annotations

from andamio.estilos import contexto_tema_js, pieza_tema
from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Stack

_HOOK_CONSULTA = frozenset({"hooks/useConsulta.ts", "hooks/useConsulta.js"})

PANTALLA = Pieza(
    clave="pantalla",
    lectura=(
        ("@@datos_servicio@@", "las funciones que piden los datos a la API"),
        ("@@datos_hook@@", "useConsulta: el useEffect que pide los datos, con cargando y error"),
        ("app/@@ruta_pantalla@@.@@extx@@", "la pantalla"),
    ),
    titulo="Pantalla",
    descripcion="pantalla de Expo Router (un archivo en app/ es una ruta); con --datos, muestra datos de la API",
    ejemplo="detalle-producto",
    formas=("@@nombreKebab@@", "@@Nombre@@Pantalla"),
    opciones=frozenset({"carpeta", "datos", "uno"}),
    normalizar_opcion={"carpeta": _js.normalizar_carpeta, "datos": _js.normalizar_datos},
    ajustar_palabras=_js.sin_sufijo("pantalla", "screen"),
    contexto=_js.contexto_pantalla,
    marcadores=_js.MARCADORES_PANTALLA,
    existe_si=("app/@@ruta_pantalla@@.@@extx@@",),
    # El hook se crea solo con --datos, y si ya existe (lo generó un servicio) no se toca.
    si_no_existe=_HOOK_CONSULTA,
    omitir=lambda sol: frozenset() if sol.opciones.get("datos") else _HOOK_CONSULTA,
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
    si_no_existe=frozenset({"services/http.ts", "services/http.js"}) | _HOOK_CONSULTA,
    siguiente_paso=[
        "# Una pantalla que lo usa (lista, o uno solo con --uno):",
        "python -m andamio nuevo pantalla @@pluralKebab@@ --datos @@nombre@@",
        "python -m andamio nuevo pantalla @@nombreKebab@@ --datos @@nombre@@ --uno",
        "# O a mano, en una pantalla:",
        "import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';",
        "# La dirección de la API está en EXPO_PUBLIC_API_URL (archivo .env); leé services/http.ts",
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
    tipos=_js.TIPOS,
    piezas={"pantalla": PANTALLA, "componente": COMPONENTE, "hook": HOOK, "servicio": SERVICIO, "tema": TEMA},
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
