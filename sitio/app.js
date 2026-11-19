/* andamio · sitio. Sin librerías: los datos vienen de datos.js (scripts/sitio.py). */
(function () {
  "use strict";

  const datos = window.ANDAMIO;
  const sinMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // --- Utilidades ------------------------------------------------------------

  function escapar(texto) {
    return texto.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
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
    const original = boton.textContent;
    boton.textContent = "¡Copiado!";
    setTimeout(() => (boton.textContent = original), 1500);
  }

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

  // --- Resaltado de sintaxis mínimo -------------------------------------------

  const PALABRAS = {
    python:
      "and as assert async await break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield",
    ts: "as async await break case catch class const continue default delete do else export extends false finally for from function if import in instanceof interface let new null of return static super switch this throw true try type typeof undefined var void while readonly",
    json: "true false null",
    sql: "CREATE TABLE IF NOT EXISTS INTEGER PRIMARY KEY AUTOINCREMENT TEXT REAL NULL SELECT INSERT INTO VALUES UPDATE SET DELETE FROM WHERE ORDER BY",
    css: "",
    html: "",
    md: "",
    texto: "",
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

  function regla(lenguaje) {
    if (reglas[lenguaje]) return reglas[lenguaje];
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

  const CLASES = { com: "h-com", str: "h-str", num: "h-num", kw: "h-kw", fn: "h-fn", tipo: "h-tipo" };

  /** Devuelve el código resaltado, una línea por <span class="l">. */
  function resaltar(codigo, lenguaje) {
    const tokens = [];
    const expresion = regla(lenguaje);
    let ultimo = 0;
    if (expresion) {
      expresion.lastIndex = 0;
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

  // --- Terminal animada del menú -----------------------------------------------

  const terminalMenu = document.getElementById("terminal-menu");
  let reproduccion = { cancelada: false };

  async function escribir(destino, texto, ms) {
    for (const letra of texto) {
      destino.textContent += letra;
      await esperar(ms);
    }
  }

  async function reproducirMenu() {
    reproduccion.cancelada = true;
    const actual = { cancelada: false };
    reproduccion = actual;
    terminalMenu.innerHTML = "";
    const cursor = document.createElement("span");
    cursor.className = "cursor";

    const agregar = (html) => {
      cursor.insertAdjacentHTML("beforebegin", html);
      terminalMenu.scrollTop = terminalMenu.scrollHeight;
    };
    terminalMenu.appendChild(cursor);

    agregar('<span class="t-tenue">C:\\Users\\alumno\\mi-api&gt;</span> ');
    const comando = document.createElement("span");
    comando.className = "t-comando";
    terminalMenu.insertBefore(comando, cursor);
    await esperar(500);
    await escribir(comando, "andamio", 90);
    await esperar(300);
    agregar("\n");

    for (const evento of datos.menu) {
      if (actual.cancelada) return;
      if (evento.tipo === "salida") {
        const lineas = evento.texto.split("\n");
        for (let i = 0; i < lineas.length; i++) {
          agregar(ansiAHtml(lineas[i]) + (i < lineas.length - 1 ? "\n" : ""));
          await esperar(45);
          if (actual.cancelada) return;
        }
      } else {
        agregar(ansiAHtml(evento.pregunta));
        await esperar(450);
        const respuesta = document.createElement("span");
        respuesta.className = "t-respuesta";
        terminalMenu.insertBefore(respuesta, cursor);
        await escribir(respuesta, evento.respuesta, 85);
        if (!evento.respuesta) {
          respuesta.className = "t-tenue";
          respuesta.textContent = "↵";
        }
        await esperar(250);
        agregar("\n");
      }
    }
  }

  // --- Demo por stack ------------------------------------------------------------

  const ORDEN = { carpeta: 0, archivo: 1 };

  function armarArbol(archivos) {
    const raiz = { hijos: new Map() };
    for (const archivo of archivos) {
      const partes = archivo.ruta.split("/");
      let nodo = raiz;
      partes.forEach((parte, i) => {
        if (!nodo.hijos.has(parte)) {
          nodo.hijos.set(parte, i === partes.length - 1 ? { archivo } : { hijos: new Map() });
        }
        nodo = nodo.hijos.get(parte);
      });
    }
    return raiz;
  }

  function tieneCambios(nodo) {
    if (nodo.archivo) return nodo.archivo.estado !== "proyecto";
    return Array.from(nodo.hijos.values()).some(tieneCambios);
  }

  function dibujarArbol(nodo) {
    const entradas = Array.from(nodo.hijos.entries()).sort(([a, x], [b, y]) => {
      const tipoX = x.archivo ? "archivo" : "carpeta";
      const tipoY = y.archivo ? "archivo" : "carpeta";
      return ORDEN[tipoX] - ORDEN[tipoY] || a.localeCompare(b, "es", { sensitivity: "base" });
    });
    return entradas
      .map(([nombre, hijo]) => {
        if (hijo.archivo) {
          const a = hijo.archivo;
          return `<li><button type="button" class="archivo" data-ruta="${escapar(a.ruta)}" title="${escapar(a.ruta)}">
            <i class="estado estado--${a.estado}"></i><span class="nombre">${escapar(nombre)}</span></button></li>`;
        }
        const abierta = tieneCambios(hijo);
        return `<li><button type="button" class="carpeta" aria-expanded="${abierta}"><span class="nombre">${escapar(nombre)}/</span></button>
          <ul${abierta ? "" : " hidden"}>${dibujarArbol(hijo)}</ul></li>`;
      })
      .join("");
  }

  const elementos = {
    terminal: document.getElementById("demo-terminal"),
    arbol: document.getElementById("demo-arbol"),
    carpeta: document.getElementById("demo-carpeta"),
    nombre: document.getElementById("codigo-nombre"),
    codigo: document.getElementById("codigo-contenido"),
    copiar: document.getElementById("codigo-copiar"),
  };
  let stackActual = null;
  let archivoActual = null;

  function mostrarArchivo(ruta) {
    archivoActual = stackActual.archivos.find((a) => a.ruta === ruta);
    if (!archivoActual) return;
    elementos.nombre.textContent = ruta;
    elementos.codigo.innerHTML = resaltar(archivoActual.contenido, archivoActual.lenguaje);
    elementos.codigo.parentElement.scrollTop = 0;
    elementos.arbol.querySelectorAll(".archivo").forEach((b) => {
      b.setAttribute("aria-current", String(b.dataset.ruta === ruta));
    });
  }

  function mostrarStack(clave) {
    stackActual = datos.stacks.find((s) => s.clave === clave);
    elementos.terminal.innerHTML = stackActual.pasos
      .map((p) => `<span class="t-tenue">&gt;</span> <span class="t-comando">${escapar(p.comando)}</span>\n${ansiAHtml(p.salida)}`)
      .join("\n\n");
    elementos.carpeta.textContent = stackActual.carpeta + "/";
    elementos.arbol.innerHTML = dibujarArbol(armarArbol(stackActual.archivos));
    mostrarArchivo(stackActual.destacado);
  }

  elementos.arbol.addEventListener("click", (e) => {
    const boton = e.target.closest("button");
    if (!boton) return;
    if (boton.classList.contains("carpeta")) {
      const abierta = boton.getAttribute("aria-expanded") === "true";
      boton.setAttribute("aria-expanded", String(!abierta));
      boton.nextElementSibling.hidden = abierta;
    } else {
      mostrarArchivo(boton.dataset.ruta);
    }
  });

  elementos.copiar.addEventListener("click", () => {
    if (archivoActual) copiar(archivoActual.contenido, elementos.copiar);
  });

  // --- Inicio ------------------------------------------------------------------

  if (!datos) {
    const aviso = "Faltan los datos de la demostración. Generalos con: python scripts/sitio.py";
    terminalMenu.textContent = aviso;
    elementos.terminal.textContent = aviso;
  } else {
    document.querySelectorAll("[data-version]").forEach((e) => (e.textContent = datos.version));

    const listaStacks = document.getElementById("pestanas-stack");
    listaStacks.innerHTML = datos.stacks
      .map(
        (s, i) =>
          `<button role="tab" type="button" aria-selected="${i === 0}" aria-controls="demo-panel" data-stack="${s.clave}">${escapar(s.titulo)}</button>`,
      )
      .join("");
    pestanas(listaStacks, (boton) => mostrarStack(boton.dataset.stack));

    reproducirMenu();
    document.getElementById("repetir-menu").addEventListener("click", reproducirMenu);
  }

  // Comandos de instalación con la versión actual.
  const version = datos ? datos.version : "1.0.0";
  const whl = `https://github.com/rodal95/andamio/releases/download/v${version}/andamio-${version}-py3-none-any.whl`;
  document.querySelectorAll("[data-instalar]").forEach((e) => {
    e.textContent = `${e.dataset.instalar} -m pip install ${whl}`;
  });
  document.querySelectorAll(".comando__copiar").forEach((boton) => {
    boton.addEventListener("click", () => copiar(boton.previousElementSibling.textContent, boton));
  });

  pestanas(document.getElementById("pestanas-instalar"), (boton) => {
    document.querySelectorAll(".instalar__panel").forEach((panel) => {
      panel.hidden = panel.id !== boton.dataset.panel;
    });
  });
})();
