"""Cómo se ve la página al compartirla: imágenes, etiquetas para redes y buscadores.

    python scripts/compartir_sitio.py            genera todo (imágenes y etiquetas)
    python scripts/compartir_sitio.py --etiquetas  solo las etiquetas (no necesita Chromium)

Para cada página de sitio/ (la portada y una guía por tecnología):

- Una imagen de 1200x630 (sitio/img/compartir/<página>.png) con el logo, el título y
  comandos reales de la guía: es la vista previa de WhatsApp, Facebook, LinkedIn, X,
  Discord o Slack al pegar el enlace.
- Las etiquetas Open Graph y Twitter Card, la dirección canónica y los íconos, en un
  bloque marcado del <head> (se reemplaza cada vez: no editar a mano).

Además: los íconos PNG del logo (a partir de sitio/favicon.svg), site.webmanifest y
sitemap.xml (para darlo de alta en Google Search Console; robots.txt no sirve en una
subcarpeta como /andamio/). tests/integracion/test_sitio.py controla que las etiquetas
estén al día y que cada imagen exista.

Las imágenes necesitan Playwright para Python con Chromium:
    python -m pip install playwright && python -m playwright install chromium
Se ejecuta a mano cuando cambian los títulos o las guías, y se suben las imágenes.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITIO = RAIZ / "sitio"
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

from andamio import stacks  # noqa: E402

BASE = "https://rodal95.github.io/andamio/"
CARPETA_IMAGENES = SITIO / "img" / "compartir"
INICIO = "<!-- compartir: lo genera scripts/compartir_sitio.py (no editar a mano) -->"
FIN = "<!-- /compartir -->"
FONDO, ACENTO, TEXTO = "#1b2430", "#e2a012", "#f7f5f0"


def paginas() -> list[dict]:
    """Cada página del sitio con su título y su descripción (los del <head>)."""
    resultado = []
    for clave in ["index", *(s.clave for s in stacks.ORDEN_MENU)]:
        archivo = SITIO / f"{clave}.html"
        texto = archivo.read_text(encoding="utf-8")
        titulo = html.unescape(re.search(r"<title>(.*?)</title>", texto).group(1))
        descripcion = html.unescape(re.search(r'<meta property="og:description" content="(.*?)" />', texto).group(1))
        resultado.append(
            {
                "clave": clave,
                "archivo": archivo,
                "titulo": titulo,
                "descripcion": descripcion,
                "url": BASE if clave == "index" else f"{BASE}{clave}.html",
                "imagen": f"img/compartir/{clave}.png",
            }
        )
    return resultado


# --- Etiquetas -------------------------------------------------------------------------


def _datos_estructurados() -> str:
    datos = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "andamio",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Windows, macOS, Linux",
        "inLanguage": "es",
        "url": BASE,
        "image": f"{BASE}img/compartir/index.png",
        "description": "Generador de código en español: crea proyectos y genera tablas, APIs, componentes y pantallas con un comando.",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "license": "https://opensource.org/licenses/MIT",
        "codeRepository": "https://github.com/rodal95/andamio",
    }
    return '<script type="application/ld+json">' + json.dumps(datos, ensure_ascii=False) + "</script>"


def _datos_guia(pagina: dict) -> str:
    """Una guía: artículo técnico (con su imagen y su idioma) y la ruta de navegación."""
    datos = [
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": pagina["titulo"],
            "description": pagina["descripcion"],
            "inLanguage": "es",
            "url": pagina["url"],
            "image": BASE + pagina["imagen"],
            "proficiencyLevel": "Beginner",
            "isPartOf": {"@type": "WebSite", "name": "andamio", "url": BASE},
            "about": {"@type": "SoftwareApplication", "name": "andamio", "applicationCategory": "DeveloperApplication"},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "andamio", "item": BASE},
                {"@type": "ListItem", "position": 2, "name": pagina["titulo"], "item": pagina["url"]},
            ],
        },
    ]
    return '<script type="application/ld+json">' + json.dumps(datos, ensure_ascii=False) + "</script>"


def bloque(pagina: dict) -> str:
    e = lambda texto: html.escape(texto, quote=True)  # noqa: E731
    imagen = BASE + pagina["imagen"]
    alt = f"{pagina['titulo']}: {pagina['descripcion']}"
    lineas = [
        INICIO,
        f'<link rel="canonical" href="{pagina["url"]}" />',
        '<meta property="og:type" content="website" />',
        '<meta property="og:site_name" content="andamio" />',
        '<meta property="og:locale" content="es_AR" />',
        f'<meta property="og:url" content="{pagina["url"]}" />',
        f'<meta property="og:image" content="{imagen}" />',
        '<meta property="og:image:type" content="image/png" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="{e(alt)}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{e(pagina["titulo"])}" />',
        f'<meta name="twitter:description" content="{e(pagina["descripcion"])}" />',
        f'<meta name="twitter:image" content="{imagen}" />',
        f'<meta name="twitter:image:alt" content="{e(alt)}" />',
        '<link rel="icon" href="img/icono-32.png" sizes="32x32" type="image/png" />',
        '<link rel="apple-touch-icon" href="img/apple-touch-icon.png" />',
        '<link rel="manifest" href="site.webmanifest" />',
    ]
    lineas.append(_datos_estructurados() if pagina["clave"] == "index" else _datos_guia(pagina))
    lineas.append(FIN)
    return "\n".join("    " + linea for linea in lineas)


def cabecera_actualizada(pagina: dict) -> str:
    """El HTML de la página con el bloque de compartir al día (después del favicon)."""
    texto = pagina["archivo"].read_text(encoding="utf-8")
    texto = re.sub(r"\n[ \t]*" + re.escape(INICIO) + r".*?" + re.escape(FIN), "", texto, flags=re.S)
    favicon = '<link rel="icon" href="favicon.svg" type="image/svg+xml" />'
    assert favicon in texto, f"{pagina['archivo'].name} no tiene {favicon}"
    return texto.replace(favicon, favicon + "\n" + bloque(pagina), 1)


def mapa_del_sitio(lista: list[dict]) -> str:
    urls = "\n".join(f"  <url><loc>{p['url']}</loc></url>" for p in lista)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


MANIFIESTO = json.dumps(
    {
        "name": "andamio",
        "short_name": "andamio",
        "description": "Generador de código para tus proyectos, en español.",
        "start_url": "./",
        "display": "standalone",
        "background_color": "#f7f5f0",
        "theme_color": FONDO,
        "icons": [
            {"src": "img/icono-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "img/icono-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    },
    ensure_ascii=False,
    indent=2,
) + "\n"


def archivos_de_texto() -> dict[Path, str]:
    """Todo lo que se escribe como texto: las páginas, el sitemap y el manifiesto."""
    lista = paginas()
    archivos = {p["archivo"]: cabecera_actualizada(p) for p in lista}
    archivos[SITIO / "sitemap.xml"] = mapa_del_sitio(lista)
    archivos[SITIO / "site.webmanifest"] = MANIFIESTO
    return archivos


# --- Imágenes --------------------------------------------------------------------------

LOGO = (
    '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M7 3v26M25 3v26M7 9h18M7 18h18M7 27h18M7 9l18 9M25 18 7 27" '
    f'fill="none" stroke="{ACENTO}" stroke-width="2.6" stroke-linecap="round"/></svg>'
)

ESTILO = f"""
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 1200px; height: 630px; background: {FONDO}; color: {TEXTO};
  font-family: "Noto Sans", "Segoe UI", Roboto, system-ui, sans-serif; overflow: hidden; }}
.lienzo {{ position: relative; height: 100%; padding: 64px 72px; display: flex; flex-direction: column; }}
.grilla {{ position: absolute; inset: 0; opacity: .07;
  background-image: linear-gradient({TEXTO} 1px, transparent 1px), linear-gradient(90deg, {TEXTO} 1px, transparent 1px);
  background-size: 48px 48px; }}
.marca {{ display: flex; align-items: center; gap: 18px; font-size: 44px; font-weight: 800; letter-spacing: -.02em; }}
.marca svg {{ width: 60px; height: 60px; }}
h1 {{ margin-top: 40px; font-size: 68px; line-height: 1.05; font-weight: 800; letter-spacing: -.03em; max-width: 1000px; }}
h1 span {{ color: {ACENTO}; }}
p {{ margin-top: 20px; font-size: 27px; line-height: 1.35; color: #c5ccd6; max-width: 1000px; }}
.terminal {{ margin-top: auto; background: #11161d; border: 1px solid #2c3644; border-radius: 14px; padding: 20px 26px;
  font-family: "Cascadia Code", "DejaVu Sans Mono", Consolas, monospace; font-size: 23px; line-height: 1.6; }}
.terminal div {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.guia h1 {{ font-size: 60px; }}
.terminal b {{ color: #7ee787; font-weight: 400; }}
.terminal i {{ color: #8b949e; font-style: normal; }}
.pie {{ position: absolute; right: 72px; top: 76px; font-size: 22px; color: #8b949e; }}
"""


def _comandos(clave: str) -> list[str]:
    import sitio

    if clave == "index":
        return [
            "python -m andamio crear django mi-api",
            "python -m andamio nuevo recurso producto nombre:str precio:decimal",
            "python -m andamio nuevo crud producto nombre:str precio:decimal",
        ]
    info = sitio.TECNOLOGIAS[clave]
    piezas = list(info["piezas"].values())
    # Primero las piezas con campos (son las más vistosas), después las demás.
    piezas.sort(key=lambda p: ":" not in p["comando"])
    # Con dos campos alcanza para el ejemplo (así entra en una línea).
    cortos = [" ".join(w for i, w in enumerate(p["comando"].split()) if ":" not in w or i < 5) for p in piezas[:2]]
    return [f"python -m andamio crear {clave} {info['carpeta']}", *(f"python -m andamio {c}" for c in cortos)]


def html_imagen(pagina: dict) -> str:
    e = html.escape
    if pagina["clave"] == "index":
        titulo = "Armá la estructura.<br><span>Programá la lógica.</span>"
        texto = "Creá proyectos y generá tablas, APIs, componentes y pantallas con un comando. En español."
    else:
        tecnologia = pagina["titulo"].removeprefix("andamio con ")
        titulo = f"andamio con <span>{e(tecnologia)}</span>"
        texto = pagina["descripcion"]
    lineas = []
    for comando in _comandos(pagina["clave"]):
        verbo, _, resto = comando.removeprefix("python -m andamio ").partition(" ")
        lineas.append(f"<div><i>&gt;</i> python -m andamio <b>{e(verbo)}</b> {e(resto)}</div>")
    terminal = "".join(lineas)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{ESTILO}</style></head>
<body class="{'portada' if pagina['clave'] == 'index' else 'guia'}"><div class="lienzo"><div class="grilla"></div>
<div class="marca">{LOGO} andamio</div>
<div class="pie">rodal95.github.io/andamio</div>
<h1>{titulo}</h1><p>{e(texto)}</p>
<div class="terminal">{terminal}</div>
</div></body></html>"""


def generar_imagenes() -> None:
    from playwright.sync_api import sync_playwright

    CARPETA_IMAGENES.mkdir(parents=True, exist_ok=True)
    favicon = (SITIO / "favicon.svg").read_text(encoding="utf-8")
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina_web = navegador.new_page(viewport={"width": 1200, "height": 630})
        for pagina in paginas():
            pagina_web.set_content(html_imagen(pagina), wait_until="load")
            destino = SITIO / pagina["imagen"]
            pagina_web.screenshot(path=str(destino))
            print(f"{destino.relative_to(RAIZ)}")
        for nombre, lado in (("icono-32.png", 32), ("apple-touch-icon.png", 180), ("icono-192.png", 192), ("icono-512.png", 512)):
            icono = navegador.new_page(viewport={"width": lado, "height": lado})
            # El ícono de iPhone va sin transparencia (iOS redondea las esquinas solo): fondo lleno.
            apple = nombre == "apple-touch-icon.png"
            fondo = f"body{{background:{FONDO}}}" if apple else ""
            svg = favicon.replace('rx="7"', 'rx="0"') if apple else favicon
            icono.set_content(f"<style>*{{margin:0}}{fondo}svg{{display:block;width:{lado}px;height:{lado}px}}</style>{svg}")
            icono.screenshot(path=str(SITIO / "img" / nombre), omit_background=not apple)
            icono.close()
            print(f"sitio/img/{nombre}")
        navegador.close()


def main() -> None:
    for ruta, texto in archivos_de_texto().items():
        ruta.write_text(texto, encoding="utf-8")
        print(ruta.relative_to(RAIZ))
    if "--etiquetas" not in sys.argv:
        generar_imagenes()


if __name__ == "__main__":
    main()
