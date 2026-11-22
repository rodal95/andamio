"""Piezas y ayudas compartidas por los stacks de JavaScript (react y react-native)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from andamio.nucleo import consola, historial, identificadores, relaciones
from andamio.nucleo.deteccion import dependencias_npm
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre, camel, kebab, pascal, parece_plural, separar_palabras, snake, titulo
from andamio.stacks.base import Solicitud
from andamio.stacks.django import TIPOS as TIPOS_API
from andamio.stacks.django import TIPOS_RECURSO

# Los servicios usan los mismos tipos que el recurso de Django, FastAPI y Express, para que el
# mismo comando sirva en los dos lados: nombre:str precio:decimal ...
TIPOS = TIPOS_API
# React y React Native también aceptan relaciones (categoria:fk), como el recurso de Django.
TIPOS_CON_RELACIONES = TIPOS_RECURSO

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
    "fk": "number | null",
}

_COMENTARIOS_TS = {
    "fk": "  // id de la relación (null: sin elegir)",
    "decimal": "  // La API lo envía como número (no como texto)",
    "date": '  // fecha: "2025-03-15"',
    "datetime": '  // fecha y hora: "2025-03-15T10:30:00Z"',
}

_COMENTARIOS_JSDOC = {
    "fk": "id de la relación (null: sin elegir)",
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
    "ejemplo_validacion": "ejemplo de validación para el TODO(logica) del formulario, con un campo propio",
    "ejemplo_validacion_vue": "el mismo ejemplo, para Vue (datos.value y errores.value)",
}


def ejemplo_validacion(campos, vue: bool = False) -> str:
    """Un ejemplo de validación (para el TODO(logica)) con un campo del propio formulario:
    el primero que no sea sí/no. En Vue, datos y errores son ref (datos.value...)."""
    campo = next((c for c in campos if c.tipo != "bool"), campos[0] if campos else None)
    if campo is None:
        return ""
    datos = "datos.value" if vue else "datos"
    valor = f"{datos}.{campo.nombre}"
    if campo.tipo in ("int", "decimal", "float"):
        condicion, mensaje = f"Number({valor}) <= 0", "Tiene que ser mayor que cero."
    elif campo.tipo == "bool":
        condicion, mensaje = f"!{valor}", "Tenés que marcarlo."
    elif campo.tipo in ("date", "datetime", relaciones.TIPO):
        condicion, mensaje = f"!{valor}", "Elegí uno."
    else:
        condicion, mensaje = f"String({valor}).trim().length < 3", "Escribí al menos 3 letras."
    errores = f"errores.value = {{ {campo.nombre}: ['{mensaje}'] }};" if vue else f"setErrores({{ {campo.nombre}: ['{mensaje}'] }});"
    return f"if ({condicion}) {{ {errores} return; }}"


def contexto_servicio(sol: Solicitud) -> dict[str, str]:
    # Los campos quedan en snake_case, igual que en el JSON que devuelve la API.
    lineas_ts, lineas_jsdoc = [], []
    for c in sol.campos:
        lineas_ts.append(f"{c.nombre}: {_TIPOS_TS[c.tipo]};{_COMENTARIOS_TS.get(c.tipo, '')}")
        comentario = f" {_COMENTARIOS_JSDOC[c.tipo]}" if c.tipo in _COMENTARIOS_JSDOC else ""
        lineas_jsdoc.append(f"* @property {{{_TIPOS_TS[c.tipo]}}} {c.nombre}{comentario}")
        if c.tipo == relaciones.TIPO:
            # Opcional (?): solo lo devuelve la API de Django, y no se manda al crear o modificar.
            lineas_ts.append(f"{c.nombre}_texto?: string | null; // su texto, como lo muestra la API (solo lectura)")
            lineas_jsdoc.append(f"* @property {{string | null}} [{c.nombre}_texto] su texto, como lo muestra la API (solo lectura)")
    return {
        "campos_ts": "\n".join(lineas_ts),
        "campos_jsdoc": "\n".join(lineas_jsdoc),
        # Para el ejemplo del TODO(logica) de los formularios (crud), con un campo propio.
        "ejemplo_validacion": ejemplo_validacion(sol.campos),
        "ejemplo_validacion_vue": ejemplo_validacion(sol.campos, vue=True),
    }


# --- Servicio con algunas funciones (--solo crear, --solo listar,obtener) ---------------

OPERACIONES = ("listar", "obtener", "crear", "actualizar", "eliminar")
# En inglés, y los métodos HTTP que no dejan dudas (GET puede ser listar u obtener).
_ALIAS_OPERACIONES = {
    "list": "listar",
    "get": "obtener",
    "create": "crear",
    "post": "crear",
    "update": "actualizar",
    "patch": "actualizar",
    "put": "actualizar",
    "delete": "eliminar",
}
_EJEMPLO_SOLO = "Ejemplo: --solo crear (solo enviar, POST), o --solo listar,obtener (solo ver)"


def normalizar_solo(texto: str) -> str:
    """--solo "Crear" / --solo listar,obtener / --solo post -> "crear" / "listar,obtener" (en el orden del servicio)."""
    elegidas = set()
    for parte in re.split(r"[\s,]+", texto.strip().lower()):
        if not parte:
            continue
        operacion = _ALIAS_OPERACIONES.get(parte, parte)
        if operacion not in OPERACIONES:
            raise AndamioError(
                f"--solo: '{parte}' no es una de las funciones del servicio ({', '.join(OPERACIONES)}).", _EJEMPLO_SOLO
            )
        elegidas.add(operacion)
    if not elegidas:
        raise AndamioError("--solo va con las funciones que querés en el servicio.", _EJEMPLO_SOLO)
    return ",".join(op for op in OPERACIONES if op in elegidas)


def operaciones_pedidas(sol: Solicitud) -> tuple[str, ...]:
    """Las funciones que tiene que tener el servicio: las de --solo, o todas."""
    solo = sol.opciones.get("solo")
    return tuple(solo.split(",")) if solo else OPERACIONES


_INICIO_SERVICIO = re.compile(r"^export const \w+ = \{$")
_FUNCION_SERVICIO = re.compile(r"^  (\w+): ")


def filtrar_operaciones(texto: str, operaciones: tuple[str, ...], guia: bool = True) -> str:
    """Deja en el objeto del servicio solo estas funciones (con sus comentarios).

    El objeto es `export const productoService = {` ... `};`, con una función por línea, y
    arriba de cada una, sus comentarios. Las funciones que no son de OPERACIONES (las que
    agregaste en una plantilla propia) quedan.
    """
    lineas = texto.split("\n")
    inicio = next((i for i, linea in enumerate(lineas) if _INICIO_SERVICIO.match(linea)), None)
    fin = next((i for i in range(inicio + 1, len(lineas)) if lineas[i] == "};"), None) if inicio is not None else None
    if inicio is None or fin is None:
        raise AndamioError(
            "--solo: no encontré el objeto del servicio (export const ...Service = { ... };) en la plantilla.",
            "Si usás plantillas propias, dejá el objeto con una función por línea, como en la original.",
        )
    cuerpo, bloque, encontradas = [], [], []
    for linea in lineas[inicio + 1 : fin]:
        bloque.append(linea)
        funcion = _FUNCION_SERVICIO.match(linea)
        if funcion:
            nombre = funcion.group(1)
            encontradas.append(nombre)
            if nombre in operaciones or nombre not in OPERACIONES:
                cuerpo += bloque
            bloque = []
    cuerpo += bloque  # lo que queda después de la última función (comentarios)
    faltan = [op for op in operaciones if op not in encontradas]
    if faltan:
        raise AndamioError(f"--solo: la plantilla del servicio no tiene {', '.join(faltan)}.")
    descartadas = [op for op in OPERACIONES if op in encontradas and op not in operaciones]
    aviso = []
    if guia and descartadas:
        elegidas = ", ".join(operaciones)
        aviso = [f"// Solo {elegidas} (--solo {','.join(operaciones)}): {', '.join(descartadas)} no se generaron."]
    return "\n".join([*lineas[:inicio], *aviso, lineas[inicio], *cuerpo, *lineas[fin:]])


def transformar_servicio(sol: Solicitud, ruta: str, texto: str) -> str:
    """Pieza.transformar del servicio: con --solo, el objeto solo con esas funciones."""
    # Sin --solo, o no es el archivo del servicio (http.ts también exporta un objeto: http).
    if not sol.opciones.get("solo") or not Path(ruta).stem.endswith(("Service", "Servicio")):
        return texto
    return filtrar_operaciones(texto, operaciones_pedidas(sol), sol.guia)


def hooks_del_servicio(carpeta: str) -> Callable[[Solicitud], frozenset[str]]:
    """Pieza.omitir del servicio: con --solo, solo los hooks que pueden usar sus funciones.

    useConsulta pide datos (listar u obtener); useFormulario carga, crea y actualiza.
    """

    def omitir(sol: Solicitud) -> frozenset[str]:
        ops = set(operaciones_pedidas(sol))
        sobran = () if ops & {"listar", "obtener"} else HOOK_CONSULTA
        if not {"obtener", "crear", "actualizar"} <= ops:
            sobran += HOOK_FORMULARIO
        return frozenset(f"{carpeta}/{archivo}" for archivo in sobran)

    return omitir


def pasos_servicio(
    pieza: str, nombres: tuple[str, str, str, str], a_mano: list[str], con_listar: list[str] = ()
) -> Callable[[Solicitud], list[str]]:
    """Los siguientes pasos de un servicio (React y React Native): las páginas o pantallas que
    lo pueden usar, según sus funciones (--solo).

    nombres: el de la lista, el de uno solo, el del formulario y el del formulario que solo envía.
    a_mano: cómo usarlo a mano; con_listar: lo que se suma si tiene listar (el ejemplo con useConsulta).
    """
    lista, uno, form, envio = nombres

    def pasos(sol: Solicitud) -> list[str]:
        ops = set(operaciones_pedidas(sol))
        comando = f"python -m andamio nuevo {pieza}"
        resultado = [f"# Una {'página' if pieza == 'pagina' else pieza} que lo usa:"]
        if "listar" in ops:
            resultado.append(f"{comando} {lista} --datos @@nombre@@")
        if "obtener" in ops:
            resultado.append(f"{comando} {uno} --datos @@nombre@@ --uno")
        if {"obtener", "crear", "actualizar"} <= ops:
            resultado.append(f"{comando} {form} --datos @@nombre@@ --form")
        elif "crear" in ops:
            explicacion = "con un formulario que solo envía (el servicio no tiene obtener ni actualizar)"
            if len(resultado) == 1:
                resultado = [f"# Una {'página' if pieza == 'pagina' else pieza} {explicacion}:"]
            else:
                resultado.append(f"# Y {explicacion[4:]}:")
            resultado.append(f"{comando} {envio} --datos @@nombre@@ --form")
        if len(resultado) == 1:
            resultado = []  # ej.: --solo eliminar: ninguna página generada lo usa
        return resultado + a_mano[:2] + (list(con_listar) if "listar" in ops else []) + a_mano[2:]

    return pasos


# Lo que suma --solo a la pieza servicio de cada stack: Pieza(..., **_js.OPCION_SOLO).
OPCION_SOLO = {
    "opciones": frozenset({"solo"}),
    "normalizar_opcion": {"solo": normalizar_solo},
    "transformar": transformar_servicio,
}


def operaciones_del_archivo(archivo: Path) -> set[str]:
    """Las funciones que tiene un servicio ya generado (las de OPERACIONES que encuentra)."""
    try:
        lineas = archivo.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError):
        return set(OPERACIONES)  # si no se puede leer, no se controla
    inicio = next((i for i, linea in enumerate(lineas) if _INICIO_SERVICIO.match(linea)), None)
    if inicio is None:
        return set(OPERACIONES)  # escrito a mano, de otra forma: no se controla
    encontradas = set()
    for linea in lineas[inicio + 1 :]:
        if linea.startswith("}"):
            break
        funcion = _FUNCION_SERVICIO.match(linea)
        if funcion and funcion.group(1) in OPERACIONES:
            encontradas.add(funcion.group(1))
    return encontradas


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


# --- Datos de la API en una página o pantalla (--datos producto [--uno | --form]) -------
#
# Tres formas de usar un servicio que ya existe, con los hooks de src/hooks (o hooks/):
#   lista  useConsulta(servicio.listar)
#   uno    useConsulta(() => servicio.obtener(id)), con el id en la ruta
#   form   useFormulario(servicio, id, VACIO, aDatos): crear, o editar si hay id


def normalizar_datos(texto: str) -> str:
    """--datos Producto, --datos item-pedido -> producto, item_pedido (el nombre del servicio, en singular)."""
    palabras = separar_palabras(texto, "El nombre del servicio (--datos)")
    if parece_plural(palabras):
        raise AndamioError(
            f"--datos va con el nombre del servicio en singular: '{texto}' parece plural.",
            "Ejemplo: --datos producto (usa el servicio productoService)",
        )
    return snake(palabras)


def modo_datos(sol: Solicitud) -> str:
    """"" (sin --datos), "lista", "uno" (--uno) o "form" (--form)."""
    uno, form = bool(sol.opciones.get("uno")), bool(sol.opciones.get("form"))
    ejemplo = f"{consola.programa()} nuevo {sol.pieza.clave} {sol.nombre.kebab} --datos producto"
    if not sol.opciones.get("datos"):
        if uno or form:
            opcion = "--uno" if uno else "--form"
            raise AndamioError(
                f"{opcion} va junto con --datos: dice qué hace la {sol.pieza.titulo.lower()} con esos datos.",
                f"Ejemplo: {ejemplo} {opcion}",
            )
        return ""
    if uno and form:
        raise AndamioError(
            "Elegí --uno (muestra uno solo) o --form (el formulario para crear y editar), no los dos.",
            f"Ejemplo: {ejemplo} --form",
        )
    return "uno" if uno else "form" if form else "lista"


def _archivo_servicio(sol: Solicitud, carpeta: str) -> tuple[str, str]:
    """El servicio que usa --datos (productoService) y su archivo."""
    servicio = f"{camel(sol.opciones['datos'].split('_'))}Service"
    return servicio, f"{carpeta}/{servicio}.{MARCADORES_VARIANTE[sol.variante or 'ts']['ext']}"


def solo_envia(sol: Solicitud, carpeta: str) -> bool:
    """--form con un servicio que no tiene obtener o actualizar (ej.: --solo crear).

    El formulario entonces solo envía: no carga ni edita registros (sin useFormulario ni /:id).
    """
    if not (sol.opciones.get("datos") and sol.opciones.get("form")):
        return False
    _, archivo = _archivo_servicio(sol, carpeta)
    return not {"obtener", "actualizar"} <= operaciones_del_archivo(sol.raiz / archivo)


def servicio_de_datos(sol: Solicitud, carpeta: str) -> tuple[str, str, list]:
    """Para --datos: el servicio que se usa (productoService), su archivo y sus campos.

    El servicio tiene que existir (no se crea: necesitaría los campos). Los campos salen del
    historial (con qué campos se generó); si no está, la lista vacía (el formulario los necesita).
    """
    datos = sol.opciones["datos"]
    servicio, archivo = _archivo_servicio(sol, carpeta)
    sugerencia = f"{consola.programa()} nuevo servicio {datos} nombre:str precio:decimal"
    pieza = sol.pieza.titulo.lower()
    if not (sol.raiz / archivo).is_file():
        raise AndamioError(
            f"La {pieza} usa {archivo}, que todavía no existe.",
            f"Generá primero el servicio, con los campos de la API: {sugerencia}",
        )
    # Un servicio generado con --solo puede no tener la función que usa la página.
    necesita = {"uno": "obtener", "form": "crear"}.get(modo_datos(sol), "listar")
    if necesita not in operaciones_del_archivo(sol.raiz / archivo):
        raise AndamioError(
            f"La {pieza} usa {servicio}.{necesita}, y {archivo} no la tiene (se generó con --solo).",
            f"Agregala en el servicio (un servicio completo la trae), o elegí lo que la {pieza} hace con "
            "el servicio: lista (listar), --uno (obtener) o --form (crear).",
        )
    campos = historial.campos_de(sol.raiz, datos, ("servicio", "crud")) or []
    if not campos and sol.opciones.get("form"):
        raise AndamioError(
            f"Para armar el formulario hacen falta los campos de {servicio}, y no están en el historial de andamio "
            f"({historial.ARCHIVO}).",
            f"Si el servicio lo hiciste a mano, borralo y generalo con andamio: {sugerencia}",
        )
    return servicio, archivo, campos


def campo_de_texto(campos, datos: str, variable: str = "item") -> str:
    """Lo que se muestra de cada registro en una lista: {item.nombre}, o {`Producto ${item.id}`}."""
    para_texto = next((c for c in campos if c.tipo in ("str", "email")), None)
    if para_texto:
        return f"{{{variable}.{para_texto.nombre}}}"
    return f"{{`{titulo(datos.split('_'))} ${{{variable}.id}}`}}"


def _consulta(sol: Solicitud, servicio: str, parametros: str) -> list[str]:
    """La llamada a useConsulta: la lista, o uno solo con el id de la ruta (--uno)."""
    if sol.opciones.get("uno"):
        explicacion = "// El id sale de la ruta; si cambia, useConsulta vuelve a pedir los datos."
        lineas = [
            f"const id = Number({parametros}.id);",
            f"const {{ datos, cargando, error }} = useConsulta(() => {servicio}.obtener(id), [id]);",
        ]
    else:
        explicacion = "// useConsulta pide los datos a la API (con useEffect) y avisa si está cargando o si falló."
        lineas = [f"const {{ datos, cargando, error }} = useConsulta({servicio}.listar);"]
    # Con guía, una línea que explica la consulta (la guía de los bloques se arma acá, no en la plantilla).
    return ([explicacion] if sol.guia else []) + lineas


def _formulario(sol: Solicitud, servicio: str, parametros: str, al_guardar: str, campos=()) -> list[str]:
    """La llamada a useFormulario y la función enviar() (con la marca para la lógica propia)."""
    lineas = [
        f"const {{ id }} = {parametros};",
        "const { datos, cambiar, errores, guardar, editando, cargado } = useFormulario(",
        f"  {servicio},",
        "  id === undefined ? undefined : Number(id),",
        "  VACIO,",
        "  aDatos,",
        ");",
        "",
        "async function enviar() {",
        "  // TODO(logica): validaciones del formulario antes de enviar (la API también valida).",
        "  // Ejemplo (sumá setErrores a lo que tomás de useFormulario):",
        f"  // {ejemplo_validacion(campos)}",
        "  const guardado = await guardar();",
        f"  if (guardado) {al_guardar};",
        "}",
    ]
    if sol.guia:
        lineas.insert(0, "// useFormulario carga el registro si hay un id (editar), y guarda con crear o actualizar.")
    return lineas


def _previo_formulario(sol: Solicitud, campos, nombre_tipo: str, ruta_servicio: str) -> str:
    """VACIO (los valores al crear) y aDatos (de un registro de la API al formulario), antes del componente."""
    vacios = [f"  {c.nombre}: {_VACIOS[c.tipo]}," for c in campos]
    copiar = [f"    {c.nombre}: registro.{c.nombre}{'.slice(0, 16)' if c.tipo == 'datetime' else ''}," for c in campos]
    datos_tipo = f"{nombre_tipo}Datos"
    if sol.variante == "js":
        cabecera = [
            f"/** @typedef {{import('{ruta_servicio}').{datos_tipo}}} {datos_tipo} */",
            "",
            "/**",
            " * Valores del formulario al crear uno nuevo.",
            f" * @type {{{datos_tipo}}}",
            " */",
            "const VACIO = {",
        ]
        funcion = [
            "/**",
            " * Pasa un registro de la API a los datos del formulario.",
            f" * @param {{import('{ruta_servicio}').{nombre_tipo}}} registro",
            f" * @returns {{{datos_tipo}}}",
            " */",
            "function aDatos(registro) {",
        ]
    else:
        cabecera = ["// Valores del formulario al crear uno nuevo.", f"const VACIO: {datos_tipo} = {{"]
        funcion = ["/** Pasa un registro de la API a los datos del formulario. */", f"function aDatos(registro: {nombre_tipo}): {datos_tipo} {{"]
    return "\n".join([*cabecera, *vacios, "};", "", *funcion, "  return {", *copiar, "  };", "}", ""])


# El formulario que solo envía (--form con un servicio --solo crear): sin useFormulario,
# con su propio estado. Es lo que se escribiría a mano para un formulario de contacto.


def _envio(sol: Solicitud, servicio: str, tipo: str, campos, rn: bool = False) -> list[str]:
    """El estado del formulario, cambiar() y enviar() (con la marca para la lógica propia).

    rn: en React Native, después de enviar se cuentan los envíos (enviados) en lugar de un
    sí/no: el número es la key de los campos, que así se vuelven a crear vacíos.
    """
    js = sol.variante == "js"
    datos_tipo = f"{tipo}Datos"
    ejemplo = campos[0].nombre if campos else "nombre"
    guia = (lambda *lineas: list(lineas)) if sol.guia else (lambda *lineas: [])
    lineas = guia("// El servicio solo tiene crear: el formulario solo envía (no carga ni edita registros).")
    if js:
        lineas += [
            "const [datos, setDatos] = useState(VACIO);",
            *guia(f"// Los errores de cada campo, como los devuelve la API: {{ {ejemplo}: ['...'] }}"),
            "const [errores, setErrores] = useState(/** @type {Record<string, string[]>} */ ({}));",
        ]
    else:
        lineas += [
            f"const [datos, setDatos] = useState<{datos_tipo}>(VACIO);",
            *guia(f"// Los errores de cada campo, como los devuelve la API: {{ {ejemplo}: ['...'] }}"),
            "const [errores, setErrores] = useState<Record<string, string[]>>({});",
        ]
    lineas.append("const [enviando, setEnviando] = useState(false);")
    lineas.append("const [enviados, setEnviados] = useState(0);" if rn else "const [enviado, setEnviado] = useState(false);")
    lineas.append("")
    if js:
        lineas += ["/**", f" * @param {{keyof {datos_tipo}}} campo", " * @param {unknown} valor", " */", "function cambiar(campo, valor) {"]
    else:
        lineas.append(f"function cambiar<K extends keyof {datos_tipo}>(campo: K, valor: {datos_tipo}[K]) {{")
    exito = ["    setEnviados((n) => n + 1);"] if rn else ["    setEnviado(true);"]
    detalle = "/** @type {Record<string, string[]>} */ (e.detalle)" if js else "e.detalle as Record<string, string[]>"
    lineas += [
        "  setDatos((actual) => ({ ...actual, [campo]: valor }));",
        "}",
        "",
        "async function enviar() {",
        "  // TODO(logica): validaciones del formulario antes de enviar (la API también valida).",
        "  // Ejemplo:",
        f"  // {ejemplo_validacion(campos)}",
        "  setErrores({});",
        "  setEnviando(true);",
        "  try {",
        f"    await {servicio}.crear(datos);",
        *exito,
        "    setDatos(VACIO);" + (" // vacío otra vez, listo para otro" if sol.guia else ""),
        "  } catch (e) {",
        *guia("    // 400: la API dice qué está mal en cada campo. Otro error (ej.: sin conexión), en general."),
        "    if (e instanceof ErrorApi && e.estado === 400) {",
        f"      setErrores({detalle});",
        "    } else {",
        "      setErrores({ general: [e instanceof Error ? e.message : String(e)] });",
        "    }",
        "  } finally {",
        "    setEnviando(false);",
        "  }",
        "}",
    ]
    return lineas


def _previo_envio(sol: Solicitud, campos, tipo: str, ruta_servicio: str) -> str:
    """VACIO: los valores del formulario al empezar (y después de enviar)."""
    vacios = [f"  {c.nombre}: {_VACIOS[c.tipo]}," for c in campos]
    datos_tipo = f"{tipo}Datos"
    if sol.variante == "js":
        cabecera = [
            f"/** @typedef {{import('{ruta_servicio}').{datos_tipo}}} {datos_tipo} */",
            "",
            "/**",
            " * Valores del formulario al empezar (y después de enviar).",
            f" * @type {{{datos_tipo}}}",
            " */",
            "const VACIO = {",
        ]
    else:
        cabecera = ["// Valores del formulario al empezar (y después de enviar).", f"const VACIO: {datos_tipo} = {{"]
    return "\n".join([*cabecera, *vacios, "};", ""])


def _import_servicio(sol: Solicitud, servicio: str, ruta: str, nombre_tipo: str, envio: bool = False) -> str:
    if sol.opciones.get("form") and sol.variante != "js":
        # El formulario que solo envía no pasa registros de la API al formulario (aDatos).
        tipos = f"type {nombre_tipo}Datos" if envio else f"type {nombre_tipo}, type {nombre_tipo}Datos"
        return f"import {{ {servicio}, {tipos} }} from '{ruta}';"
    return f"import {{ {servicio} }} from '{ruta}';"


def _valor(campo, variable: str = "datos") -> str:
    if campo.tipo == "bool":
        return f"{{{variable}.{campo.nombre} ? 'Sí' : 'No'}}"
    if campo.tipo == relaciones.TIPO:
        # El texto que manda la API de Django; si no está (otras APIs), el id.
        return f"{{{variable}.{campo.nombre}_texto ?? {variable}.{campo.nombre}}}"
    return f"{{{variable}.{campo.nombre}}}"


_VACIOS_DATOS = ("datos_imports", "datos_previo", "datos_consulta", "datos_contenido", "datos_servicio", "datos_hook")


def _archivo_hook(sol: Solicitud, carpeta: str, modo: str) -> str:
    """El hook que usa la página ("" si ninguno: el formulario que solo envía, sin relaciones)."""
    if modo == "envio" and not usa_relaciones(sol):
        return ""
    hook = "useFormulario" if modo == "form" else "useConsulta"
    return f"{carpeta}/{hook}.{MARCADORES_VARIANTE[sol.variante or 'ts']['ext']}"


HOOK_CONSULTA = ("useConsulta.ts", "useConsulta.js")
HOOK_FORMULARIO = ("useFormulario.ts", "useFormulario.js")


def hooks_a_omitir(carpeta: str, servicios: str) -> Callable[[Solicitud], frozenset[str]]:
    """Pieza.omitir: cada página o pantalla crea solo el hook que usa (y solo si falta).

    carpeta: la de los hooks; servicios: la de los servicios (para ver qué funciones tiene).
    """

    def omitir(sol: Solicitud) -> frozenset[str]:
        modo = sol.opciones.get("datos") and ("form" if sol.opciones.get("form") else "consulta")
        if modo == "form" and solo_envia(sol, servicios):
            modo = "consulta" if usa_relaciones(sol) else ""  # sin useFormulario
        elif modo == "form" and usa_relaciones(sol):
            modo = "ambos"  # el formulario carga con useConsulta la lista de cada relación
        sobran = {"consulta": HOOK_FORMULARIO, "form": HOOK_CONSULTA, "ambos": ()}.get(modo, HOOK_CONSULTA + HOOK_FORMULARIO)
        return frozenset(f"{carpeta}/{archivo}" for archivo in sobran)

    return omitir


def hooks(carpeta: str) -> frozenset[str]:
    return frozenset(f"{carpeta}/{archivo}" for archivo in HOOK_CONSULTA + HOOK_FORMULARIO)


# Relaciones (campo:fk) en los formularios: se elige de la lista del otro servicio.


class RelacionJs:
    """Un campo :fk en un formulario: su servicio (categoriaService) y la lista (categorias)."""

    def __init__(self, rel: relaciones.Relacion, servicio: str, variable: str) -> None:
        self.campo, self.servicio, self.variable = rel.campo, servicio, variable
        self.etiqueta = campo_de_texto(rel.campos, rel.campo.nombre, "opcion")


def relaciones_formulario(sol: Solicitud, campos, propio: Nombre, carpeta: str) -> dict[str, RelacionJs]:
    """Los campos :fk de un formulario, controlando que exista el servicio de cada uno."""
    ext = MARCADORES_VARIANTE[sol.variante or "ts"]["ext"]
    resultado = {}
    for rel in relaciones.de_campos(sol.raiz, campos, propio, ("servicio", "crud")):
        servicio = f"{rel.destino.camel}Service"
        if not (sol.raiz / carpeta / f"{servicio}.{ext}").is_file():
            raise relaciones.falta(
                rel.campo, f"el servicio {servicio} (para elegir de su lista)", f"python -m andamio nuevo servicio {rel.campo.nombre} nombre:str"
            )
        resultado[rel.campo.nombre] = RelacionJs(rel, servicio, camel(rel.destino.plural_palabras))
    return resultado


def _imports_relaciones(rels: dict[str, RelacionJs], ruta: str) -> list[str]:
    return [f"import {{ {r.servicio} }} from '{ruta}/{r.servicio}';" for r in rels.values()]


def _consultas_relaciones(rels: dict[str, RelacionJs]) -> list[str]:
    # Cada relación se elige de una lista: se pide con useConsulta, como cualquier otra lista.
    return [f"const {{ datos: {r.variable} }} = useConsulta({r.servicio}.listar);" for r in rels.values()]


def usa_relaciones(sol: Solicitud) -> bool:
    """Si el servicio que usa la página (--datos) tiene campos :fk (el formulario necesita useConsulta)."""
    datos = sol.opciones.get("datos")
    campos = historial.campos_de(sol.raiz, datos, ("servicio", "crud")) if datos else None
    return any(c.tipo == relaciones.TIPO for c in campos or [])


# React (pagina)

MARCADORES_PAGINA = {
    "ruta_pagina": "la ruta de la página: /contacto, o /producto-detalle/:id con --uno",
    "url_pagina": "la dirección para abrirla: /contacto, o /producto-detalle/1 con --uno",
    "datos_imports": "imports del hook y del servicio (vacío sin --datos)",
    "datos_previo": "con --form: VACIO y aDatos, antes del componente (vacío si no)",
    "datos_consulta": "la llamada a useConsulta o useFormulario (vacío sin --datos)",
    "datos_contenido": "cargando, error y los datos: una lista, uno solo (--uno) o el formulario (--form)",
    "datos_css": "con --form: los estilos del formulario (vacío si no)",
    "datos_servicio": "el archivo del servicio que usa (vacío sin --datos)",
    "datos_hook": "el archivo del hook que usa: useConsulta o useFormulario (vacío sin --datos)",
}

_CARGANDO_Y_ERROR = [
    "{cargando && <p>Cargando…</p>}",
    "{error && <p role=\"alert\">No se pudo cargar: {error}</p>}",
]

_CSS_FORMULARIO = """
.formulario {
  display: grid;
  gap: 14px;
  max-width: 480px;
}

.campo {
  display: grid;
  gap: 4px;
  font-weight: 600;
}

.campo input:not([type='checkbox']),
.campo textarea {
  font: inherit;
  font-weight: normal;
  padding: 6px 8px;
}

.acciones {
  display: flex;
  gap: 8px;
}

.error {
  color: #b42318;
  font-weight: normal;
}"""

_CSS_ENVIO = """

.exito {
  color: #067647;
  font-weight: 600;
}"""


def contexto_pagina(sol: Solicitud) -> dict[str, str]:
    modo = modo_datos(sol)
    ruta = f"/{sol.nombre.kebab}"
    if not modo:
        return {**dict.fromkeys(_VACIOS_DATOS, ""), "datos_css": "", "ruta_pagina": ruta, "url_pagina": ruta}

    datos = sol.opciones["datos"]
    servicio, archivo_servicio, campos = servicio_de_datos(sol, "src/services")
    tipo = pascal(datos.split("_"))
    ruta_servicio = f"../../services/{servicio}"
    envio = modo == "form" and solo_envia(sol, "src/services")
    if envio:
        rels = relaciones_formulario(sol, campos, Nombre.desde_palabras(datos.split("_")), "src/services")
        imports = ["import { useState } from 'react';"]
        imports += ["import { useConsulta } from '../../hooks/useConsulta';"] if rels else []
        imports += ["import { ErrorApi } from '../../services/http';", *_imports_relaciones(rels, "../../services")]
        consulta = [*_envio(sol, servicio, tipo, campos), *_consultas_relaciones(rels)]
        contenido = _contenido_envio(campos, rels)
    elif modo == "form":
        rels = relaciones_formulario(sol, campos, Nombre.desde_palabras(datos.split("_")), "src/services")
        imports = ["import { useNavigate, useParams } from 'react-router';"]
        imports += ["import { useConsulta } from '../../hooks/useConsulta';"] if rels else []
        imports += ["import { useFormulario } from '../../hooks/useFormulario';", *_imports_relaciones(rels, "../../services")]
        consulta = ["const navegar = useNavigate();", *_formulario(sol, servicio, "useParams()", "navegar(-1)", campos), *_consultas_relaciones(rels)]
        contenido = _contenido_formulario(campos, rels)
    else:
        imports = (["import { useParams } from 'react-router';"] if modo == "uno" else []) + ["import { useConsulta } from '../../hooks/useConsulta';"]
        consulta = _consulta(sol, servicio, "useParams()")
        contenido = _contenido_uno(campos) if modo == "uno" else _contenido_lista(campos, datos)
    imports.append(_import_servicio(sol, servicio, ruta_servicio, tipo, envio))
    if envio:
        previo = _previo_envio(sol, campos, tipo, ruta_servicio)
    else:
        previo = _previo_formulario(sol, campos, tipo, ruta_servicio) if modo == "form" else ""
    return {
        "ruta_pagina": f"{ruta}/:id" if modo == "uno" else ruta,
        "url_pagina": f"{ruta}/1" if modo == "uno" else ruta,
        "datos_imports": "\n".join(imports),
        "datos_previo": previo,
        "datos_consulta": "\n".join(consulta) + "\n",
        "datos_contenido": "\n".join(contenido),
        "datos_css": (_CSS_FORMULARIO + _CSS_ENVIO if envio else _CSS_FORMULARIO) if modo == "form" else "",
        "datos_servicio": archivo_servicio,
        "datos_hook": _archivo_hook(sol, "src/hooks", "envio" if envio else modo),
    }


def _contenido_lista(campos, datos: str) -> list[str]:
    return [
        *_CARGANDO_Y_ERROR,
        "{datos?.length === 0 && <p>Todavía no hay registros.</p>}",
        "<ul>",
        "  {datos?.map((item) => (",
        f"    <li key={{item.id}}>{campo_de_texto(campos, datos)}</li>",
        "  ))}",
        "</ul>",
    ]


def _contenido_uno(campos) -> list[str]:
    if not campos:
        # Sin los campos (el servicio no está en el historial): se muestra todo lo que llegó.
        return [*_CARGANDO_Y_ERROR, "{datos && <pre>{JSON.stringify(datos, null, 2)}</pre>}"]
    filas = []
    for c in campos:
        filas += [f"    <dt>{c.titulo}</dt>", f"    <dd>{_valor(c)}</dd>"]
    return [*_CARGANDO_Y_ERROR, "{datos && (", "  <dl>", *filas, "  </dl>", ")}"]


def _contenido_formulario(campos, rels) -> list[str]:
    controles = [f"  {linea}" for c in campos for linea in _campo_formulario(c, rels)]
    return [
        "{!cargado && <p>Cargando…</p>}",
        "<form",
        "  className={styles.formulario}",
        "  onSubmit={(evento) => {",
        "    evento.preventDefault();",
        "    void enviar();",
        "  }}",
        ">",
        *controles,
        "  {errores.general && <p className={styles.error}>{errores.general.join(' ')}</p>}",
        "  <div className={styles.acciones}>",
        "    <button type=\"submit\">{editando ? 'Guardar cambios' : 'Agregar'}</button>",
        "    <button type=\"button\" onClick={() => navegar(-1)}>",
        "      Cancelar",
        "    </button>",
        "  </div>",
        "</form>",
    ]


def _contenido_envio(campos, rels) -> list[str]:
    controles = [f"  {linea}" for c in campos for linea in _campo_formulario(c, rels)]
    return [
        "{enviado && (",
        "  <p role=\"status\" className={styles.exito}>",
        "    ¡Listo! Se envió.",
        "  </p>",
        ")}",
        "<form",
        "  className={styles.formulario}",
        "  onSubmit={(evento) => {",
        "    evento.preventDefault();",
        "    void enviar();",
        "  }}",
        ">",
        *controles,
        "  {errores.general && <p className={styles.error}>{errores.general.join(' ')}</p>}",
        "  <div className={styles.acciones}>",
        "    <button type=\"submit\" disabled={enviando}>",
        "      {enviando ? 'Enviando…' : 'Enviar'}",
        "    </button>",
        "  </div>",
        "</form>",
    ]


def form_edita(sol: Solicitud) -> bool:
    """Inserción.condicion (React): la ruta /x/:id para editar, solo con un --form que edita."""
    return bool(sol.opciones.get("form")) and not solo_envia(sol, "src/services")


def pasos_pagina(sol: Solicitud) -> list[str]:
    pasos = ["npm run dev", "http://localhost:5173@@url_pagina@@"]
    if form_edita(sol):
        pasos.append("# Para editar uno, la misma página con su id: http://localhost:5173@@url_pagina@@/1")
    if sol.opciones.get("datos"):
        pasos.append("# Necesita la API andando (Django, FastAPI o Express), con el recurso que usa el servicio.")
    return pasos_router(pasos)(sol)


# React Native (pantalla)


def contexto_pantalla(sol: Solicitud) -> dict[str, str]:
    carpeta = sol.opciones.get("carpeta", "")
    archivo = sol.nombre.kebab
    if sol.opciones.get("uno"):
        # Uno solo: el id es parte de la ruta. En Expo Router, [id] es la parte variable.
        archivo += "/[id]"
    ruta = f"{carpeta}/{archivo}" if carpeta else archivo
    # Los grupos "(tabs)" no forman parte de la URL, y "index" es la ruta de la carpeta.
    segmentos = [p for p in ruta.split("/") if not p.startswith("(")]
    if segmentos and segmentos[-1] == "index":
        segmentos.pop()
    url = "/" + "/".join(segmentos)
    return {
        "ruta_pantalla": ruta,
        "url_pantalla": url,
        "url_abrir": url.replace("[id]", "1"),
        **_contexto_pantalla_datos(sol),
    }


_ESTILO_ERROR = ["error: {", "  color: '#b91c1c',", "  marginVertical: 8,", "},"]
_ESTILOS_CAMPOS_RN = ["etiqueta: {", "  fontWeight: 'bold',", "  marginTop: 12,", "},", "entrada: {",
                      "  borderWidth: 1,", "  borderColor: '#d0d5dd',", "  borderRadius: 6,", "  padding: 8,", "  marginTop: 4,", "},"]  # fmt: skip
_ESTILOS_OPCIONES_RN = ["opciones: {", "  flexDirection: 'row',", "  flexWrap: 'wrap',", "  gap: 8,", "  marginTop: 4,", "},",
                        "opcion: {", "  borderWidth: 1,", "  borderColor: '#d0d5dd',", "  borderRadius: 16,", "  paddingHorizontal: 12,", "  paddingVertical: 6,", "},",
                        "elegida: {", "  borderColor: '#2563eb',", "  backgroundColor: '#dbeafe',", "},"]  # fmt: skip


def _contexto_pantalla_datos(sol: Solicitud) -> dict[str, str]:
    """React Native: los bloques de una pantalla con --datos (lista con FlatList, uno solo o formulario)."""
    modo = modo_datos(sol)
    if not modo:
        return {**dict.fromkeys(_VACIOS_DATOS, ""), "datos_estilos": "", "expo_router": "Stack", "react_native": "StyleSheet, Text, View"}

    datos = sol.opciones["datos"]
    servicio, archivo_servicio, campos = servicio_de_datos(sol, "services")
    tipo = pascal(datos.split("_"))
    ruta_servicio = f"@/services/{servicio}"
    cargando_y_error = [
        "{cargando && <ActivityIndicator />}",
        "{error && <Text style={styles.error}>No se pudo cargar: {error}</Text>}",
    ]
    envio = modo == "form" and solo_envia(sol, "services")
    if envio:
        rels = relaciones_formulario(sol, campos, Nombre.desde_palabras(datos.split("_")), "services")
        hook = "\n".join(
            ["import { useState } from 'react';"]
            + (["import { useConsulta } from '@/hooks/useConsulta';"] if rels else [])
            + ["import { ErrorApi } from '@/services/http';", *_imports_relaciones(rels, "@/services")]
        )
        consulta = [*_envio(sol, servicio, tipo, campos, rn=True), *_consultas_relaciones(rels)]
        contenido = _contenido_envio_rn(campos, rels, sol.guia)
        # Solo los componentes que usan los campos (Switch para sí/no, Pressable para las relaciones).
        tipos = {"rel" if c.nombre in rels else "bool" if c.tipo == "bool" else "texto" for c in campos}
        componentes = ", ".join(
            ["Button"] + (["Pressable"] if "rel" in tipos else []) + ["ScrollView", "StyleSheet"]
            + (["Switch"] if "bool" in tipos else []) + ["Text"] + (["TextInput"] if "texto" in tipos else []) + ["View"]
        )
        router = "Stack"
        estilos = [*_ESTILO_ERROR, "exito: {", "  color: '#067647',", "  fontWeight: 'bold',", "  marginVertical: 8,", "},",
                   *_ESTILOS_CAMPOS_RN]  # fmt: skip
        if rels:
            estilos += _ESTILOS_OPCIONES_RN
    elif modo == "form":
        rels = relaciones_formulario(sol, campos, Nombre.desde_palabras(datos.split("_")), "services")
        hook = "\n".join(
            (["import { useConsulta } from '@/hooks/useConsulta';"] if rels else [])
            + ["import { useFormulario } from '@/hooks/useFormulario';", *_imports_relaciones(rels, "@/services")]
        )
        consulta = [*_formulario(sol, servicio, "useLocalSearchParams()", "router.back()", campos), *_consultas_relaciones(rels)]
        contenido = _contenido_formulario_rn(campos, rels)
        componentes = "ActivityIndicator, Button, " + ("Pressable, " if rels else "") + "ScrollView, StyleSheet, Switch, Text, TextInput, View"
        router = "Stack, router, useLocalSearchParams"
        estilos = [*_ESTILO_ERROR, *_ESTILOS_CAMPOS_RN]
        if rels:
            estilos += _ESTILOS_OPCIONES_RN
    elif modo == "uno":
        hook = "import { useConsulta } from '@/hooks/useConsulta';"
        consulta = _consulta(sol, servicio, "useLocalSearchParams()")
        contenido = [*cargando_y_error, *_contenido_uno_rn(campos)]
        componentes = "ActivityIndicator, StyleSheet, Text, View"
        router = "Stack, useLocalSearchParams"
        estilos = [*_ESTILO_ERROR, "etiqueta: {", "  fontWeight: 'bold',", "  marginTop: 8,", "},"]
    else:
        hook = "import { useConsulta } from '@/hooks/useConsulta';"
        consulta = _consulta(sol, servicio, "useLocalSearchParams()")
        contenido = [
            *cargando_y_error,
            "<FlatList",
            "  data={datos ?? []}",
            "  keyExtractor={(item) => String(item.id)}",
            f"  renderItem={{({{ item }}) => <Text style={{styles.item}}>{campo_de_texto(campos, datos)}</Text>}}",
            "  ListEmptyComponent={cargando ? undefined : <Text>Todavía no hay registros.</Text>}",
            "/>",
        ]
        componentes = "ActivityIndicator, FlatList, StyleSheet, Text, View"
        router = "Stack"
        estilos = [*_ESTILO_ERROR, "item: {", "  paddingVertical: 8,", "  borderBottomWidth: StyleSheet.hairlineWidth,", "},"]
    return {
        "expo_router": router,
        "react_native": componentes,
        "datos_imports": "\n".join(["", hook, _import_servicio(sol, servicio, ruta_servicio, tipo, envio)]),
        "datos_previo": (
            _previo_envio(sol, campos, tipo, ruta_servicio) if envio
            else _previo_formulario(sol, campos, tipo, ruta_servicio) if modo == "form" else ""
        ),
        "datos_consulta": "\n".join(consulta) + "\n",
        "datos_contenido": "\n".join(contenido),
        "datos_estilos": "\n".join(estilos),
        "datos_servicio": archivo_servicio,
        "datos_hook": _archivo_hook(sol, "hooks", "envio" if envio else modo),
    }


def _contenido_uno_rn(campos) -> list[str]:
    if not campos:
        return ["{datos && <Text>{JSON.stringify(datos, null, 2)}</Text>}"]
    filas = []
    for c in campos:
        filas += [f"    <Text style={{styles.etiqueta}}>{c.titulo}</Text>", f"    <Text>{_valor(c)}</Text>"]
    return ["{datos && (", "  <View>", *filas, "  </View>", ")}"]


_TECLADOS_RN = {"int": "number-pad", "decimal": "decimal-pad", "float": "decimal-pad", "email": "email-address"}
_EJEMPLOS_RN = {"date": "2025-03-15", "datetime": "2025-03-15T10:30"}


def _campo_formulario_rn(campo, rels=None, edita: bool = True) -> list[str]:
    n = campo.nombre
    if rels and n in rels:
        rel = rels[n]
        # Se elige tocando una de las opciones (la elegida queda resaltada).
        control = [
            "<View style={styles.opciones}>",
            f"  {{{rel.variable}?.map((opcion) => (",
            "    <Pressable",
            "      key={opcion.id}",
            f"      onPress={{() => cambiar('{n}', opcion.id)}}",
            f"      style={{[styles.opcion, datos.{n} === opcion.id && styles.elegida]}}",
            "    >",
            f"      <Text>{rel.etiqueta}</Text>",
            "    </Pressable>",
            "  ))}",
            "</View>",
        ]
    elif campo.tipo == "bool":
        control = [f"<Switch value={{datos.{n}}} onValueChange={{(valor) => cambiar('{n}', valor)}} />"]
    elif campo.tipo in ("int", "decimal", "float"):
        # Sin value (no controlado): así se puede escribir "12." mientras se tipea un decimal.
        control = [
            "<TextInput",
            "  style={styles.entrada}",
            f"  keyboardType=\"{_TECLADOS_RN[campo.tipo]}\"",
            *([f"  defaultValue={{editando ? String(datos.{n}) : ''}}"] if edita else []),
            f"  onChangeText={{(texto) => cambiar('{n}', Number(texto.replace(',', '.')))}}",
            "/>",
        ]
    else:
        extras = []
        if campo.tipo in _TECLADOS_RN:
            extras.append(f"  keyboardType=\"{_TECLADOS_RN[campo.tipo]}\"")
            extras.append("  autoCapitalize=\"none\"")
        if campo.tipo == "text":
            extras.append("  multiline")
        if campo.tipo in _EJEMPLOS_RN:
            extras.append(f"  placeholder=\"{_EJEMPLOS_RN[campo.tipo]}\"")
        control = [
            "<TextInput",
            "  style={styles.entrada}",
            *extras,
            f"  value={{datos.{n}}}",
            f"  onChangeText={{(texto) => cambiar('{n}', texto)}}",
            "/>",
        ]
    return [
        f"<Text style={{styles.etiqueta}}>{campo.titulo}</Text>",
        *control,
        f"{{errores.{n} && <Text style={{styles.error}}>{{errores.{n}.join(' ')}}</Text>}}",
    ]


def _contenido_formulario_rn(campos, rels) -> list[str]:
    controles = [f"    {linea}" for c in campos for linea in _campo_formulario_rn(c, rels)]
    return [
        "{!cargado ? (",
        "  <ActivityIndicator />",
        ") : (",
        "  <ScrollView>",
        *controles,
        "    {errores.general && <Text style={styles.error}>{errores.general.join(' ')}</Text>}",
        "    <Button title={editando ? 'Guardar cambios' : 'Agregar'} onPress={() => void enviar()} />",
        "  </ScrollView>",
        ")}",
    ]


def _contenido_envio_rn(campos, rels, guia: bool) -> list[str]:
    controles = [f"    {linea}" for c in campos for linea in _campo_formulario_rn(c, rels, edita=False)]
    explicacion = ["  {/* key: con cada envío, los campos se vuelven a crear (vacíos). */}"] if guia else []
    return [
        "<ScrollView>",
        "  {enviados > 0 && <Text style={styles.exito}>¡Listo! Se envió.</Text>}",
        *explicacion,
        "  <View key={enviados}>",
        *controles,
        "  </View>",
        "  {errores.general && <Text style={styles.error}>{errores.general.join(' ')}</Text>}",
        "  <Button title={enviando ? 'Enviando…' : 'Enviar'} disabled={enviando} onPress={() => void enviar()} />",
        "</ScrollView>",
    ]


MARCADORES_PANTALLA = {
    **MARCADORES_EXTENSION,
    "ruta_pantalla": "archivo dentro de app/, sin extensión: productos/detalle-producto (con --uno: producto/[id])",
    "url_pantalla": "ruta para navegar: /productos/detalle-producto (con --uno: /producto/[id])",
    "url_abrir": "una dirección de ejemplo para abrirla: /producto/1 con --uno",
    "expo_router": "lo que se importa de expo-router: Stack (y useLocalSearchParams, router con --uno o --form)",
    "react_native": "lo que se importa de react-native: StyleSheet, Text, View (y FlatList, ActivityIndicator con --datos)",
    "datos_imports": "imports del hook y del servicio (vacío sin --datos)",
    "datos_previo": "con --form: VACIO y aDatos, antes del componente (vacío si no)",
    "datos_consulta": "la llamada a useConsulta o useFormulario (vacío sin --datos)",
    "datos_contenido": "cargando, error y los datos: FlatList, uno solo (--uno) o el formulario (--form)",
    "datos_estilos": "estilos de la lista, del detalle o del formulario (vacío sin --datos)",
    "datos_servicio": "el archivo del servicio que usa (vacío sin --datos)",
    "datos_hook": "el archivo del hook que usa: useConsulta o useFormulario (vacío sin --datos)",
}


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
    rels = relaciones_formulario(sol, sol.campos, sol.nombre, "src/services")
    contexto["imports_relaciones"] = "\n".join(
        (["import { useConsulta } from '../../hooks/useConsulta';"] if rels else []) + _imports_relaciones(rels, "../../services")
    )
    contexto["consultas_relaciones"] = "\n".join(_consultas_relaciones(rels))
    para_texto = next((c for c in sol.campos if c.tipo in ("str", "email")), None)
    contexto["texto_item"] = f"item.{para_texto.nombre}" if para_texto else f"`{sol.nombre.pascal} ${{item.id}}`"

    detalle, vacios, copiar, formulario = [], [], [], []
    for c in sol.campos:
        valor = f"{variable}.{c.nombre}"
        detalle += [f"<dt>{c.titulo}</dt>", f"<dd>{_valor(c, variable)}</dd>"]
        vacios.append(f"{c.nombre}: {_VACIOS[c.tipo]},")
        copiar.append(f"{c.nombre}: registro.{c.nombre}{'.slice(0, 16)' if c.tipo == 'datetime' else ''},")
        formulario += _campo_formulario(c, rels)
    contexto.update(
        campos_detalle="\n".join(detalle),
        valores_vacios="\n".join(vacios),
        campos_copiar="\n".join(copiar),
        campos_formulario="\n".join(formulario),
    )
    return contexto


_VACIOS = {"str": "''", "text": "''", "email": "''", "date": "''", "datetime": "''", "int": "0", "decimal": "0", "float": "0", "bool": "false", "fk": "null"}

_PASOS_NUMERICOS = {"int": "1", "decimal": "0.01", "float": "any"}


def _campo_formulario(campo, rels=None) -> list[str]:
    n = campo.nombre
    if rels and n in rels:
        rel = rels[n]
        # Se elige de la lista del otro servicio; "" (sin elegir) se guarda como null.
        control = "\n  ".join([
            f"<select value={{datos.{n} ?? ''}} onChange={{(e) => cambiar('{n}', e.target.value === '' ? null : Number(e.target.value))}}>",
            "  <option value=\"\">(sin elegir)</option>",
            f"  {{{rel.variable}?.map((opcion) => (",
            "    <option key={opcion.id} value={opcion.id}>",
            f"      {rel.etiqueta}",
            "    </option>",
            "  ))}",
            "</select>",
        ])  # fmt: skip
    elif campo.tipo == "bool":
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
    "imports_relaciones": "React: imports de useConsulta y del servicio de cada relación (vacío sin campos :fk)",
    "consultas_relaciones": "React: la lista de cada relación, para elegir en el formulario (vacío sin campos :fk)",
}

contexto_crud = _contexto_crud
