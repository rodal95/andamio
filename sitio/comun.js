/* andamio · sitio: utilidades compartidas por todas las páginas (sin librerías). */
(function () {
  "use strict";

  const sinMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const PAGINAS = [
    { href: "index.html", texto: "Inicio" },
    { href: "python.html", texto: "Python" },
    { href: "django.html", texto: "Django" },
    { href: "react.html", texto: "React" },
    { href: "react-native.html", texto: "React Native" },
  ];

  // --- Texto y HTML ------------------------------------------------------------

  function escapar(texto) {
    return String(texto).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  }

  /** Convierte los colores ANSI de la terminal (\x1b[32;1m ... \x1b[0m) en <span>. */
  function ansiAHtml(texto) {
    const partes = texto.split(/\x1b\[([\d;]*)m/);
    let html = "";
    let abierto = false;
    partes.forEach((parte, i) => {
      if (i % 2 === 0) {
        html += escapar(parte);
        return;
      }
      if (abierto) {
        html += "</span>";
        abierto = false;
      }
      const codigos = parte.split(";").filter((c) => c && c !== "0");
      if (codigos.length) {
        html += `<span class="${codigos.map((c) => "a" + c).join(" ")}">`;
        abierto = true;
      }
    });
    return abierto ? html + "</span>" : html;
  }

  /** Un comando con su salida, como en la terminal. */
  function terminalHtml(comando, salida) {
    return `<span class="t-tenue">&gt;</span> <span class="t-comando">${escapar(comando)}</span>\n${ansiAHtml(salida)}`;
  }

  const esperar = (ms) => new Promise((resolver) => setTimeout(resolver, sinMovimiento ? 0 : ms));

  async function copiar(texto, boton) {
    try {
      await navigator.clipboard.writeText(texto);
    } catch {
      const area = document.createElement("textarea");
      area.value = texto;
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }
    if (boton) {
      const original = boton.textContent;
      boton.textContent = "¡Copiado!";
      setTimeout(() => (boton.textContent = original), 1500);
    }
  }

  /** Bloque de comando con botón Copiar. */
  function comandoHtml(comando, clase = "") {
    return `<div class="comando ${clase}"><code>${escapar(comando)}</code><button type="button" class="comando__copiar" data-copiar="${escapar(comando)}">Copiar</button></div>`;
  }

  // Un solo manejador para todos los botones de copiar de la página.
  document.addEventListener("click", (e) => {
    const boton = e.target.closest("[data-copiar]");
    if (boton) copiar(boton.dataset.copiar, boton);
  });

  /** Pestañas accesibles: clic y flechas izquierda/derecha. */
  function pestanas(lista, alElegir) {
    const botones = () => Array.from(lista.querySelectorAll('[role="tab"]'));
    function elegir(boton) {
      botones().forEach((b) => {
        const activo = b === boton;
        b.setAttribute("aria-selected", String(activo));
        b.tabIndex = activo ? 0 : -1;
      });
      alElegir(boton);
    }
    lista.addEventListener("click", (e) => {
      const boton = e.target.closest('[role="tab"]');
      if (boton) elegir(boton);
    });
    lista.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      const todos = botones();
      const actual = todos.indexOf(document.activeElement);
      const siguiente = todos[(actual + (e.key === "ArrowRight" ? 1 : -1) + todos.length) % todos.length];
      siguiente.focus();
      elegir(siguiente);
    });
    const inicial = botones().find((b) => b.getAttribute("aria-selected") === "true") || botones()[0];
    if (inicial) elegir(inicial);
  }

  // --- Resaltado de sintaxis mínimo ---------------------------------------------

  const PALABRAS = {
    python:
      "and as assert async await break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield",
    ts: "as async await break case catch class const continue default delete do else export extends false finally for from function if import in instanceof interface let new null of return static super switch this throw true try type typeof undefined var void while readonly",
    json: "true false null",
    sql: "CREATE TABLE IF NOT EXISTS INTEGER PRIMARY KEY AUTOINCREMENT TEXT REAL NULL SELECT INSERT INTO VALUES UPDATE SET DELETE FROM WHERE ORDER BY",
  };

  const COMENTARIOS = {
    python: String.raw`#.*`,
    ts: String.raw`\/\/.*|\/\*[\s\S]*?\*\/`,
    sql: String.raw`--.*`,
    css: String.raw`\/\*[\s\S]*?\*\/`,
    html: String.raw`<!--[\s\S]*?-->`,
    md: String.raw`^#{1,6} .*$`,
    texto: String.raw`#.*`,
  };

  const CADENAS = {
    python: String.raw`"""[\s\S]*?"""|'''[\s\S]*?'''|[rf]?"(?:[^"\\\n]|\\.)*"|[rf]?'(?:[^'\\\n]|\\.)*'`,
    ts: String.raw`\`(?:[^\`\\]|\\.)*\`|"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'`,
    json: String.raw`"(?:[^"\\\n]|\\.)*"`,
    sql: String.raw`'[^'\n]*'`,
    css: String.raw`"[^"\n]*"`,
    html: String.raw`"[^"\n]*"`,
  };

  const reglas = {};
  const CLASES = { com: "h-com", str: "h-str", num: "h-num", kw: "h-kw", fn: "h-fn", tipo: "h-tipo" };

  function regla(lenguaje) {
    if (lenguaje in reglas) return reglas[lenguaje];
    const partes = [];
    if (COMENTARIOS[lenguaje]) partes.push(`(?<com>${COMENTARIOS[lenguaje]})`);
    if (CADENAS[lenguaje]) partes.push(`(?<str>${CADENAS[lenguaje]})`);
    if (lenguaje !== "texto" && lenguaje !== "md") partes.push(String.raw`(?<num>\b\d+(?:\.\d+)?\b)`);
    if (PALABRAS[lenguaje]) partes.push(`(?<kw>\\b(?:${PALABRAS[lenguaje].split(" ").join("|")})\\b)`);
    if (lenguaje === "python" || lenguaje === "ts") {
      partes.push(String.raw`(?<fn>\b[a-z_]\w*(?=\())`);
      partes.push(String.raw`(?<tipo>\b[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*\b)`);
    }
    reglas[lenguaje] = partes.length ? new RegExp(partes.join("|"), "gm") : null;
    return reglas[lenguaje];
  }

  /** Código resaltado, una línea por <span class="l">. */
  function resaltar(codigo, lenguaje) {
    const tokens = [];
    const expresion = regla(lenguaje);
    let ultimo = 0;
    if (expresion) {
      for (const m of codigo.matchAll(expresion)) {
        if (m.index > ultimo) tokens.push([null, codigo.slice(ultimo, m.index)]);
        const tipo = Object.keys(m.groups).find((k) => m.groups[k] !== undefined);
        tokens.push([CLASES[tipo], m[0]]);
        ultimo = m.index + m[0].length;
      }
    }
    tokens.push([null, codigo.slice(ultimo)]);
    const lineas = [""];
    for (const [clase, texto] of tokens) {
      texto.split("\n").forEach((trozo, i) => {
        if (i > 0) lineas.push("");
        if (trozo) lineas[lineas.length - 1] += clase ? `<span class="${clase}">${escapar(trozo)}</span>` : escapar(trozo);
      });
    }
    if (lineas.length > 1 && lineas[lineas.length - 1] === "") lineas.pop();
    return lineas.map((l) => `<span class="l">${l || " "}</span>`).join("");
  }

  function codigoHtml(codigo, lenguaje, numerado = false) {
    return `<pre class="codigo-suelto${numerado ? " codigo-suelto--numerado" : ""}"><code>${resaltar(codigo, lenguaje)}</code></pre>`;
  }

  // --- Visor de archivos (diálogo) ----------------------------------------------

  let visor = null;
  let contenidoVisor = "";

  function crearVisor() {
    visor = document.createElement("dialog");
    visor.className = "visor";
    visor.setAttribute("aria-labelledby", "visor-ruta");
    visor.innerHTML = `
      <div class="visor__barra">
        <div class="visor__titulos"><p class="visor__ruta" id="visor-ruta"></p><p class="visor__desc"></p></div>
        <button type="button" class="terminal__boton" data-visor-copiar>Copiar</button>
        <button type="button" class="terminal__boton" data-visor-cerrar aria-label="Cerrar">Cerrar ✕</button>
      </div>
      <pre class="codigo__cuerpo"><code></code></pre>`;
    document.body.appendChild(visor);
    visor.querySelector("[data-visor-cerrar]").addEventListener("click", () => visor.close());
    visor.querySelector("[data-visor-copiar]").addEventListener("click", (e) => copiar(contenidoVisor, e.target));
    visor.addEventListener("click", (e) => {
      if (e.target === visor) visor.close();
    });
  }

  /** Muestra un archivo generado: ruta, para qué sirve y su contenido. */
  function abrirArchivo(archivo) {
    if (!visor) crearVisor();
    contenidoVisor = archivo.lenguaje === "imagen" ? "" : archivo.contenido;
    visor.querySelector(".visor__ruta").textContent = archivo.ruta;
    visor.querySelector(".visor__desc").textContent = archivo.descripcion || "";
    visor.querySelector("[data-visor-copiar]").hidden = archivo.lenguaje === "imagen";
    const destino = visor.querySelector("code");
    destino.innerHTML =
      archivo.lenguaje === "imagen"
        ? `<img class="visor__imagen" src="${archivo.contenido}" alt="${escapar(archivo.ruta)}">`
        : resaltar(archivo.contenido, archivo.lenguaje);
    visor.showModal();
    visor.querySelector(".codigo__cuerpo").scrollTop = 0;
  }

  // --- Árbol de archivos ----------------------------------------------------------

  function armarArbol(archivos) {
    const raiz = { hijos: new Map() };
    for (const archivo of archivos) {
      const partes = archivo.ruta.split("/");
      let nodo = raiz;
      partes.forEach((parte, i) => {
        if (!nodo.hijos.has(parte)) nodo.hijos.set(parte, i === partes.length - 1 ? { archivo } : { hijos: new Map() });
        nodo = nodo.hijos.get(parte);
      });
    }
    return raiz;
  }

  function tieneCambios(nodo) {
    if (nodo.archivo) return nodo.archivo.estado !== "proyecto";
    return Array.from(nodo.hijos.values()).some(tieneCambios);
  }

  function arbolHtml(nodo) {
    const entradas = Array.from(nodo.hijos.entries()).sort(([a, x], [b, y]) => {
      const orden = (n) => (n.archivo ? 1 : 0);
      return orden(x) - orden(y) || a.localeCompare(b, "es", { sensitivity: "base" });
    });
    return entradas
      .map(([nombre, hijo]) => {
        if (hijo.archivo) {
          const a = hijo.archivo;
          return `<li><button type="button" class="archivo" data-ruta="${escapar(a.ruta)}" title="${escapar(a.descripcion || a.ruta)}">
            <i class="estado estado--${a.estado}"></i><span class="nombre">${escapar(nombre)}</span></button></li>`;
        }
        const abierta = tieneCambios(hijo);
        return `<li><button type="button" class="carpeta" aria-expanded="${abierta}"><span class="nombre">${escapar(nombre)}/</span></button>
          <ul${abierta ? "" : " hidden"}>${arbolHtml(hijo)}</ul></li>`;
      })
      .join("");
  }

  // --- Barra y pie comunes -----------------------------------------------------------

  function dibujarBarra() {
    const barra = document.querySelector("[data-barra]");
    if (!barra) return;
    const actual = location.pathname.split("/").pop() || "index.html";
    barra.className = "barra";
    barra.innerHTML = `
      <div class="contenedor barra__interior">
        <a class="marca" href="index.html" aria-label="andamio, inicio">
          <svg class="marca__icono" viewBox="0 0 32 32" aria-hidden="true"><path d="M7 3v26M25 3v26M7 9h18M7 18h18M7 27h18M7 9l18 9M25 18 7 27" /></svg>
          andamio
        </a>
        <nav class="barra__nav" aria-label="Guías">
          ${PAGINAS.map((p) => `<a href="${p.href}"${p.href === actual ? ' aria-current="page"' : ""}>${p.texto}</a>`).join("")}
        </nav>
        <a class="boton boton--chico boton--borde" href="https://github.com/rodal95/andamio">GitHub</a>
      </div>`;
  }

  function dibujarPie(version) {
    const pie = document.querySelector("[data-pie]");
    if (!pie) return;
    pie.className = "pie";
    pie.innerHTML = `
      <div class="contenedor pie__interior">
        <span>andamio v${escapar(version)} · Licencia MIT</span>
        <span>
          <a href="https://github.com/rodal95/andamio">Código</a> ·
          <a href="https://github.com/rodal95/andamio/releases">Versiones</a> ·
          <a href="https://github.com/rodal95/andamio/blob/main/docs/docente.md">Guía para docentes</a>
        </span>
      </div>`;
  }

  const datos = window.ANDAMIO;
  const version = datos ? datos.version : "1.0.0";
  const urlWhl = `https://github.com/rodal95/andamio/releases/download/v${version}/andamio-${version}-py3-none-any.whl`;

  dibujarBarra();
  dibujarPie(version);

  window.Andamio = {
    datos,
    version,
    urlWhl,
    sinMovimiento,
    escapar,
    ansiAHtml,
    terminalHtml,
    esperar,
    copiar,
    comandoHtml,
    pestanas,
    resaltar,
    codigoHtml,
    abrirArchivo,
    armarArbol,
    arbolHtml,
  };
})();
