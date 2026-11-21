"""Arma el Plan de cambios a partir de un stack, una pieza y los datos del alumno."""

from __future__ import annotations

import dataclasses
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from andamio.nucleo import ajustes, historial, identificadores, plantillas
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.motor import renderizar, renderizar_ruta
from andamio.nucleo.nombres import (
    Nombre,
    kebab,
    pascal,
    pluralizar,
    separar_palabras,
    snake,
    titulo,
    validar_nombre,
    validar_nombre_carpeta,
)
from andamio.nucleo.insercion import ya_presente
from andamio.nucleo.plan import Plan

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

    from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack


# --- Nombres ----------------------------------------------------------------


def nombre_para_pieza(pieza: Pieza, texto: str, plural: str | None = None) -> Nombre:
    palabras = separar_palabras(texto)
    if pieza.ajustar_palabras:
        palabras = pieza.ajustar_palabras(palabras)
        if not palabras:
            raise AndamioError(f"Al nombre '{texto}' le falta la parte principal.")
    plural_palabras = separar_palabras(plural, "El plural") if plural else pluralizar(palabras)
    return Nombre.desde_palabras(palabras, plural_palabras)


def validar_nombre_pieza(stack: Stack, raiz: Path, nombre: Nombre, pieza: Pieza | None = None) -> None:
    validar_nombre(nombre)
    # Primero la validación de la pieza: es la más específica y da el mejor consejo.
    if pieza is not None and pieza.validar_nombre:
        pieza.validar_nombre(raiz, nombre)
    if stack.validar_nombre and not (pieza is not None and pieza.usa_existente):
        stack.validar_nombre(raiz, nombre)


def _error_identificador(pieza: Pieza, forma: str, donde: str) -> AndamioError:
    return AndamioError(
        f"No se puede usar '{forma}' como nombre: en {donde} el código ya usa '{forma}' para otra cosa "
        "(el código generado no funcionaría).",
        "Elegí otro nombre" + (", o indicá otro plural con --plural." if pieza.usa_plural else "."),
    )


def describir_nombre(pieza: Pieza, nombre: Nombre) -> str:
    formas: list[str] = []
    for forma in pieza.formas:
        valor = renderizar(forma, nombre.marcadores()) if "@@" in forma else nombre.forma(forma)
        if valor not in formas:
            formas.append(valor)
    texto = " / ".join(formas)
    if pieza.usa_plural:
        texto += f"  (plural: {nombre.plural})"
    return texto


def carpeta_proyecto(texto: str) -> str:
    carpeta = kebab(separar_palabras(texto, "El nombre del proyecto"))
    validar_nombre_carpeta(carpeta)
    return carpeta


# --- Plantillas -------------------------------------------------------------


def carpeta_plantillas(stack: Stack, variante: str = "") -> Traversable:
    """Carpeta de plantillas incorporadas del stack (y de la variante, si tiene)."""
    base = stack.plantillas if stack.plantillas is not None else plantillas.carpeta_incorporada(stack.clave)
    return base / variante if variante else base


def stack_base(stack: Stack) -> Stack | None:
    """El stack que este extiende (Stack.extiende), o None."""
    if not stack.extiende:
        return None
    from andamio.stacks import por_clave

    base = por_clave(stack.extiende)
    if base is None:
        raise AndamioError(f"El stack '{stack.clave}' extiende a '{stack.extiende}', que no existe.")
    return base


def carpeta_pieza(stack: Stack, pieza: Pieza, variante: str = "") -> Traversable:
    """Carpeta incorporada de una pieza: la del stack o, si no la tiene, la del stack que extiende."""
    propia = carpeta_plantillas(stack, variante) / pieza.clave
    base = stack_base(stack)
    if base is not None and not propia.is_dir():
        return carpeta_pieza(base, pieza, variante)
    return propia


def archivos_proyecto(stack: Stack, variante: str = "") -> list[plantillas.ArchivoPlantilla]:
    """Los archivos de _proyecto: los del stack que extiende (si hay) y después los propios."""
    archivos: dict[str, plantillas.ArchivoPlantilla] = {}
    base = stack_base(stack)
    if base is not None:
        archivos.update((a.ruta, a) for a in archivos_proyecto(base, variante))
    carpeta = carpeta_plantillas(stack, variante) / plantillas.CARPETA_PROYECTO
    archivos.update((a.ruta, a) for a in plantillas.leer_arbol(carpeta, ignorar_leeme=False))
    return [archivos[ruta] for ruta in sorted(archivos)]


def ubicar_plantilla(stack: Stack, pieza: Pieza, raiz: Path, variante: str = "") -> tuple[Traversable, bool]:
    """Devuelve la carpeta de plantillas a usar y si es la personalizada por el alumno."""
    propia = plantillas.carpeta_personalizada(raiz, stack.clave, pieza.clave)
    if propia.is_dir():
        return propia, True
    return carpeta_pieza(stack, pieza, variante), False


# --- Variantes --------------------------------------------------------------


def resolver_variante(stack: Stack, pedida: str | None) -> str:
    """La variante para un proyecto nuevo: la pedida (validada) o la primera del stack."""
    if not stack.variantes:
        if pedida:
            raise AndamioError(f"Los proyectos {stack.titulo} no tienen variantes; sacá la opción --variante/--js/--ts.")
        return ""
    if pedida is None:
        return next(iter(stack.variantes))
    pedida = pedida.strip().lower()
    if pedida not in stack.variantes:
        disponibles = ", ".join(f"{k} ({v})" for k, v in stack.variantes.items())
        raise AndamioError(f"'{pedida}' no es una variante de {stack.titulo}.", f"Variantes: {disponibles}")
    return pedida


def variante_del_proyecto(stack: Stack, raiz: Path) -> str:
    if not stack.variantes:
        return ""
    configurada = ajustes.de_proyecto(raiz).variante
    if configurada:
        if configurada not in stack.variantes:
            raise AndamioError(f"{ajustes.ARCHIVO}: los proyectos {stack.titulo} no tienen la variante '{configurada}'.")
        return configurada
    if stack.detectar_variante:
        return stack.detectar_variante(raiz)
    return next(iter(stack.variantes))


def nombre_variante(stack: Stack, variante: str) -> str:
    return stack.variantes.get(variante, "")


# --- Piezas -----------------------------------------------------------------


def contexto_pieza(sol: Solicitud) -> dict[str, str]:
    contexto = sol.nombre.marcadores()
    contexto.update(sol.stack.marcadores_variante.get(sol.variante, {}))
    if sol.pieza.contexto:
        contexto.update(sol.pieza.contexto(sol))
    return contexto


def archivos_de_la_pieza(sol: Solicitud, carpeta: Traversable) -> list[plantillas.ArchivoPlantilla]:
    """Los archivos de la plantilla que corresponden a esta solicitud (sin los que omite)."""
    omitidos = sol.pieza.omitir(sol) if sol.pieza.omitir else frozenset()
    return [a for a in plantillas.leer_arbol(carpeta) if a.ruta not in omitidos]


def inserciones_de_la_pieza(sol: Solicitud) -> list[Insercion]:
    """Las inserciones que corresponden a esta solicitud (las que no tienen condición o la cumplen)."""
    return [ins for ins in sol.pieza.inserciones if ins.condicion is None or ins.condicion(sol)]


def planificar_pieza(sol: Solicitud) -> Plan:
    stack, pieza = sol.stack, sol.pieza
    sol.contexto = contexto = contexto_pieza(sol)
    plan = Plan(sol.raiz)

    for ruta in pieza.existe_si:
        plan.exigir_inexistente(renderizar_ruta(tuple(ruta.split("/")), contexto, ruta))

    carpeta, _ = ubicar_plantilla(stack, pieza, sol.raiz, sol.variante)
    if not carpeta.is_dir():
        raise AndamioError(f"No encontré las plantillas de '{pieza.clave}' en {carpeta}.")
    # Nombres que chocan con lo que el código ya usa. Se informan al final: si además hay
    # archivos que ya existen, ese error es más claro (la pieza ya se generó).
    choques: list[AndamioError] = []
    centinela = _contexto_centinela(sol)
    # Los nombres se controlan en todos los archivos de la plantilla, también en los que esta
    # vez no se crean (ej.: el menú de una entidad --sin-menu, que se puede generar después).
    if centinela is not None:
        for archivo in plantillas.leer_arbol(carpeta):
            if archivo.texto is None or archivo.ruta in pieza.si_no_existe:
                continue
            origen = f"{stack.clave}/{pieza.clave}/{archivo.ruta}"
            forma = identificadores.conflicto(archivo.partes[-1], renderizar(archivo.texto, centinela, origen), sol.nombre)
            if forma:
                choques.append(_error_identificador(pieza, forma, str(renderizar_ruta(archivo.partes, contexto, origen))))
    for archivo in archivos_de_la_pieza(sol, carpeta):
        origen = f"{stack.clave}/{pieza.clave}/{archivo.ruta}"
        destino = renderizar_ruta(archivo.partes, contexto, origen)
        texto = archivo.texto
        contenido = renderizar(texto, contexto, origen, sol.guia) if texto is not None else archivo.contenido
        plan.crear(destino, contenido, si_no_existe=archivo.ruta in pieza.si_no_existe)

    conexiones = ajustes.de_proyecto(sol.raiz).conexiones
    for ins in inserciones_de_la_pieza(sol):
        origen = f"inserción en {ins.archivo}"
        if ins.marcador and ins.marcador in conexiones:
            # andamio.json indica que ese punto de conexión está en otro archivo.
            ruta = PurePosixPath(conexiones[ins.marcador])
        else:
            ruta = renderizar_ruta(tuple(ins.archivo.split("/")), contexto, origen)
        bloque = renderizar(ins.texto, contexto, origen, sol.guia)
        if centinela is not None:
            choque = _choque_insercion(pieza, sol, ruta, renderizar(ins.texto, centinela, origen), bloque)
            if choque:
                choques.append(choque)
        plan.insertar(
            ruta,
            bloque,
            marcador=ins.marcador,
            descripcion=renderizar(ins.descripcion, contexto, origen),
            comentario=ins.comentario,
            crear_si_falta=ins.crear_si_falta,
            ubicacion=renderizar(ins.ubicacion, contexto, origen),
        )
    # El historial (lo usa `andamio mapa`): una línea más, en el mismo plan que la pieza.
    plan.insertar(
        historial.ARCHIVO,
        historial.linea(pieza.clave, sol.nombre, sol.campos, sol.opciones, sol.variante),
        descripcion="lo generado, para andamio mapa",
        crear_si_falta=True,
    )
    plan.validar()
    if choques:
        raise choques[0]
    return plan


def _contexto_centinela(sol: Solicitud) -> dict[str, str] | None:
    """El contexto de la pieza con el nombre centinela (ver nucleo/identificadores.py)."""
    try:
        return contexto_pieza(dataclasses.replace(sol, nombre=identificadores.CENTINELA, contexto={}))
    except (AndamioError, OSError, LookupError, ValueError):
        # Algunas piezas leen archivos según el nombre (ej.: ui tarjetas): con el centinela no
        # existen. Esas piezas no generan código con el nombre, así que no hay nada que controlar.
        return None


def _choque_insercion(pieza: Pieza, sol: Solicitud, ruta: PurePosixPath, texto_centinela: str, bloque: str) -> AndamioError | None:
    """Lo que se inserta (ej.: `from .paginas.app import app`) no puede chocar con lo que el
    archivo del proyecto ya declara (ej.: `app = rx.App()`)."""
    try:
        actual = (sol.raiz / ruta).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None
    if ya_presente(actual, bloque):
        return None  # ya se había insertado: lo declaró andamio para este mismo nombre
    ocupados = identificadores.declarados(ruta.name, actual)
    chocan = sorted(identificadores.formas_usadas(texto_centinela, sol.nombre) & ocupados)
    return _error_identificador(pieza, chocan[0], str(ruta)) if chocan else None


def pasos_pieza(sol: Solicitud) -> list[str]:
    pasos = sol.pieza.siguiente_paso
    lista = pasos(sol) if callable(pasos) else pasos
    return [renderizar(p, sol.contexto) for p in lista]


# --- Proyectos --------------------------------------------------------------


def contexto_proyecto(stack: Stack, texto: str, variante: str = "") -> dict[str, str]:
    palabras = separar_palabras(texto, "El nombre del proyecto")
    validar_nombre_carpeta(kebab(palabras))
    contexto = {
        **stack.marcadores_variante.get(variante, {}),
        "carpeta": kebab(palabras),
        "proyecto": kebab(palabras),
        "proyecto_snake": snake(palabras),
        "Proyecto": pascal(palabras),
        "proyectoTitulo": titulo(palabras),
    }
    if stack.contexto_proyecto:
        contexto.update(stack.contexto_proyecto(Nombre.desde_palabras(palabras)))
    return contexto


AQUI = "."  # crear <tipo> . : el proyecto en la carpeta actual


def en_la_carpeta_actual(texto: str) -> bool:
    return texto.strip() in (".", "./", ".\\")


# Lo que puede haber en la carpeta actual antes de crear el proyecto ahí: lo de git y del editor.
_PERMITIDOS_AQUI = {".git", ".gitattributes", ".vscode", ".idea", ".DS_Store", "Thumbs.db", "LICENSE"}


def validar_carpeta_actual(padre: Path) -> None:
    sobran = sorted(p.name for p in padre.iterdir() if p.name not in _PERMITIDOS_AQUI)
    if sobran:
        lista = ", ".join(sobran[:5]) + (f" y {len(sobran) - 5} más" if len(sobran) > 5 else "")
        raise AndamioError(
            f"Para crear el proyecto acá (con '.') la carpeta tiene que estar vacía, y tiene: {lista}.",
            "Usá una carpeta vacía, o creá el proyecto en una carpeta nueva: escribí un nombre en lugar de '.'.",
        )


def planificar_proyecto(
    stack: Stack, texto: str, padre: Path, variante: str = "", guia: bool = True
) -> tuple[Plan, dict[str, str]]:
    aqui = en_la_carpeta_actual(texto)
    if aqui:
        # El nombre del proyecto es el de la carpeta actual (ej.: mi-tienda).
        validar_carpeta_actual(padre)
        texto = padre.resolve().name
    contexto = contexto_proyecto(stack, texto, variante)
    nombre_carpeta = contexto["carpeta"]
    plan = Plan(padre)
    if aqui:
        contexto["aqui"] = "1"
        base = PurePosixPath()
    else:
        destino = padre / nombre_carpeta
        if destino.exists() and (not destino.is_dir() or any(destino.iterdir())):
            raise AndamioError(
                f"Ya existe '{nombre_carpeta}' en {padre} y no está vacía.",
                "Elegí otro nombre para el proyecto, o creálo en otra carpeta (o creálo acá mismo con '.').",
            )
        plan.crear_carpeta(nombre_carpeta)
        base = PurePosixPath(nombre_carpeta)
    for archivo in archivos_proyecto(stack, variante):
        origen = f"{stack.clave}/{plantillas.CARPETA_PROYECTO}/{archivo.ruta}"
        destino_rel = base / renderizar_ruta(archivo.partes, contexto, origen)
        texto_plantilla = archivo.texto
        if texto_plantilla is None:
            plan.crear(destino_rel, archivo.contenido)
            continue
        plan.crear(destino_rel, renderizar(texto_plantilla, contexto, origen, guia))
        if archivo.ruta == ".env.example" and stack.contexto_env:
            plan.crear(base / ".env", renderizar(texto_plantilla, {**contexto, **stack.contexto_env()}, origen, guia))
    return plan, contexto


def pasos_proyecto(stack: Stack, contexto: dict[str, str]) -> list[str]:
    pasos = stack.siguiente_paso_proyecto
    if contexto.get("aqui"):
        pasos = [p for p in pasos if not p.startswith("cd ")]  # ya estás en la carpeta
    return [renderizar(p, contexto) for p in pasos]
