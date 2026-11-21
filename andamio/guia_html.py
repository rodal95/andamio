"""andamio-guia.html: una página dentro del proyecto para guiarse mientras se trabaja.

Muestra qué tipo de proyecto es, cómo ponerlo en marcha, qué piezas se generaron (y si
siguen conectadas), dónde va la lógica propia (TODO(logica)), qué más se puede generar
(con su comando y dónde quedan los archivos) y en qué archivos se conecta cada cosa.

Se crea con `crear` y se actualiza sola después de cada `nuevo` (y con `init`). Es local:
va en .gitignore, así no se sube al repositorio. Se abre con doble clic.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING

from andamio import __version__

if TYPE_CHECKING:
    from andamio.stacks.base import Stack

ARCHIVO = "andamio-guia.html"
LINEA_GITIGNORE = f"\n# La página de andamio para guiarte (se actualiza sola; no hace falta subirla)\n{ARCHIVO}\n"
URL_GUIAS = "https://rodal95.github.io/andamio"

# Qué hace cada opción de `nuevo` (las que tiene cada pieza).
_OPCIONES = {
    "migrar": ("--migrar", "además crea y aplica la migración (la tabla en la base)"),
    "protegido": ("--protegido", "crear, modificar y eliminar piden login (generá antes: nuevo login)"),
    "solo_lectura": ("--solo-lectura", "la API solo lista y muestra; los datos se cargan desde /admin/"),
    "carpeta": ("--carpeta <carpeta>", "dentro de una carpeta de app/ (es parte de la ruta)"),
    "modo": ("--modo auto|claro|oscuro", "el modo del tema"),
    "datos": ("--datos <servicio>", "usa un servicio que ya existe: muestra su lista"),
    "uno": ("--datos <servicio> --uno", "muestra uno solo, con el id en la ruta"),
    "form": ("--datos <servicio> --form", "el formulario para crear y editar"),
    "sin_menu": ("--sin-menu", "solo la tabla y las funciones, sin el menú de consola"),
}


def _e(texto: object) -> str:
    return escape(str(texto), quote=True)


def _codigo(comando: str) -> str:
    return f'<div class="cmd"><code>{_e(comando)}</code><button type="button" data-copiar="{_e(comando)}">Copiar</button></div>'


def _enlace(raiz: Path, ruta: str) -> str:
    existe = (raiz / ruta).exists()
    return f'<a href="{_e(ruta)}">{_e(ruta)}</a>' if existe else f'<span class="falta">{_e(ruta)}</span>'


def _seccion(id_: str, titulo: str, cuerpo: str, bajada: str = "") -> str:
    return f'<section id="{id_}"><h2>{_e(titulo)}</h2>{f"<p class=bajada>{bajada}</p>" if bajada else ""}{cuerpo}</section>'


def _pasos(stack: Stack, raiz: Path, variante: str) -> str:
    from andamio.nucleo.generador import contexto_proyecto, pasos_proyecto

    try:
        contexto = {**contexto_proyecto(stack, raiz.name, variante), "aqui": "1"}
        pasos = pasos_proyecto(stack, contexto)
    except Exception:  # un nombre de carpeta raro no impide la página
        pasos = [p for p in stack.siguiente_paso_proyecto if not p.startswith("cd ")]
    items = []
    for paso in pasos:
        if paso.startswith("# "):
            items.append(f"<li><p>{_e(paso[2:])}</p></li>")
        elif paso.startswith("http"):
            items.append(f'<li><p>Abrí en el navegador: <a href="{_e(paso)}">{_e(paso)}</a></p></li>')
        else:
            items.append(f"<li>{_codigo(paso)}</li>")
    return f'<ol class="pasos">{"".join(items)}</ol>'


def _generado(stack: Stack, raiz: Path, programa: str) -> str:
    from andamio import inspeccion
    from andamio.nucleo import historial

    entradas, _ = historial.leer(raiz)
    if not entradas:
        return f'<p class="vacio">Todavía no generaste piezas. Empezá por alguna de <a href="#piezas">las de abajo</a>: {_e(programa)} nuevo &lt;pieza&gt; &lt;nombre&gt;.</p>'
    filas = []
    for entrada in reversed(entradas):
        estado = inspeccion.revisar_entrada(stack, raiz, entrada)
        archivos = "".join(f"<li>{_enlace(raiz, r)}</li>" for r, _ in estado.archivos if not r.startswith(".andamio/"))
        conexiones = "".join(
            f'<li class="{"ok" if esta else "mal"}">{_e(que)} en {_enlace(raiz, r)}{"" if esta else " — falta: andamio mapa te dice qué pegar"}</li>'
            for r, que, esta in estado.conexiones
            if not r.startswith(".andamio/")
        )
        marca = '<span class="ok">✓ completa</span>' if estado.completa else f'<span class="mal">{_e(estado.error or "le falta algo")}</span>'
        fecha = entrada.fecha.replace("T", " ")[:16]
        filas.append(
            f"""<details><summary><code>{_e(programa)} nuevo {_e(entrada.resumen())}</code> {marca} <small>{_e(fecha)}</small></summary>
            <div class="det">{f"<h4>Archivos</h4><ul>{archivos}</ul>" if archivos else ""}{f"<h4>Conectada en</h4><ul>{conexiones}</ul>" if conexiones else ""}</div></details>"""
        )
    return "".join(filas)


def _logica(raiz: Path) -> str:
    from andamio import inspeccion

    marcas = inspeccion.buscar_pendientes(raiz)
    if not marcas:
        return '<p class="vacio">No quedan marcas TODO(logica): no hay lógica propia pendiente.</p>'
    filas = "".join(f"<tr><td>{_enlace(raiz, m.archivo)}<small>:{m.linea}</small></td><td>{_e(m.texto)}</td></tr>" for m in marcas)
    return f'<table><thead><tr><th>Dónde</th><th>Qué falta</th></tr></thead><tbody>{filas}</tbody></table>'


def _piezas(stack: Stack, raiz: Path, variante: str, programa: str) -> str:
    from andamio.comandos import forma_general
    from andamio.inspeccion import _contexto_de_ejemplo
    from andamio.nucleo.lectura import orden_de_lectura

    tarjetas = []
    for clave, pieza in stack.piezas.items():
        contexto = _contexto_de_ejemplo(stack, pieza, raiz, variante)
        try:
            lectura = orden_de_lectura(pieza.lectura, contexto) if pieza.lectura else []
        except Exception:
            lectura = []
        donde = "".join(f"<li><code>{_e(r)}</code> <span>{_e(rol)}</span></li>" for r, rol in lectura)
        opciones = "".join(
            f"<li><code>{_e(_OPCIONES[o][0])}</code> {_e(_OPCIONES[o][1])}</li>" for o in sorted(pieza.opciones) if o in _OPCIONES
        )
        antes = "".join(f"<li>{_codigo(f'{programa} nuevo {p}')}</li>" for p in pieza.preparar)
        tarjetas.append(
            f"""<article class="pieza" data-buscar="{_e((clave + ' ' + pieza.titulo + ' ' + pieza.descripcion).lower())}">
            <h3>{_e(pieza.titulo)} <small>{_e(clave)}</small></h3><p>{_e(pieza.descripcion[:1].upper() + pieza.descripcion[1:])}.</p>
            <p class="rotulo">La forma general</p><div class="forma"><code>{_e(programa)} {_e(forma_general(clave, pieza))}</code></div>
            <p class="rotulo">Un ejemplo</p>{_codigo(f"{programa} nuevo {clave} {pieza.ejemplo}".rstrip())}
            {f'<p class="rotulo">Necesita antes (ejemplo)</p><ul class="lista">{antes}</ul>' if antes else ""}
            {f'<p class="rotulo">Opciones</p><ul class="lista">{opciones}</ul>' if opciones else ""}
            {f'<p class="rotulo">Qué crea y dónde (con el ejemplo)</p><ul class="donde">{donde}</ul>' if donde else ""}
            </article>"""
        )
    buscador = '<input type="search" placeholder="Buscar una pieza: página, servicio, crud..." data-filtro aria-label="Buscar una pieza">'
    return buscador + f'<div class="piezas">{"".join(tarjetas)}</div>'


def _conexiones(stack: Stack, raiz: Path, variante: str) -> str:
    from andamio import inspeccion

    puntos = inspeccion.puntos_de_conexion(stack, raiz, variante)
    if not puntos:
        return '<p class="vacio">Este tipo de proyecto no tiene puntos de conexión: cada pieza queda en sus propios archivos.</p>'
    filas = "".join(
        f"""<tr><td>{_enlace(raiz, p.archivo)}</td><td><code>{_e(p.linea)}</code><br><small>{_e(p.ubicacion)}</small></td>
        <td>{_e(", ".join(p.piezas))}</td><td class="{"ok" if p.estado == "ok" else "mal"}">{"✓" if p.estado == "ok" else _e(p.estado)}</td></tr>"""
        for p in puntos
    )
    return f'<table><thead><tr><th>Archivo</th><th>Línea que no hay que borrar</th><th>Lo usan</th><th></th></tr></thead><tbody>{filas}</tbody></table>'


def _tipos(stack: Stack) -> str:
    if not any(p.usa_campos for p in stack.piezas.values()):
        return ""
    filas = "".join(f"<tr><td><code>{_e(t)}</code></td><td>{_e(d)}</td></tr>" for t, d in stack.tipos.items())
    return _seccion(
        "tipos",
        "Tipos de campo",
        f"<table><thead><tr><th>Tipo</th><th>Qué guarda</th></tr></thead><tbody>{filas}</tbody></table>",
        "Los campos se escriben <code>nombre:tipo</code>; sin tipo, es <code>str</code>.",
    )


def _otros(programa: str) -> str:
    comandos = [
        (programa, "el menú: te pregunta todo, paso a paso"),
        (f"{programa} info", "qué proyecto es y qué piezas acepta"),
        (f"{programa} mapa", "lo que generaste y si sigue conectado (y qué pegar si falta algo)"),
        (f"{programa} pendientes", "dónde falta tu lógica (las marcas TODO(logica))"),
        (f"{programa} comandos", "todos los comandos y sus opciones"),
        (f"{programa} nuevo <pieza> <nombre> --simular", "muestra qué crearía, sin tocar nada"),
        (f"{programa} plantillas exportar", "copia las plantillas al proyecto para cambiar el código que se genera"),
    ]
    return "".join(f"<li>{_codigo(c)}<p>{_e(d)}</p></li>" for c, d in comandos)


def contenido(stack: Stack, raiz: Path, variante: str = "") -> str:
    from andamio.nucleo import consola
    from andamio.nucleo.generador import nombre_variante

    programa = consola.programa()
    nombre = raiz.resolve().name
    tipo = stack.titulo + (f" ({nombre_variante(stack, variante)})" if variante else "")
    secciones = [
        _seccion("marcha", "Ponerlo en marcha", _pasos(stack, raiz, variante), "Desde la carpeta del proyecto, en la terminal:"),
        _seccion("generado", "Lo que ya generaste", _generado(stack, raiz, programa), "Cada pieza con sus archivos (tocá uno para abrirlo) y dónde quedó conectada."),
        _seccion("logica", "Dónde va tu lógica", _logica(raiz), "andamio marca con <code>TODO(logica)</code> los lugares donde va lo tuyo: validaciones, reglas al guardar..."),
        _seccion("piezas", "Qué más podés generar", _piezas(stack, raiz, variante, programa), f"Cada pieza con su comando. Lo que va entre &lt; &gt; lo elegís vos."),
        _seccion("conexiones", "Dónde se conecta cada cosa", _conexiones(stack, raiz, variante), "andamio agrega las rutas, imports y menús antes de estas líneas. Si las borrás, te muestra qué pegar a mano."),
        _tipos(stack),
        _seccion("comandos", "Otros comandos", f'<ul class="pasos">{_otros(programa)}</ul>'),
    ]
    indice = "".join(
        f'<a href="#{i}">{t}</a>'
        for i, t in [("marcha", "En marcha"), ("generado", "Generado"), ("logica", "Tu lógica"), ("piezas", "Generar"), ("conexiones", "Conexiones"), ("comandos", "Comandos")]
    )
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    return _PLANTILLA.format(
        titulo=_e(f"{nombre} · andamio"),
        nombre=_e(nombre),
        tipo=_e(tipo),
        version=_e(__version__),
        fecha=_e(ahora),
        indice=indice,
        secciones="".join(secciones),
        guia_online=f"{URL_GUIAS}/{stack.clave}.html",
        archivo=ARCHIVO,
    )


def escribir(stack: Stack, raiz: Path, variante: str = "") -> bool:
    """Escribe (o actualiza) la página. Nunca hace fallar al comando que la llama."""
    try:
        (raiz / ARCHIVO).write_text(contenido(stack, raiz, variante), encoding="utf-8")
        return True
    except Exception:
        return False


def actualizar(stack: Stack, raiz: Path, variante: str = "") -> None:
    """Después de `nuevo`: la actualiza si el proyecto la tiene (los creados antes no la tienen)."""
    if (raiz / ARCHIVO).is_file():
        escribir(stack, raiz, variante)


_PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>
:root {{ --fondo:#f7f5f0; --sup:#fff; --texto:#1b2430; --tenue:#586272; --borde:#ddd6c8; --acento:#e2a012; --azul:#1f4e79; --ok:#1a7f37; --mal:#b42318; --code:#efebe2; }}
@media (prefers-color-scheme: dark) {{ :root {{ --fondo:#0f141a; --sup:#18202a; --texto:#e6edf3; --tenue:#9aa5b1; --borde:#2a3440; --acento:#f2b72b; --azul:#79c0ff; --ok:#56d364; --mal:#ff7b72; --code:#141b23; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--fondo); color:var(--texto); font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
a {{ color:var(--azul); }}
code {{ font-family:ui-monospace,Consolas,monospace; font-size:.88em; }}
header {{ padding:28px 16px 18px; background:var(--sup); border-bottom:1px solid var(--borde); }}
header .c, main, nav .c {{ max-width:980px; margin:0 auto; }}
h1 {{ margin:0; font-size:1.9rem; }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 0; padding:0; list-style:none; }}
.chips li {{ padding:2px 10px; border:1px solid var(--borde); border-radius:999px; font-size:.85rem; }}
.nota {{ margin:12px 0 0; color:var(--tenue); font-size:.92rem; }}
nav {{ position:sticky; top:0; z-index:1; background:var(--fondo); border-bottom:1px solid var(--borde); }}
nav .c {{ display:flex; gap:16px; overflow-x:auto; padding:10px 16px; }}
nav a {{ white-space:nowrap; text-decoration:none; font-weight:600; }}
main {{ padding:8px 16px 60px; }}
section {{ margin-top:34px; scroll-margin-top:60px; }}
h2 {{ margin:0 0 4px; font-size:1.35rem; }}
.bajada {{ margin:0 0 14px; color:var(--tenue); }}
.cmd {{ display:flex; align-items:center; gap:8px; padding:6px 8px 6px 12px; border:1px solid var(--borde); border-radius:8px; background:var(--code); }}
.cmd code {{ flex:1; min-width:0; overflow-x:auto; white-space:pre; }}
.cmd button {{ flex:none; }}
button {{ font:inherit; font-size:.8rem; padding:3px 10px; border:1px solid var(--borde); border-radius:6px; background:var(--sup); color:var(--texto); cursor:pointer; }}
.pasos {{ display:grid; gap:10px; margin:0; padding-left:1.4rem; }}
.pasos p {{ margin:4px 0 0; color:var(--tenue); }}
details {{ margin:0 0 8px; border:1px solid var(--borde); border-radius:10px; background:var(--sup); }}
summary {{ padding:10px 14px; cursor:pointer; }}
summary small {{ color:var(--tenue); margin-left:6px; }}
.det {{ padding:0 14px 10px; }}
.det h4 {{ margin:8px 0 2px; font-size:.85rem; color:var(--tenue); }}
.det ul {{ margin:0; padding-left:1.2rem; }}
.ok {{ color:var(--ok); font-weight:600; }}
.mal {{ color:var(--mal); font-weight:600; }}
.falta {{ color:var(--mal); text-decoration:line-through; }}
.vacio {{ padding:12px 14px; border:1px dashed var(--borde); border-radius:10px; color:var(--tenue); }}
table {{ width:100%; border-collapse:collapse; background:var(--sup); border:1px solid var(--borde); border-radius:10px; overflow:hidden; font-size:.92rem; }}
th, td {{ padding:8px 10px; border-bottom:1px solid var(--borde); text-align:left; vertical-align:top; }}
th {{ background:var(--code); }}
td small {{ color:var(--tenue); }}
input[type=search] {{ width:100%; margin:0 0 12px; padding:9px 12px; border:1px solid var(--borde); border-radius:8px; background:var(--sup); color:var(--texto); font:inherit; }}
.piezas {{ display:grid; gap:12px; grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr)); }}
.pieza {{ padding:14px; border:1px solid var(--borde); border-radius:12px; background:var(--sup); min-width:0; }}
.pieza h3 {{ margin:0; }}
.pieza h3 small {{ color:var(--tenue); font-weight:400; font-family:ui-monospace,Consolas,monospace; font-size:.8rem; }}
.pieza > p {{ margin:4px 0; }}
.rotulo {{ margin:12px 0 4px !important; color:var(--tenue); font-size:.75rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase; }}
.forma code {{ font-weight:600; }}
.lista, .donde {{ margin:0; padding-left:1.1rem; font-size:.92rem; }}
.lista li {{ margin:4px 0; }}
.donde span {{ color:var(--tenue); }}
footer {{ max-width:980px; margin:0 auto; padding:0 16px 40px; color:var(--tenue); font-size:.88rem; }}
</style>
</head>
<body>
<header><div class="c">
<h1>{nombre}</h1>
<ul class="chips"><li>Proyecto {tipo}</li><li>andamio {version}</li><li>Actualizada: {fecha}</li></ul>
<p class="nota">Esta página la armó andamio con lo que tiene tu proyecto. Se actualiza sola cada vez que generás una pieza.
No se sube al repositorio (está en .gitignore). La guía completa, con ejemplos y el código de cada pieza: <a href="{guia_online}">{guia_online}</a>.</p>
</div></header>
<nav><div class="c">{indice}</div></nav>
<main>{secciones}</main>
<footer>{archivo} · generado por andamio {version}</footer>
<script>
document.addEventListener("click", async (ev) => {{
  const b = ev.target.closest("[data-copiar]");
  if (!b) return;
  try {{ await navigator.clipboard.writeText(b.dataset.copiar); }} catch (e) {{
    const t = document.createElement("textarea"); t.value = b.dataset.copiar; document.body.appendChild(t); t.select(); document.execCommand("copy"); t.remove();
  }}
  const antes = b.textContent; b.textContent = "¡Copiado!"; setTimeout(() => (b.textContent = antes), 1400);
}});
const filtro = document.querySelector("[data-filtro]");
if (filtro) filtro.addEventListener("input", () => {{
  const q = filtro.value.trim().toLowerCase();
  document.querySelectorAll(".pieza").forEach((p) => (p.hidden = q && !p.dataset.buscar.includes(q)));
}});
</script>
</body>
</html>
"""
