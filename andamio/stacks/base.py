"""Estructuras con las que se declara un stack y sus piezas.

Un stack es un módulo en `andamio/stacks/` que define una variable `STACK`.
Agregar una pieza = crear su carpeta en `andamio/plantillas/<stack>/<pieza>/` y
sumar una entrada `Pieza(...)` en el diccionario `piezas` del stack.
Ver docs/docente.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Union

from andamio.nucleo.campos import Campo
from andamio.nucleo.nombres import Nombre

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


@dataclass
class Solicitud:
    """Todo lo que se sabe de la pieza que se va a generar."""

    stack: Stack
    pieza: Pieza
    raiz: Path
    nombre: Nombre
    campos: list[Campo] = field(default_factory=list)
    opciones: dict[str, Any] = field(default_factory=dict)
    contexto: dict[str, str] = field(default_factory=dict)
    variante: str = ""  # ej.: "ts" o "js"; vacío si el stack no tiene variantes
    guia: bool = True  # con los comentarios de guía (False con --sin-guia)


# Lista de comandos (con marcadores) o función que la calcula según la solicitud.
# Un paso que empieza con "# " se muestra como nota; uno que empieza con http, como enlace.
Pasos = Union[list[str], Callable[[Solicitud], list[str]]]


@dataclass(frozen=True)
class Insercion:
    """Líneas que se agregan a un archivo que ya existe en el proyecto."""

    archivo: str  # ruta relativa, puede tener marcadores
    texto: str  # puede tener marcadores y varias líneas
    marcador: str | None = None  # clave del marcador (andamio:<clave>); None = al final del archivo
    descripcion: str = ""  # se muestra en el resumen: "registro en LOCAL_APPS"
    ubicacion: str = ""  # dónde pegarlo si falta el marcador: "dentro de LOCAL_APPS"
    comentario: str = "#"  # cómo empieza un comentario en ese archivo ("#" o "//")
    crear_si_falta: bool = False


@dataclass(frozen=True)
class Pieza:
    clave: str
    titulo: str
    descripcion: str
    ejemplo: str  # ejemplo de uso: "producto nombre:str precio:float"
    # Nombre que se usa si no se escribe ninguno (ej.: "cuenta" en el login de Django).
    # Con nombre por defecto, el menú no pregunta el nombre.
    nombre_defecto: str = ""
    # Si la pieza tiene nombre por defecto pero conviene elegirlo (ej.: el color del tema),
    # la pregunta que hace el menú. Vacío = el menú usa el nombre por defecto sin preguntar.
    pregunta_nombre: str = ""
    # Formas del nombre que se muestran en "Se usará: ...": "snake", "pascal", ... o un
    # texto con marcadores, como "use@@Nombre@@".
    formas: tuple[str, ...] = ("snake",)
    usa_campos: bool = False
    usa_plural: bool = False
    opciones: frozenset[str] = frozenset()  # opciones extra que acepta: "carpeta", "migrar"
    ajustar_palabras: Callable[[list[str]], list[str]] | None = None
    # Nombres de campo prohibidos para esta pieza (ej.: chocan con variables de la plantilla).
    campos_reservados: Callable[[Nombre], dict[str, str]] | None = None
    # Validación extra del nombre para esta pieza; lanza AndamioError si no sirve.
    validar_nombre: Callable[[Path, Nombre], None] | None = None
    # Normaliza el valor de una opción de texto ("carpeta"); lanza AndamioError si no sirve.
    normalizar_opcion: dict[str, Callable[[str], str]] = field(default_factory=dict)
    contexto: Callable[[Solicitud], dict[str, str]] | None = None
    marcadores: dict[str, str] = field(default_factory=dict)  # marcadores propios (para el LEEME)
    existe_si: tuple[str, ...] = ()  # si alguna de estas rutas existe, la pieza ya fue generada
    si_no_existe: frozenset[str] = frozenset()  # archivos de la plantilla que se crean solo si faltan
    inserciones: tuple[Insercion, ...] = ()
    # Orden recomendado para leer lo que se generó: (ruta con marcadores, qué hace).
    # Se muestra después de generar, para que el código no sea una caja negra.
    lectura: tuple[tuple[str, str], ...] = ()
    siguiente_paso: Pasos = field(default_factory=list)
    despues: Callable[[Solicitud], None] | None = None  # acción extra después de escribir
    # Opciones de sí/no que el menú pregunta después de escribir: {"migrar": "¿Ejecutar...?"}
    confirmaciones: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Stack:
    clave: str
    titulo: str
    senal: str  # qué archivos lo identifican, para explicar la detección
    detectar: Callable[[Path], bool]
    tipos: dict[str, str]  # tipo de campo -> descripción
    piezas: dict[str, Pieza]
    ejemplo_proyecto: str = "mi-proyecto"
    siguiente_paso_proyecto: list[str] = field(default_factory=list)
    contexto_proyecto: Callable[[Nombre], dict[str, str]] | None = None
    # Si está definido, el `.env` se genera a partir de `.env.example` con estos valores.
    contexto_env: Callable[[], dict[str, str]] | None = None
    # Validación extra del nombre según el proyecto (ej.: apps de Django que ya existen).
    # Recibe la raíz del proyecto y el nombre; lanza AndamioError si no sirve.
    validar_nombre: Callable[[Path, Nombre], None] | None = None
    # Variantes (ej.: {"ts": "TypeScript", "js": "JavaScript"}). La primera es la que se usa
    # por defecto. Con variantes, las plantillas van en plantillas/<stack>/<variante>/.
    variantes: dict[str, str] = field(default_factory=dict)
    # Cuál es la variante de un proyecto que ya existe (ej.: "ts" si hay tsconfig.json).
    detectar_variante: Callable[[Path], str] | None = None
    # Marcadores propios de cada variante: {"ts": {"ext": "ts", "extx": "tsx"}, "js": {...}}.
    marcadores_variante: dict[str, dict[str, str]] = field(default_factory=dict)
    # Clave de otro stack cuyas plantillas se reutilizan: el proyecto nuevo junta los
    # archivos de _proyecto de los dos (si se repiten, gana el de este stack), y las
    # piezas que este stack no tiene en su carpeta se toman de la del otro.
    # Ej.: next-fullstack extiende next (mismas páginas y componentes, más la API).
    extiende: str = ""
    # Solo para tests: carpeta de plantillas alternativa a la incorporada.
    plantillas: Traversable | None = None
