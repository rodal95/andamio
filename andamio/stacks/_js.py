"""Piezas y ayudas compartidas por los stacks de JavaScript (react y react-native)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from andamio.nucleo import consola, historial, identificadores
from andamio.nucleo.deteccion import dependencias_npm
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre, camel, kebab, parece_plural, separar_palabras, snake, titulo
from andamio.stacks.base import Solicitud
from andamio.stacks.django import TIPOS as TIPOS_API

# Los servicios usan los mismos tipos que el recurso de Django, FastAPI y Express, para que el
# mismo comando sirva en los dos lados: nombre:str precio:decimal ...
TIPOS = TIPOS_API

_TIPOS_TS = {
    "str": "string",
    "text": "string",
    "int": "number",
    "decimal": "number",
    "float": "number",
    "bool": "boolean",
    "date": "string",
    "datetime": "string",
    "email": "string",
}

_COMENTARIOS_TS = {
    "decimal": "  // La API lo envía como número (no como texto)",
    "date": '  // fecha: "2025-03-15"',
    "datetime": '  // fecha y hora: "2025-03-15T10:30:00Z"',
}

_COMENTARIOS_JSDOC = {
    "decimal": "número con 2 decimales",
    "date": 'fecha: "2025-03-15"',
    "datetime": 'fecha y hora: "2025-03-15T10:30:00Z"',
}

# --- Variantes: TypeScript y JavaScript -------------------------------------------------

VARIANTES = {"ts": "TypeScript", "js": "JavaScript"}

MARCADORES_VARIANTE = {
    "ts": {"ext": "ts", "extx": "tsx"},
    "js": {"ext": "js", "extx": "jsx"},
}

MARCADORES_EXTENSION = {
    "ext": "extensión de los archivos de código: ts o js",
    "extx": "extensión de los componentes: tsx o jsx",
}


def detectar_variante(raiz: Path) -> str:
    """TypeScript si el proyecto tiene tsconfig.json o la dependencia typescript."""
    if (raiz / "tsconfig.json").is_file() or "typescript" in dependencias_npm(raiz):
        return "ts"
    return "js"


MARCADORES_SERVICIO = {
    **MARCADORES_EXTENSION,
    "campos_ts": "una línea por campo de la interfaz (TypeScript): precio: number;",
    "campos_jsdoc": "una línea por campo del comentario JSDoc (JavaScript): * @property {number} precio",
}


def contexto_servicio(sol: Solicitud) -> dict[str, str]:
    # Los campos quedan en snake_case, igual que en el JSON que devuelve la API.
    lineas_ts = [f"{c.nombre}: {_TIPOS_TS[c.tipo]};{_COMENTARIOS_TS.get(c.tipo, '')}" for c in sol.campos]
    lineas_jsdoc = [
        f"* @property {{{_TIPOS_TS[c.tipo]}}} {c.nombre}" + (f" {_COMENTARIOS_JSDOC[c.tipo]}" if c.tipo in _COMENTARIOS_JSDOC else "")
        for c in sol.campos
    ]
    return {"campos_ts": "\n".join(lineas_ts), "campos_jsdoc": "\n".join(lineas_jsdoc)}


def detectar_dependencias(*paquetes: str) -> Callable[[Path], bool]:
    def detectar(raiz: Path) -> bool:
        if not (raiz / "package.json").is_file():
            return False
        return set(paquetes) <= dependencias_npm(raiz)

    return detectar


# --- Ajustes de nombres -------------------------------------------------------------


def sin_prefijo_use(palabras: list[str]) -> list[str]:
    """"useContador" y "contador" generan el mismo hook: useContador."""
    return palabras[1:] if palabras and palabras[0] == "use" else palabras


def sin_sufijo(*sufijos: str) -> Callable[[list[str]], list[str]]:
    """"ProductosPage" y "Productos" generan la misma página: ProductosPage."""

    def ajustar(palabras: list[str]) -> list[str]:
        return palabras[:-1] if len(palabras) > 1 and palabras[-1] in sufijos else palabras

    return ajustar


_HOOKS_DE_REACT = {
    "useState", "useEffect", "useRef", "useMemo", "useCallback", "useContext", "useReducer", "useId",
    "useTransition", "useDeferredValue", "useLayoutEffect", "useInsertionEffect", "useImperativeHandle",
    "useSyncExternalStore", "useDebugValue", "useActionState", "useOptimistic", "useFormStatus",
}  # fmt: skip

_COMPONENTES_OCUPADOS = {"App", "React", "Fragment", "StrictMode", "Suspense", "Profiler"}


def validar_hook(raiz: Path, nombre: Nombre) -> None:
    hook = f"use{nombre.pascal}"
    if hook in _HOOKS_DE_REACT:
        raise AndamioError(f"'{hook}' ya existe en React; si creás otro con ese nombre se confunden.", "Elegí otro nombre.")


def validar_componente(raiz: Path, nombre: Nombre) -> None:
    if nombre.pascal in _COMPONENTES_OCUPADOS:
        raise AndamioError(f"'{nombre.pascal}' ya lo usa React o el proyecto.", "Elegí otro nombre para el componente.")


# --- Carpeta de pantallas (Expo Router) ----------------------------------------------


def normalizar_carpeta(texto: str) -> str:
    """"Productos" -> "productos"; "(Tabs)" -> "(tabs)" (grupo de Expo Router); admite "a/b"."""
    partes: list[str] = []
    for parte in re.split(r"[\\/]+", texto.strip()):
        if not parte:
            continue
        grupo = parte.startswith("(") and parte.endswith(")")
        interior = parte[1:-1] if grupo else parte
        normal = kebab(separar_palabras(interior, "La carpeta"))
        partes.append(f"({normal})" if grupo else normal)
    if not partes:
        raise AndamioError("La carpeta está vacía.")
    return "/".join(partes)


def contexto_pantalla(sol: Solicitud) -> dict[str, str]:
    carpeta = sol.opciones.get("carpeta", "")
    archivo = sol.nombre.kebab
    ruta = f"{carpeta}/{archivo}" if carpeta else archivo
    # Los grupos "(tabs)" no forman parte de la URL, y "index" es la ruta de la carpeta.
    segmentos = [p for p in ruta.split("/") if not p.startswith("(")]
    if segmentos and segmentos[-1] == "index":
        segmentos.pop()
    return {"ruta_pantalla": ruta, "url_pantalla": "/" + "/".join(segmentos)}


MARCADORES_PANTALLA = {
    **MARCADORES_EXTENSION,
    "ruta_pantalla": "archivo dentro de app/, sin extensión: productos/detalle-producto",
    "url_pantalla": "ruta para navegar: /productos/detalle-producto",
}


# --- Página con datos de la API (pagina --datos producto [--uno]) ----------------------


def normalizar_datos(texto: str) -> str:
    """--datos Producto, --datos item-pedido -> producto, item_pedido (el nombre del servicio, en singular)."""
    palabras = separar_palabras(texto, "El nombre del servicio (--datos)")
    if parece_plural(palabras):
        raise AndamioError(
            f"--datos va con el nombre del servicio en singular: '{texto}' parece plural.",
            "Ejemplo: --datos producto (usa src/services/productoService)",
        )
    return snake(palabras)


MARCADORES_PAGINA = {
    "ruta_pagina": "la ruta de la página: /contacto, o /producto-detalle/:id con --uno",
    "url_pagina": "la dirección para abrirla: /contacto, o /producto-detalle/1 con --uno",
    "datos_imports": "imports del hook y del servicio (vacío sin --datos)",
    "datos_consulta": "la llamada a useConsulta (vacío sin --datos)",
    "datos_contenido": "cargando, error y los datos: una lista, o uno solo con --uno (vacío sin --datos)",
    "datos_servicio": "el archivo del servicio que usa (vacío sin --datos)",
    "datos_hook": "el archivo de useConsulta (vacío sin --datos)",
}


def contexto_pagina(sol: Solicitud) -> dict[str, str]:
    datos = sol.opciones.get("datos")
    uno = bool(sol.opciones.get("uno"))
    ruta = f"/{sol.nombre.kebab}"
    if not datos:
        if uno:
            raise AndamioError(
                "--uno va junto con --datos: dice que la página muestra uno solo de esos datos.",
                f"Ejemplo: {consola.programa()} nuevo pagina {sol.nombre.pascal} --datos producto --uno",
            )
        vacios = ("datos_imports", "datos_consulta", "datos_contenido", "datos_servicio", "datos_hook")
        return {**dict.fromkeys(vacios, ""), "ruta_pagina": ruta, "url_pagina": ruta}

    ext = MARCADORES_VARIANTE[sol.variante or "ts"]["ext"]
    servicio = f"{camel(datos.split('_'))}Service"
    archivo_servicio = f"src/services/{servicio}.{ext}"
    if not (sol.raiz / archivo_servicio).is_file():
        raise AndamioError(
            f"La página usa {archivo_servicio}, que todavía no existe.",
            f"Generá primero el servicio, con los campos de la API: {consola.programa()} nuevo servicio {datos} nombre:str precio:decimal",
        )
    campos = historial.campos_de(sol.raiz, datos, ("servicio", "crud")) or []
    # Con guía, una línea que explica la consulta (la guía de los bloques se arma acá, no en la plantilla).
    if uno:
        explicacion = "// El id sale de la ruta; si cambia, useConsulta vuelve a pedir los datos."
        consulta = [
            "const id = Number(useParams().id);",
            f"const {{ datos, cargando, error }} = useConsulta(() => {servicio}.obtener(id), [id]);",
        ]
        imports = ["import { useParams } from 'react-router';"]
        contenido = _contenido_uno(campos)
    else:
        explicacion = "// useConsulta pide los datos a la API (con useEffect) y avisa si está cargando o si falló."
        consulta = [f"const {{ datos, cargando, error }} = useConsulta({servicio}.listar);"]
        imports = []
        contenido = _contenido_lista(campos, datos)
    imports += ["import { useConsulta } from '../../hooks/useConsulta';", f"import {{ {servicio} }} from '../../services/{servicio}';"]
    if sol.guia:
        consulta.insert(0, explicacion)
    return {
        "ruta_pagina": f"{ruta}/:id" if uno else ruta,
        "url_pagina": f"{ruta}/1" if uno else ruta,
        "datos_imports": "\n".join(imports),
        "datos_consulta": "\n".join(consulta) + "\n",
        "datos_contenido": "\n".join(contenido),
        "datos_servicio": archivo_servicio,
        "datos_hook": f"src/hooks/useConsulta.{ext}",
    }


_CARGANDO_Y_ERROR = [
    "{cargando && <p>Cargando…</p>}",
    "{error && <p role=\"alert\">No se pudo cargar: {error}</p>}",
]


def _contenido_lista(campos, datos: str) -> list[str]:
    para_texto = next((c for c in campos if c.tipo in ("str", "email")), None)
    texto = f"{{item.{para_texto.nombre}}}" if para_texto else f"{{`{titulo(datos.split('_'))} ${{item.id}}`}}"
    return [
        *_CARGANDO_Y_ERROR,
        "{datos?.length === 0 && <p>Todavía no hay registros.</p>}",
        "<ul>",
        "  {datos?.map((item) => (",
        f"    <li key={{item.id}}>{texto}</li>",
        "  ))}",
        "</ul>",
    ]


def _contenido_uno(campos) -> list[str]:
    if not campos:
        # Sin los campos (el servicio no está en el historial): se muestra todo lo que llegó.
        return [*_CARGANDO_Y_ERROR, "{datos && <pre>{JSON.stringify(datos, null, 2)}</pre>}"]
    filas = []
    for c in campos:
        valor = f"{{datos.{c.nombre} ? 'Sí' : 'No'}}" if c.tipo == "bool" else f"{{datos.{c.nombre}}}"
        filas += [f"    <dt>{c.titulo}</dt>", f"    <dd>{valor}</dd>"]
    return [*_CARGANDO_Y_ERROR, "{datos && (", "  <dl>", *filas, "  </dl>", ")}"]


def pasos_pagina(sol: Solicitud) -> list[str]:
    pasos = ["npm run dev", "http://localhost:5173@@url_pagina@@"]
    if sol.opciones.get("datos"):
        pasos.append("# Necesita la API andando (Django, FastAPI o Express), con el recurso que usa el servicio.")
    return pasos_router(pasos)(sol)


# --- Router (React) ---------------------------------------------------------------------

# Rama 7: funciona con Node 20 (la 8 pide Node 22.22). Tiene que coincidir con package.json
# de la plantilla del proyecto (hay un test que lo controla).
VERSION_ROUTER = "7.18.6"


def _app(raiz: Path) -> tuple[str, str]:
    for nombre in ("App.tsx", "App.jsx"):
        archivo = raiz / "src" / nombre
        if archivo.is_file():
            try:
                return nombre, archivo.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError):
                return nombre, ""
    return "App.tsx", ""


def _leer_app(raiz: Path) -> str:
    return _app(raiz)[1]


def validar_componentes_libres(componentes: Callable[[Nombre], list[str]]) -> Callable[[Path, Nombre], None]:
    """Rechaza una pieza si src/App ya importa un componente con el mismo nombre
    (ej.: nuevo pagina ProductoLista después de nuevo crud producto: los dos son ProductoListaPage)."""

    def validar(raiz: Path, nombre: Nombre) -> None:
        archivo, texto = _app(raiz)
        ocupados = identificadores.declarados(archivo, texto)
        repetido = next((c for c in componentes(nombre) if c in ocupados), None)
        if repetido:
            raise AndamioError(
                f"src/{archivo} ya usa un componente {repetido} (lo generó otra pieza): el código no compilaría.",
                "Elegí otro nombre.",
            )

    return validar


def validar_ruta_libre(ruta: Callable[[Nombre], str]) -> Callable[[Path, Nombre], None]:
    """Rechaza una pieza si su ruta ya está registrada en src/App."""

    def validar(raiz: Path, nombre: Nombre) -> None:
        camino = ruta(nombre)
        if f'path="{camino}"' in _leer_app(raiz):
            raise AndamioError(
                f"Ya hay una página en la ruta {camino} (src/App).",
                "Elegí otro nombre, o borrá esa ruta de src/App si ya no la usás.",
            )

    return validar


def pasos_router(pasos: list[str]) -> Callable[[Solicitud], list[str]]:
    """Agrega la instalación del router si el proyecto todavía no lo tiene."""

    def calcular(sol: Solicitud) -> list[str]:
        if "react-router" in dependencias_npm(sol.raiz):
            return list(pasos)
        return [
            "# Tu proyecto todavía no tiene el router (react-router). Instalalo una vez:",
            f"npm install react-router@{VERSION_ROUTER}",
            *pasos,
        ]

    return calcular


def _contexto_crud(sol: Solicitud) -> dict[str, str]:
    contexto = contexto_servicio(sol)
    variable = sol.nombre.camel
    para_texto = next((c for c in sol.campos if c.tipo in ("str", "email")), None)
    contexto["texto_item"] = f"item.{para_texto.nombre}" if para_texto else f"`{sol.nombre.pascal} ${{item.id}}`"

    detalle, vacios, copiar, formulario = [], [], [], []
    for c in sol.campos:
        valor = f"{variable}.{c.nombre}"
        detalle += [f"<dt>{c.titulo}</dt>", f"<dd>{{{valor} ? 'Sí' : 'No'}}</dd>" if c.tipo == "bool" else f"<dd>{{{valor}}}</dd>"]
        vacios.append(f"{c.nombre}: {_VACIOS[c.tipo]},")
        copiar.append(f"{c.nombre}: registro.{c.nombre}{'.slice(0, 16)' if c.tipo == 'datetime' else ''},")
        formulario += _campo_formulario(c)
    contexto.update(
        campos_detalle="\n".join(detalle),
        valores_vacios="\n".join(vacios),
        campos_copiar="\n".join(copiar),
        campos_formulario="\n".join(formulario),
    )
    return contexto


_VACIOS = {"str": "''", "text": "''", "email": "''", "date": "''", "datetime": "''", "int": "0", "decimal": "0", "float": "0", "bool": "false"}

_PASOS_NUMERICOS = {"int": "1", "decimal": "0.01", "float": "any"}


def _campo_formulario(campo) -> list[str]:
    n = campo.nombre
    if campo.tipo == "bool":
        control = f"<input type=\"checkbox\" checked={{datos.{n}}} onChange={{(e) => cambiar('{n}', e.target.checked)}} />"
    elif campo.tipo in _PASOS_NUMERICOS:
        control = (
            f"<input type=\"number\" step=\"{_PASOS_NUMERICOS[campo.tipo]}\" required "
            f"value={{Number.isNaN(datos.{n}) ? '' : datos.{n}}} onChange={{(e) => cambiar('{n}', e.target.valueAsNumber)}} />"
        )
    elif campo.tipo == "text":
        control = f"<textarea required value={{datos.{n}}} onChange={{(e) => cambiar('{n}', e.target.value)}} />"
    else:
        tipo = {"email": "email", "date": "date", "datetime": "datetime-local"}.get(campo.tipo, "text")
        control = f"<input type=\"{tipo}\" required value={{datos.{n}}} onChange={{(e) => cambiar('{n}', e.target.value)}} />"
    return [
        "<label className={styles.campo}>",
        f"  {campo.titulo}",
        f"  {control}",
        f"  {{errores.{n} && <small className={{styles.error}}>{{errores.{n}.join(' ')}}</small>}}",
        "</label>",
    ]


MARCADORES_CRUD = {
    **MARCADORES_SERVICIO,
    "texto_item": "lo que se muestra de cada registro en la lista: item.nombre",
    "campos_detalle": "un <dt> y un <dd> por campo, para el componente de detalle",
    "valores_vacios": "valores iniciales del formulario: nombre: '',",
    "campos_copiar": "copia un registro de la API a los datos del formulario: nombre: registro.nombre,",
    "campos_formulario": "un <label> con su <input> (según el tipo) y su error, por campo",
}

contexto_crud = _contexto_crud
