"""Estilos compartidos por los stacks web: el tema (variables CSS), las piezas de ui y estilo.

Las mismas tres piezas existen en web, django-web, vue, react y next:

- `nuevo tema <color> [--modo claro|oscuro|auto]`: variables de color, letra, espacios,
  bordes y sombras, más estilos base de botones, formularios y tablas. Todo lo que
  genera andamio (y lo que escribas con esas variables) cambia de look desde un archivo.
- `nuevo ui <parte>`: una parte de interfaz lista (tarjetas, alertas, modal...).
- `nuevo estilo <nombre>`: un archivo CSS propio (para tu componente o tu página) que ya
  usa las variables del tema y queda conectado.

El CSS vive acá (andamio/estilos/ui/*.css y las funciones de abajo) y cada stack lo pone
en su carpeta con una plantilla de un solo marcador (@@css@@).
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Callable

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks.base import Insercion, Pieza, Solicitud

# Color de acento: (modo claro, modo oscuro). Los claros tienen contraste con texto blanco;
# los oscuros, con texto negro.
PALETA = {
    "azul": ("#2563eb", "#60a5fa"),
    "verde": ("#15803d", "#4ade80"),
    "violeta": ("#7c3aed", "#a78bfa"),
    "naranja": ("#c2410c", "#fb923c"),
    "rojo": ("#b91c1c", "#f87171"),
    "turquesa": ("#0f766e", "#2dd4bf"),
    "rosa": ("#be185d", "#f472b6"),
    "ambar": ("#b45309", "#fbbf24"),
    "gris": ("#374151", "#9ca3af"),
}

PREGUNTA_COLOR = f"Color ({', '.join(PALETA)}; Enter para azul)"

MODOS = {"auto": "sigue al sistema (claro u oscuro)", "claro": "siempre claro", "oscuro": "siempre oscuro"}

PARTES = {
    "tarjetas": "grilla de tarjetas con imagen, título, texto y botones",
    "alertas": "mensajes de éxito, error, aviso e información",
    "modal": "ventana modal con <dialog> (sin librerías)",
    "navbar": "barra de navegación que en el celular se pliega (sin JavaScript)",
    "badges": "etiquetas chicas para estados o categorías",
    "tabs": "pestañas sin JavaScript",
    "paginacion": "números de página para listas largas",
    "cargando": "ruedita de carga y esqueletos animados",
    "responsive": "mejoras para el celular: tablas como tarjetas, formularios a todo el ancho",
    "accesible": "foco visible, texto para lectores de pantalla, menos movimiento",
}

_CLARO = {
    "fondo": "#f6f7f9",
    "superficie": "#ffffff",
    "texto": "#1b2430",
    "suave": "#5c6878",
    "borde": "#d9dee5",
    "peligro": "#b42318",
    "exito": "#15803d",
    "aviso": "#b45309",
    "acento-texto": "#ffffff",
    "sombra": "0 1px 3px rgb(16 24 40 / 8%)",
    "sombra-alta": "0 12px 32px rgb(16 24 40 / 16%)",
}
_OSCURO = {
    "fondo": "#0f141a",
    "superficie": "#1a2129",
    "texto": "#e6edf3",
    "suave": "#9aa6b2",
    "borde": "#2c3644",
    "peligro": "#f97066",
    "exito": "#4ade80",
    "aviso": "#fbbf24",
    "acento-texto": "#0f141a",
    "sombra": "0 1px 3px rgb(0 0 0 / 40%)",
    "sombra-alta": "0 12px 32px rgb(0 0 0 / 50%)",
}


def _variables(colores: dict[str, str], acento: str, oscuro: bool, sangria: str = "  ") -> str:
    lineas = [f"--acento: {acento};", *(f"--{k}: {v};" for k, v in colores.items())]
    lineas.append(f"color-scheme: {'dark' if oscuro else 'light'};")
    return "\n".join(sangria + l for l in lineas)


def css_tema(color: str, modo: str) -> str:
    claro, oscuro = PALETA[color]
    variables_claro = _variables(_CLARO, claro, False)
    variables_oscuro = _variables(_OSCURO, oscuro, True)
    principal = variables_oscuro if modo == "oscuro" else variables_claro
    automatico = (
        f"""
/* Modo oscuro automático: si el sistema de la persona está en oscuro. */
@media (prefers-color-scheme: dark) {{
  :root:root:not([data-tema="claro"]) {{
{_variables(_OSCURO, oscuro, True, "    ")}
  }}
}}
"""
        if modo == "auto"
        else ""
    )
    return f"""/* Tema del proyecto (lo generó: python -m andamio nuevo tema {color} --modo {modo}).

   Todo el diseño sale de estas variables: cambiá un valor y cambia en todas las páginas.
   Usalas en tu CSS:  color: var(--acento);  border-radius: var(--radio);
   Para cambiar de tema: borrá este archivo y volvé a generarlo con otro color o modo.
   Colores: {", ".join(PALETA)}.  Modos: {", ".join(MODOS)}.

   Para forzar un modo desde el código: document.documentElement.dataset.tema = 'oscuro' (o 'claro').
   (:root:root pesa más que :root, así estas variables ganan a las del CSS del proyecto.) */

:root:root {{
{principal}
  --radio: 10px;
  --espacio: 1rem;
  --fuente: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --fuente-mono: ui-monospace, "Cascadia Code", "SFMono-Regular", Consolas, monospace;
}}
{automatico}
:root:root[data-tema="claro"] {{
{variables_claro}
}}

:root:root[data-tema="oscuro"] {{
{variables_oscuro}
}}

/* --- Estilos base: usan las variables ---------------------------------------- */

body {{
  background: var(--fondo);
  color: var(--texto);
  font-family: var(--fuente);
  line-height: 1.55;
}}

a {{
  color: var(--acento);
}}

h1,
h2,
h3 {{
  line-height: 1.2;
  letter-spacing: -0.01em;
}}

code,
pre {{
  font-family: var(--fuente-mono);
}}

button,
.boton {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--acento);
  border-radius: var(--radio);
  background: var(--acento);
  color: var(--acento-texto);
  font: inherit;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: filter 0.15s;
}}

button:hover,
.boton:hover {{
  filter: brightness(1.08);
}}

button:disabled {{
  opacity: 0.6;
  cursor: not-allowed;
}}

.boton--borde {{
  background: transparent;
  color: var(--acento);
}}

.boton--peligro {{
  border-color: var(--peligro);
  background: var(--peligro);
  color: var(--acento-texto);
}}

input:not([type="checkbox"]):not([type="radio"]),
textarea,
select {{
  box-sizing: border-box;
  max-width: 100%;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--borde);
  border-radius: var(--radio);
  background: var(--superficie);
  color: var(--texto);
  font: inherit;
}}

input:focus,
textarea:focus,
select:focus {{
  border-color: var(--acento);
  outline: 2px solid color-mix(in srgb, var(--acento) 30%, transparent);
}}

input[type="checkbox"],
input[type="radio"] {{
  accent-color: var(--acento);
}}

table,
.tabla {{
  width: 100%;
  border-collapse: collapse;
  background: var(--superficie);
  border-radius: var(--radio);
  overflow: hidden;
}}

th,
td {{
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid var(--borde);
  text-align: left;
}}

th {{
  color: var(--suave);
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}}

.error {{
  color: var(--peligro);
}}

::selection {{
  background: color-mix(in srgb, var(--acento) 30%, transparent);
}}
"""


def css_ui(parte: str) -> str:
    return (resources.files("andamio.estilos") / "ui" / f"{parte}.css").read_text(encoding="utf-8")


def css_estilo(nombre: Nombre) -> str:
    clase = nombre.kebab
    return f"""/* Estilos de {nombre.forma('pascal')} (lo generó: python -m andamio nuevo estilo {nombre.kebab}).

   Usá la clase en tu componente o página:  <section class="{clase}"> ... </section>
   (En React y Next.js: className="{clase}"; en Vue, class="{clase}".)

   Las variables vienen del tema (python -m andamio nuevo tema): si cambiás el tema,
   esto cambia con él. Sin tema, se usan los valores después de la coma. */

.{clase} {{
  display: grid;
  gap: var(--espacio, 1rem);
  padding: var(--espacio, 1rem);
  background: var(--superficie, #fff);
  color: var(--texto, #1b2430);
  border: 1px solid var(--borde, #d9dee5);
  border-radius: var(--radio, 8px);
}}

.{clase}__titulo {{
  margin: 0;
  color: var(--acento, #0b7a75);
}}

.{clase}__texto {{
  margin: 0;
  color: var(--suave, #5c6878);
}}

/* En el celular. */
@media (max-width: 640px) {{
  .{clase} {{
    padding: calc(var(--espacio, 1rem) * 0.75);
  }}
}}
"""


# --- Piezas ---------------------------------------------------------------------------


def normalizar_modo(texto: str) -> str:
    modo = texto.strip().lower()
    if modo not in MODOS:
        raise AndamioError(f"El modo '{texto}' no existe.", "Modos: " + ", ".join(f"{m} ({d})" for m, d in MODOS.items()))
    return modo


def _validar_color(raiz: Path, nombre: Nombre) -> None:
    if nombre.snake not in PALETA:
        raise AndamioError(f"No tengo el color '{nombre.snake}'.", "Colores: " + ", ".join(PALETA))


def _validar_parte(raiz: Path, nombre: Nombre) -> None:
    if nombre.snake not in PARTES:
        lista = "\n".join(f"  {p.ljust(11)} {d}" for p, d in PARTES.items())
        raise AndamioError(
            f"No hay una parte de ui llamada '{nombre.snake}'.",
            f"Partes:\n{lista}\nPara un estilo propio: python -m andamio nuevo estilo <nombre>",
        )


def _validar_estilo(raiz: Path, nombre: Nombre) -> None:
    if nombre.kebab in ("tema", *PARTES):
        raise AndamioError(
            f"'{nombre.kebab}' ya es una pieza de estilos.",
            f"Usá: python -m andamio nuevo {'tema' if nombre.kebab == 'tema' else 'ui'} {nombre.kebab if nombre.kebab != 'tema' else ''}".rstrip(),
        )


InsercionCss = Callable[[str], Insercion]


def piezas_de_estilos(carpeta: str, conectar: InsercionCss, nota_uso: str, marcadores: dict[str, str] | None = None) -> dict[str, Pieza]:
    """Las piezas tema, ui y estilo de un stack.

    carpeta: dónde van los CSS ("css", "static/css", "src", "app").
    conectar: arma la Insercion que carga un CSS, a partir de su ruta relativa a la carpeta.
    nota_uso: cómo se usan las clases en ese stack (class o className).
    marcadores: marcadores propios del stack que usa `conectar` (ej.: @@extx@@ en React).
    """
    extra = marcadores or {}
    tema = Pieza(
        clave="tema",
        titulo="Tema",
        descripcion="colores, letra, bordes y modo oscuro de todo el proyecto (variables CSS)",
        ejemplo="violeta --modo auto",
        nombre_defecto="azul",
        pregunta_nombre=PREGUNTA_COLOR,
        formas=("color @@nombre@@",),
        validar_nombre=_validar_color,
        opciones=frozenset({"modo"}),
        normalizar_opcion={"modo": normalizar_modo},
        contexto=lambda sol: {"css": css_tema(sol.nombre.snake, sol.opciones.get("modo", "auto"))},
        marcadores={**extra, "css": "el CSS del tema (variables y estilos base), armado con el color y el modo"},
        existe_si=(f"{carpeta}/tema.css",),
        inserciones=(conectar("tema.css"),),
        siguiente_paso=[
            f"# Listo: todo el proyecto usa los colores del tema ({carpeta}/tema.css).",
            "# En tu CSS: color: var(--acento); background: var(--superficie); border-radius: var(--radio);",
            f"# Para cambiarlo: borrá {carpeta}/tema.css y generalo de nuevo (ej.: nuevo tema verde --modo oscuro).",
        ],
    )
    ui = Pieza(
        clave="ui",
        titulo="Parte de interfaz",
        descripcion="CSS listo para usar: " + ", ".join(PARTES),
        ejemplo="tarjetas",
        formas=("@@nombre@@",),
        validar_nombre=_validar_parte,
        contexto=lambda sol: {"css": css_ui(sol.nombre.snake)},
        marcadores={**extra, "css": "el CSS de la parte (andamio/estilos/ui/<parte>.css)"},
        existe_si=(f"{carpeta}/ui/@@nombreKebab@@.css",),
        inserciones=(conectar("ui/@@nombreKebab@@.css"),),
        siguiente_paso=[
            f"# El ejemplo de uso está al principio de {carpeta}/ui/@@nombreKebab@@.css. {nota_uso}",
            "# Con un tema (nuevo tema <color>), toma sus colores.",
        ],
    )
    estilo = Pieza(
        clave="estilo",
        titulo="Estilo propio",
        descripcion="un CSS para tu componente o página, con las variables del tema",
        ejemplo="catalogo",
        formas=(".@@nombreKebab@@",),
        validar_nombre=_validar_estilo,
        contexto=lambda sol: {"css": css_estilo(sol.nombre)},
        marcadores={**extra, "css": "el CSS con la clase .<nombre>, usando las variables del tema"},
        existe_si=(f"{carpeta}/estilos/@@nombreKebab@@.css",),
        inserciones=(conectar("estilos/@@nombreKebab@@.css"),),
        siguiente_paso=[
            f"# Editá {carpeta}/estilos/@@nombreKebab@@.css y usá la clase en tu componente o página:",
            f"# {nota_uso.replace('clase', 'clase .@@nombreKebab@@')}",
        ],
    )
    return {"tema": tema, "ui": ui, "estilo": estilo}


# --- Tema sin CSS: React Native y Reflex -----------------------------------------------

# Colores de acento de Radix (los que usa Reflex) para cada color de la paleta.
RADIX = {
    "azul": "blue",
    "verde": "green",
    "violeta": "violet",
    "naranja": "orange",
    "rojo": "red",
    "turquesa": "teal",
    "rosa": "pink",
    "ambar": "amber",
    "gris": "gray",
}


def _camel(clave: str) -> str:
    primera, *resto = clave.split("-")
    return primera + "".join(p.capitalize() for p in resto)


def contexto_tema_js(sol: Solicitud) -> dict[str, str]:
    """Los colores como objetos de JavaScript (React Native)."""
    claro, oscuro = PALETA[sol.nombre.snake]
    modo = sol.opciones.get("modo", "auto")

    def objeto(colores: dict[str, str], acento: str) -> str:
        pares = {"acento": acento, **{_camel(k): v for k, v in colores.items() if not k.startswith("sombra")}}
        return "\n".join(f"{k}: '{v}'," for k, v in pares.items())

    return {"colores_claro": objeto(_CLARO, claro), "colores_oscuro": objeto(_OSCURO, oscuro), "modo": modo}


def contexto_tema_reflex(sol: Solicitud) -> dict[str, str]:
    modo = sol.opciones.get("modo", "auto")
    return {
        "acento_radix": RADIX[sol.nombre.snake],
        "apariencia": {"auto": "inherit", "claro": "light", "oscuro": "dark"}[modo],
        "modo": modo,
    }


def pieza_tema(**cambios) -> Pieza:
    """La pieza tema con lo común (color, --modo, validación), para los stacks sin CSS."""
    base = dict(
        clave="tema",
        titulo="Tema",
        nombre_defecto="azul",
        pregunta_nombre=PREGUNTA_COLOR,
        ejemplo="violeta --modo auto",
        formas=("color @@nombre@@",),
        validar_nombre=_validar_color,
        opciones=frozenset({"modo"}),
        normalizar_opcion={"modo": normalizar_modo},
    )
    return Pieza(**{**base, **cambios})
