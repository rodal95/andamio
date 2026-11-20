"""Línea de comandos de andamio."""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path

from andamio import __version__, acciones, menu, stacks
from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError, Cancelado

# argparse genera sus mensajes en inglés llamando a la función `_` de su módulo.
# La reemplazamos por una traducción; lo que no esté en la tabla queda como está.
_TRADUCCIONES = {
    "usage: ": "uso: ",
    "positional arguments": "argumentos",
    "options": "opciones",
    "optional arguments": "opciones",
    "show this help message and exit": "muestra esta ayuda y termina",
    "show program's version number and exit": "muestra la versión y termina",
    "the following arguments are required: %s": "falta indicar: %s",
    "unrecognized arguments: %s": "no reconozco estos datos: %s",
    "invalid choice: %(value)r (choose from %(choices)s)": "opción inválida: %(value)r (opciones: %(choices)s)",
    "expected one argument": "falta el valor",
    "argument %(argument_name)s: %(message)s": "%(argument_name)s: %(message)s",
    "ambiguous option: %(option)s could match %(matches)s": "opción ambigua: %(option)s puede ser %(matches)s",
}
_traducir_original = argparse._  # type: ignore[attr-defined]
argparse._ = lambda texto: _TRADUCCIONES.get(texto, _traducir_original(texto))  # type: ignore[attr-defined]


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        consola.error(message, f"Para ver la ayuda escribí: {self.prog} --help")
        raise SystemExit(2)


def _ejemplos() -> str:
    p = consola.programa()
    filas = [
        (p, "menú interactivo"),
        (f"{p} crear django mi-api", "crea un proyecto"),
        (f"{p} crear react mi-web --js", "crea un proyecto React en JavaScript"),
        (f"{p} nuevo recurso producto nombre:str", "genera un recurso con un campo"),
        (f"{p} info", "qué se puede generar acá"),
        (f"{p} init", "prepara un proyecto que ya existe (crea andamio.json)"),
        (f"{p} pendientes", "dónde falta escribir tu lógica (marcas TODO(logica))"),
        (f"{p} comandos", "todos los comandos, opciones y piezas"),
        (f"{p} new resource producto nombre:str", "lo mismo que 'nuevo recurso', en inglés"),
        (f"{p} plantillas exportar", "copia las plantillas para modificarlas"),
        (f"{p} configurar", "hace que funcione escribiendo solo: andamio"),
    ]
    ancho = max(len(c) for c, _ in filas) + 3
    return "ejemplos:\n" + "\n".join(f"  {c.ljust(ancho)}{d}" for c, d in filas) + "\n"


# Alias en inglés de cada comando: "create" es lo mismo que "crear". Los mensajes siguen
# en español; los alias son para quien está acostumbrado a escribir los comandos en inglés.
ALIAS_COMANDOS = {
    "crear": ["create"],
    "nuevo": ["new", "generate", "g"],
    "info": [],
    "init": [],
    "pendientes": ["todo", "pending"],
    "comandos": ["commands"],
    "plantillas": ["templates"],
    "configurar": ["configure", "setup"],
}
ALIAS_ACCIONES = {"exportar": ["export"]}
_A_ESPANOL = {alias: clave for clave, alias in {**ALIAS_COMANDOS, **ALIAS_ACCIONES}.items() for alias in alias}


def construir_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog=consola.programa(),
        description="Genera la estructura de código de tus proyectos. Sin argumentos abre el menú.",
        epilog=_ejemplos(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"andamio {__version__}")
    sub = parser.add_subparsers(dest="comando", metavar="comando", parser_class=_Parser)

    def comando(nombre: str, **kwargs) -> argparse.ArgumentParser:
        return sub.add_parser(nombre, aliases=ALIAS_COMANDOS[nombre], **kwargs)

    claves = ", ".join(s.clave for s in stacks.ORDEN_MENU)
    simular = {"action": "store_true", "dest": "simular", "help": "muestra qué se crearía, sin tocar nada"}
    sin_guia = {
        "action": "store_false",
        "dest": "guia",
        "default": None,  # sin la opción: lo que diga andamio.json (o con guía)
        "help": "sin los comentarios que explican el código (las marcas TODO(logica) quedan)",
    }

    crear = comando("crear", help="crea un proyecto nuevo", description="Crea un proyecto nuevo en una carpeta.")
    crear.add_argument("stack", metavar="tipo", help=f"tipo de proyecto: {claves}")
    crear.add_argument("nombre", help="nombre del proyecto (ej: mi-tienda)")
    crear.add_argument("--simular", "--dry-run", **simular)
    crear.add_argument("--sin-guia", "--no-guide", **sin_guia)
    crear.add_argument("--variante", "--variant", dest="variante", help="variante del proyecto: ts o js (Express, React, React Native, Next.js)")
    crear.add_argument("--js", dest="variante", action="store_const", const="js", help="atajo de --variante js (JavaScript)")
    crear.add_argument("--ts", dest="variante", action="store_const", const="ts", help="atajo de --variante ts (TypeScript)")

    nuevo = comando(
        "nuevo",
        help="genera una pieza en el proyecto actual",
        description="Genera una pieza (recurso, componente, etc.) en el proyecto actual.",
        epilog=f"Los campos se escriben nombre:tipo (ej: precio:decimal). Usá '{consola.programa()} comandos' para ver todas las piezas.",
    )
    nuevo.add_argument("pieza", help="qué generar: recurso, crud, pagina... (en inglés: resource, page...; ver: comandos)")
    nuevo.add_argument("nombre", nargs="?", help="nombre en singular (ej: producto); algunas piezas, como login, no lo necesitan")
    nuevo.add_argument("campos", nargs="*", help="campos con la forma nombre:tipo")
    nuevo.add_argument("--plural", help="plural del nombre, si el automático no es correcto")
    nuevo.add_argument("--carpeta", "--folder", dest="carpeta", help="subcarpeta de app/ (pantallas de React Native)")
    nuevo.add_argument("--migrar", "--migrate", dest="migrar", action="store_true", help="crea y aplica la migración (Django, Express, Next.js full stack, Reflex)")
    nuevo.add_argument("--protegido", "--protected", dest="protegido", action="store_true", help="solo usuarios con login pueden crear, modificar y eliminar (Django)")
    nuevo.add_argument("--modo", "--mode", dest="modo", help="modo del tema: auto (sigue al sistema), claro u oscuro")
    nuevo.add_argument("--simular", "--dry-run", **simular)
    nuevo.add_argument("--sin-guia", "--no-guide", **sin_guia)

    comando("info", help="muestra el tipo de proyecto detectado y qué se puede generar")
    init = comando(
        "init",
        help="prepara un proyecto que ya existe: revisa sus puntos de conexión y crea andamio.json",
        description="Prepara un proyecto que ya existe (aunque no lo haya creado andamio): detecta el tipo, "
        "revisa los puntos de conexión (los marcadores andamio:...) y crea andamio.json. No modifica tu código.",
    )
    init.add_argument("tipo", nargs="?", help=f"tipo de proyecto, si no se detecta solo: {claves}")
    init.add_argument("--variante", "--variant", dest="variante", help="ts o js")
    init.add_argument("--js", dest="variante", action="store_const", const="js", help="atajo de --variante js")
    init.add_argument("--ts", dest="variante", action="store_const", const="ts", help="atajo de --variante ts")
    init.add_argument("--simular", "--dry-run", **simular)
    comando("pendientes", help="lista las marcas TODO(logica): dónde falta escribir tu lógica")
    comando("comandos", help="muestra todos los comandos, sus opciones y las piezas de cada tecnología")

    plantillas = comando("plantillas", help="exporta las plantillas para modificarlas")
    plantillas_sub = plantillas.add_subparsers(dest="accion", metavar="accion", parser_class=_Parser)
    exportar = plantillas_sub.add_parser("exportar", aliases=ALIAS_ACCIONES["exportar"], help="copia las plantillas a .andamio/plantillas/")
    exportar.add_argument("pieza", nargs="?", help="solo esta pieza (por defecto, todas)")

    configurar = comando(
        "configurar",
        help="hace que funcione escribiendo solo: andamio",
        description="Agrega la carpeta de andamio al PATH de tu usuario (sin permisos de administrador), "
        "para poder escribir 'andamio' en lugar de 'python -m andamio'. Es opcional.",
    )
    configurar.add_argument("--simular", "--dry-run", action="store_true", dest="simular", help="muestra qué cambiaría, sin tocar nada")
    return parser


def _ejecutar(args: argparse.Namespace, cwd: Path) -> int:
    # Los alias en inglés ("create", "new"...) hacen lo mismo que el comando en español.
    args.comando = _A_ESPANOL.get(args.comando, args.comando)
    if getattr(args, "accion", None):
        args.accion = _A_ESPANOL.get(args.accion, args.accion)
    if args.comando is None:
        return menu.ejecutar(cwd)
    if args.comando == "crear":
        stack = acciones.stack_por_clave(args.stack)
        return acciones.crear_proyecto(stack, args.nombre, cwd, simular=args.simular, variante=args.variante, guia=args.guia is not False)
    if args.comando == "nuevo":
        opciones = {"carpeta": args.carpeta, "migrar": args.migrar, "protegido": args.protegido, "modo": args.modo}
        return acciones.nuevo(cwd, args.pieza, args.nombre, args.campos, args.plural, opciones, args.simular, args.guia)
    if args.comando == "info":
        return acciones.info(cwd)
    if args.comando == "init":
        from andamio import inspeccion

        return inspeccion.init(cwd, args.tipo, args.variante, args.simular)
    if args.comando == "pendientes":
        from andamio import inspeccion

        return inspeccion.pendientes(cwd)
    if args.comando == "comandos":
        from andamio import comandos

        consola.escribir(comandos.arbol(construir_parser()))
        return 0
    if args.comando == "configurar":
        from andamio import configurar

        return configurar.configurar(simular=args.simular)
    if args.comando == "plantillas":
        if args.accion != "exportar":
            raise AndamioError(
                "Indicá qué hacer con las plantillas.",
                f"Para copiarlas a tu proyecto y modificarlas: {consola.programa()} plantillas exportar",
            )
        from andamio import exportar

        return exportar.exportar(cwd, args.pieza)
    raise AssertionError(args.comando)


def main(argv: list[str] | None = None) -> int:
    consola.configurar_salida()
    try:
        args = construir_parser().parse_args(argv)
    except SystemExit as e:
        return int(e.code or 0)
    try:
        return _ejecutar(args, Path.cwd())
    except AndamioError as e:
        consola.error(e.mensaje, e.sugerencia)
        return 1
    except BrokenPipeError:
        # La salida se cerró antes de tiempo (ej.: andamio info | more). No es un error de andamio.
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass
        return 1
    except (Cancelado, KeyboardInterrupt) as e:
        detalle = f" {e}" if isinstance(e, Cancelado) and str(e) else ""
        print(f"\nCancelado.{detalle}")
        return 130
    except Exception:
        consola.error(
            "Ocurrió un error inesperado. No es culpa tuya: es un error de andamio.",
            "Sacale una captura a este mensaje completo y mandásela a tu docente.",
        )
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
