"""Stack `react-native`: aplicación móvil con Expo + Expo Router + TypeScript."""

from __future__ import annotations

from andamio.stacks import _js
from andamio.stacks.base import Insercion, Pieza, Stack

PANTALLA = Pieza(
    clave="pantalla",
    titulo="Pantalla",
    descripcion="pantalla de Expo Router (un archivo en app/ es una ruta)",
    ejemplo="detalle-producto",
    formas=("@@nombreKebab@@", "@@Nombre@@Pantalla"),
    opciones=frozenset({"carpeta"}),
    normalizar_opcion={"carpeta": _js.normalizar_carpeta},
    ajustar_palabras=_js.sin_sufijo("pantalla", "screen"),
    contexto=_js.contexto_pantalla,
    marcadores=_js.MARCADORES_PANTALLA,
    existe_si=("app/@@ruta_pantalla@@.@@extx@@",),
    siguiente_paso=[
        "npx expo start",
        "# Para abrirla desde otra pantalla:",
        "import { router } from 'expo-router';",
        "router.push('@@url_pantalla@@');",
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
    titulo="Servicio",
    descripcion="funciones para usar un recurso de la API (Django o FastAPI)",
    ejemplo="producto nombre:str precio:decimal stock:int",
    formas=("@@Nombre@@", "@@nombreCamel@@Service"),
    usa_campos=True,
    usa_plural=True,
    contexto=_js.contexto_servicio,
    marcadores=_js.MARCADORES_SERVICIO,
    existe_si=("services/@@nombreCamel@@Service.@@ext@@",),
    si_no_existe=frozenset({"services/http.ts", "services/http.js"}),
    siguiente_paso=[
        "# Usalo en una pantalla:",
        "import { @@nombreCamel@@Service } from '@/services/@@nombreCamel@@Service';",
        "# La dirección de la API está en EXPO_PUBLIC_API_URL (archivo .env); leé services/http.ts",
    ],
)

STACK = Stack(
    clave="react-native",
    titulo="React Native + Expo",
    senal="package.json con expo",
    detectar=_js.detectar_dependencias("expo"),
    tipos=_js.TIPOS,
    piezas={"pantalla": PANTALLA, "componente": COMPONENTE, "hook": HOOK, "servicio": SERVICIO},
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
