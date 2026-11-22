"""`andamio comandos`: el árbol de todos los comandos, sus opciones y las piezas de cada stack.

Se arma a partir del parser y de los stacks registrados, así nunca queda desactualizado.
"""

from __future__ import annotations

import argparse

from andamio import stacks
from andamio.acciones import ALIAS_PIEZAS
from andamio.nucleo import consola

# Opciones de `nuevo` que son de una pieza (Pieza.opciones) -> cómo se escriben.
_OPCIONES_PIEZA = {
    "migrar": "--migrar",
    "protegido": "--protegido",
    "carpeta": "--carpeta <carpeta>",
    "modo": "--modo auto|claro|oscuro",
    "datos": "--datos <servicio>",
    "uno": "--uno",
    "form": "--form",
    "sin_menu": "--sin-menu",
    "solo_lectura": "--solo-lectura",
    "solo": "--solo <funciones>",
}
_PIEZAS_EN_INGLES = {espanol: ingles for ingles, espanol in ALIAS_PIEZAS.items()}


def _subcomandos(parser: argparse.ArgumentParser) -> list[tuple[str, list[str], str, argparse.ArgumentParser]]:
    """(nombre, alias, ayuda, parser) de cada subcomando, en orden."""
    accion = next((a for a in parser._actions if isinstance(a, argparse._SubParsersAction)), None)
    if accion is None:
        return []
    resultado = []
    for elegido in accion._choices_actions:
        nombre = elegido.dest
        sub = accion._name_parser_map[nombre]
        alias = [n for n, p in accion._name_parser_map.items() if p is sub and n != nombre]
        resultado.append((nombre, alias, elegido.help or "", sub))
    return resultado


def _argumentos(parser: argparse.ArgumentParser) -> str:
    partes = []
    for accion in parser._actions:
        if accion.option_strings or isinstance(accion, argparse._SubParsersAction):
            continue
        nombre = f"<{accion.metavar or accion.dest}>"
        if accion.nargs == "?":
            nombre = f"[{nombre}]"
        elif accion.nargs == "*":
            nombre = f"[{nombre}...]"
        partes.append(nombre)
    return " ".join(partes)


def _opciones(parser: argparse.ArgumentParser) -> list[tuple[str, str]]:
    filas = []
    for accion in parser._actions:
        if not accion.option_strings or isinstance(accion, argparse._HelpAction):
            continue
        texto = ", ".join(accion.option_strings)
        if accion.nargs != 0 and not isinstance(accion, (argparse._StoreConstAction, argparse._StoreTrueAction)):
            texto += f" <{accion.dest}>"
        filas.append((texto, accion.help or ""))
    return filas


# El nombre de cada pieza en la forma general: qué se escribe en lugar del ejemplo.
_MARCADOR_NOMBRE = {"tema": "<color>", "ui": "<parte>", "menu": "<entidad>", "busqueda": "<entidad>", "accion": "<recurso>"}
# Piezas cuyos "campos" no definen datos: qué se escribe en su lugar.
_MARCADOR_CAMPOS = {"busqueda": "<campo>...", "accion": "<acción>..."}


def forma_general(clave: str, pieza) -> str:
    """nuevo crud <nombre> <campo:tipo>... : lo que se escribe, sin el ejemplo."""
    if pieza.nombre_defecto and clave != "tema":
        nombre = ""
    else:
        nombre = _MARCADOR_NOMBRE.get(clave, "<Nombre>" if pieza.ejemplo[:1].isupper() else "<nombre>")
        if pieza.nombre_defecto:
            nombre = f"[{nombre}]"
    campos = _MARCADOR_CAMPOS.get(clave, "<campo:tipo>...") if pieza.usa_campos else ""
    partes = ["nuevo", clave, nombre, campos]
    return " ".join(p for p in partes if p)


def _con_alias(nombre: str, alias: list[str]) -> str:
    return nombre + (f"  ({', '.join(alias)})" if alias else "")


def arbol(parser: argparse.ArgumentParser) -> str:
    p = consola.programa()
    lineas = [
        consola.color("Comandos", "negrita") + consola.color("  (entre paréntesis, el mismo comando en inglés)", "gris"),
        "",
        f"{p}",
        "    abre el menú: te pregunta todo, paso a paso",
        f"{p} --version",
        "",
    ]
    for nombre, alias, ayuda, sub in _subcomandos(parser):
        hijos = _subcomandos(sub)
        if hijos:
            for nombre_hijo, alias_hijo, ayuda_hijo, sub_hijo in hijos:
                ingles = [f"{a} {b}" for a in alias for b in alias_hijo]
                lineas.append(_con_alias(f"{p} {nombre} {nombre_hijo} {_argumentos(sub_hijo)}".rstrip(), ingles))
                lineas.append(f"    {ayuda_hijo}")
        else:
            lineas.append(_con_alias(f"{p} {nombre} {_argumentos(sub)}".rstrip(), alias))
            lineas.append(f"    {ayuda}")
            opciones = _opciones(sub)
            ancho = max((len(o) for o, _ in opciones), default=0)
            for opcion, texto in opciones:
                lineas.append(f"    {opcion.ljust(ancho)}  " + consola.color(texto, "gris"))
        lineas.append("")

    lineas += [consola.color("Tipos de proyecto y sus piezas", "negrita") + consola.color(f"  ({p} crear <tipo> / {p} nuevo <pieza>)", "gris"), ""]
    for stack in stacks.ORDEN_MENU:
        variantes = f"  [--{' / --'.join(stack.variantes)}]" if stack.variantes else ""
        lineas.append(consola.color(f"{stack.clave}", "negrita") + f"  {stack.titulo}{variantes}")
        filas = []
        for clave, pieza in stack.piezas.items():
            nombre = _con_alias(clave, [_PIEZAS_EN_INGLES[clave]] if clave in _PIEZAS_EN_INGLES else [])
            ejemplo = pieza.ejemplo or "(sin nombre)"
            opciones = " ".join(_OPCIONES_PIEZA[o] for o in sorted(pieza.opciones) if _OPCIONES_PIEZA[o].split()[0] not in ejemplo)
            filas.append((nombre, forma_general(clave, pieza), f"{ejemplo}  {opciones}".rstrip(), pieza.descripcion))
        ancho = max(len(f[0]) for f in filas)
        for nombre, forma, ejemplo, descripcion in filas:
            lineas.append(f"    {nombre.ljust(ancho)}  {descripcion}")
            lineas.append(f"    {' ' * ancho}  {forma}")
            lineas.append(f"    {' ' * ancho}  " + consola.color(f"ej.: nuevo {nombre.split()[0]} {ejemplo}", "gris"))
        lineas.append("")

    tipos = ", ".join(stacks.por_clave("django").tipos)
    lineas += [
        consola.color("Campos", "negrita"),
        "    Los nombres son tuyos: <Nombre> y <nombre> son cualquier nombre (en singular),",
        "    y los campos, los que necesites. Los ejemplos usan producto, pero sirve cualquiera.",
        "    nombre:tipo  (sin tipo es str). Tipos: " + tipos,
        "    En el tipo python (consola): str, int, float.",
        "",
        consola.color("Opciones de todas las piezas de nuevo", "negrita"),
        "    --simular (--dry-run)  muestra qué haría, sin tocar nada",
        "    --plural <plural>      el plural, si el automático no sirve (--plural paises)",
    ]
    return "\n".join(lineas)
