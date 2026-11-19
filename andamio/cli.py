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


EJEMPLOS = """ejemplos:
  andamio                                   menú interactivo
  andamio crear django mi-api               crea un proyecto
  andamio crear react mi-web --js           crea un proyecto React en JavaScript
  andamio nuevo recurso producto nombre:str precio:decimal
  andamio info                              qué se puede generar acá
  andamio plantillas exportar               copia las plantillas para modificarlas
"""


def construir_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="andamio",
        description="Genera la estructura de código de tus proyectos. Sin argumentos abre el menú.",
        epilog=EJEMPLOS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"andamio {__version__}")
    sub = parser.add_subparsers(dest="comando", metavar="comando", parser_class=_Parser)

    claves = ", ".join(s.clave for s in stacks.ORDEN_MENU)
    crear = sub.add_parser("crear", help="crea un proyecto nuevo", description="Crea un proyecto nuevo en una carpeta.")
    crear.add_argument("stack", metavar="tipo", help=f"tipo de proyecto: {claves}")
    crear.add_argument("nombre", help="nombre del proyecto (ej: mi-tienda)")
    crear.add_argument("--simular", action="store_true", help="muestra qué se crearía, sin tocar nada")
    crear.add_argument("--variante", help="variante del proyecto (ej.: ts o js en React y React Native)")
    crear.add_argument("--js", dest="variante", action="store_const", const="js", help="atajo de --variante js (JavaScript)")
    crear.add_argument("--ts", dest="variante", action="store_const", const="ts", help="atajo de --variante ts (TypeScript)")

    nuevo = sub.add_parser(
        "nuevo",
        help="genera una pieza en el proyecto actual",
        description="Genera una pieza (recurso, componente, etc.) en el proyecto actual.",
        epilog="Los campos se escriben nombre:tipo (ej: precio:decimal). Usá 'andamio info' para ver piezas y tipos.",
    )
    nuevo.add_argument("pieza", help="qué generar (ver 'andamio info')")
    nuevo.add_argument("nombre", help="nombre en singular (ej: producto)")
    nuevo.add_argument("campos", nargs="*", help="campos con la forma nombre:tipo")
    nuevo.add_argument("--plural", help="plural del nombre, si el automático no es correcto")
    nuevo.add_argument("--carpeta", help="subcarpeta (pantallas de React Native)")
    nuevo.add_argument("--migrar", action="store_true", help="ejecuta makemigrations y migrate (Django)")
    nuevo.add_argument("--simular", action="store_true", help="muestra qué se crearía, sin tocar nada")

    sub.add_parser("info", help="muestra el tipo de proyecto detectado y qué se puede generar")

    plantillas = sub.add_parser("plantillas", help="exporta las plantillas para modificarlas")
    plantillas_sub = plantillas.add_subparsers(dest="accion", metavar="accion", parser_class=_Parser)
    exportar = plantillas_sub.add_parser("exportar", help="copia las plantillas a .andamio/plantillas/")
    exportar.add_argument("pieza", nargs="?", help="solo esta pieza (por defecto, todas)")
    return parser


def _ejecutar(args: argparse.Namespace, cwd: Path) -> int:
    if args.comando is None:
        return menu.ejecutar(cwd)
    if args.comando == "crear":
        stack = acciones.stack_por_clave(args.stack)
        return acciones.crear_proyecto(stack, args.nombre, cwd, simular=args.simular, variante=args.variante)
    if args.comando == "nuevo":
        opciones = {"carpeta": args.carpeta, "migrar": args.migrar}
        return acciones.nuevo(cwd, args.pieza, args.nombre, args.campos, args.plural, opciones, args.simular)
    if args.comando == "info":
        return acciones.info(cwd)
    if args.comando == "plantillas":
        if args.accion != "exportar":
            raise AndamioError(
                "Indicá qué hacer con las plantillas.",
                "Para copiarlas a tu proyecto y modificarlas: andamio plantillas exportar",
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
