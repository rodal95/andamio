"""`andamio plantillas exportar`: copia las plantillas al proyecto para modificarlas.

Las copias van a `.andamio/plantillas/<stack>/<pieza>/`. Desde ese momento,
`andamio nuevo <pieza>` usa esa versión en lugar de la incorporada. Nunca se
sobrescribe un archivo: si ya existe, se deja como está.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from andamio import acciones
from andamio.nucleo import consola, plantillas
from andamio.nucleo.campos import parsear_campo
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.generador import carpeta_pieza, contexto_pieza, nombre_para_pieza, variante_del_proyecto
from andamio.nucleo.motor import renderizar
from andamio.nucleo.nombres import MARCADORES_NOMBRE
from andamio.nucleo.plan import Plan
from andamio.stacks.base import Pieza, Solicitud, Stack


def _ejemplo(stack: Stack, pieza: Pieza, raiz: Path) -> tuple[str, dict[str, str]]:
    """Calcula los marcadores con el ejemplo de la pieza, para mostrar valores reales."""
    nombre_texto, *campos_texto = pieza.ejemplo.split() or [pieza.nombre_defecto]
    nombre = nombre_para_pieza(pieza, nombre_texto)
    campos = [parsear_campo(c, stack.tipos) for c in campos_texto]
    variante = variante_del_proyecto(stack, raiz)
    contexto = contexto_pieza(Solicitud(stack, pieza, raiz, nombre, campos, variante=variante))
    return f"{consola.programa()} nuevo {pieza.clave} {pieza.ejemplo}".rstrip(), contexto


def _formatear_valor(valor: str) -> str:
    if valor == "":
        return "  Ejemplo: (vacío)"
    if "\n" not in valor:
        return f"  Ejemplo: `{valor}`"
    lineas = "\n".join(f"  {linea}" for linea in valor.split("\n"))
    return f"  Ejemplo:\n\n  ```\n{lineas}\n  ```"


def generar_leeme(stack: Stack, pieza: Pieza, raiz: Path) -> str:
    comando, contexto = _ejemplo(stack, pieza, raiz)
    descripciones = {**MARCADORES_NOMBRE, **pieza.marcadores}
    marcadores = "\n".join(
        f"- `@@{clave}@@`: {descripcion}\n{_formatear_valor(contexto.get(clave, ''))}\n"
        for clave, descripcion in descripciones.items()
    )
    modificaciones = "\n".join(
        f"- `{renderizar(ins.archivo, contexto)}`: {renderizar(ins.descripcion, contexto) or 'se agregan líneas'}"
        for ins in pieza.inserciones
    )
    extra = (
        f"\n## Además, andamio modifica\n\nEstos cambios no salen de esta carpeta:\n\n{modificaciones}\n"
        if modificaciones
        else ""
    )
    return f"""# Plantillas de `{pieza.clave}` ({stack.titulo})

Estos archivos son los que usa `{consola.programa()} nuevo {pieza.clave}` en este proyecto.
Si los modificás, andamio usa tu versión en lugar de la que trae incorporada.
Para volver a la original, borrá esta carpeta.

## Cómo funcionan

- Cada archivo se crea en el proyecto con la misma ruta que tiene acá adentro
  (este LEEME.md no se copia).
- Cada `@@marcador@@` se reemplaza por un valor. Los nombres de archivo también
  pueden llevar marcadores.
- Si un marcador ocupa una línea él solo, cada línea del valor toma la sangría
  de esa línea. Si el valor está vacío, la línea se elimina.
- Si escribís mal un marcador, andamio avisa y no genera nada.
- Si borrás un archivo de esta carpeta, ese archivo deja de generarse.

## Marcadores disponibles

Los ejemplos corresponden a:

```
{comando}
```

{marcadores}
{extra}"""


def exportar(cwd: Path, clave_pieza: str | None = None) -> int:
    stack, raiz = acciones.proyecto_actual(cwd)
    piezas = [acciones.pieza_por_clave(stack, clave_pieza)] if clave_pieza else list(stack.piezas.values())
    plan = Plan(raiz)
    base = PurePosixPath(*plantillas.CARPETA_USUARIO.parts) / stack.clave
    for pieza in piezas:
        origen = carpeta_pieza(stack, pieza, variante_del_proyecto(stack, raiz))
        if not origen.is_dir():
            raise AndamioError(f"No encontré las plantillas incorporadas de '{pieza.clave}'.")
        destino = base / pieza.clave
        for archivo in plantillas.leer_arbol(origen):
            plan.crear(destino / PurePosixPath(*archivo.partes), archivo.contenido, si_no_existe=True)
        plan.crear(destino / plantillas.LEEME, generar_leeme(stack, pieza, raiz), si_no_existe=True)

    if not plan.nuevos:
        consola.aviso(f"Las plantillas ya estaban exportadas en {base}. No se modificó nada.")
        return 0
    plan.aplicar()
    consola.exito("Listo.")
    plan.mostrar("Archivos creados")
    consola.escribir()
    consola.escribir(f"Modificá los archivos de {base}/: andamio va a usar tu versión.")
    consola.escribir("Cada carpeta tiene un LEEME.md con los marcadores @@...@@ que podés usar.")
    return 0
