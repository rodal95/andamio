/* andamio · sitio: la pestaña "Paso a paso" de React, React Native, Django y Python.
 *
 * Los datos los arma scripts/sitio.py ejecutando andamio de verdad (variante.armado):
 * cada paso con su consola, los archivos que crea o modifica (con las líneas nuevas) y
 * cómo queda el proyecto. La vista de cada paso es una demostración que se puede usar:
 * la app en el navegador o en el celular, la API o la sesión de consola real. */
(function () {
  "use strict";

  const A = window.Andamio;
  const e = A.escapar;

  let est = null; // { armado, raiz, paso, juego, app }

  // --- La forma general y el ejemplo ----------------------------------------------

  const esMarcador = (t) => /^\[?</.test(t);

  /** Reparte las palabras del ejemplo entre las de la forma general: qué valor ocupa cada <marcador>. */
  function alinear(forma, ejemplo) {
    const gen = forma.split(" ");
    const ej = ejemplo.split(" ");
    const res = [];
    let j = 0;
    gen.forEach((g, k) => {
      if (!esMarcador(g)) {
        if (ej[j] === g) res.push({ texto: ej[j++] });
        return;
      }
      const etiqueta = g.replace(/\.\.\.$/, "");
      const siguiente = gen.slice(k + 1).find((x) => !esMarcador(x));
      const sufijo = (gen[k + 1] || "").match(/>(:\w+)$/);
      if (g.endsWith("...")) {
        while (j < ej.length && ej[j] !== siguiente && !ej[j].startsWith("--") && !(sufijo && ej[j].endsWith(sufijo[1]))) {
          res.push({ texto: ej[j++], marcador: etiqueta });
        }
      } else if (j < ej.length && ej[j] !== siguiente && !ej[j].startsWith("--")) {
        res.push({ texto: ej[j++], marcador: etiqueta });
      }
    });
    while (j < ej.length) res.push({ texto: ej[j++] });
    return res;
  }

  function formaHtml(forma) {
    return forma
      .split(" ")
      .map((t) => (esMarcador(t) ? `<span class="ph">${e(t)}</span>` : e(t)))
      .join(" ");
  }

  function ejemploHtml(forma, ejemplo) {
    let n = 0;
    return alinear(forma, ejemplo)
      .map((t) => (t.marcador ? `<span class="valor" style="--i:${n++}" title="${e(t.marcador)}">${e(t.texto)}</span>` : e(t.texto)))
      .join(" ");
  }

  function formasHtml(armado) {
    const filas = armado.formas
      .map((f) => {
        const paso = armado.pasos.findIndex((p) => p.forma && p.forma === f.forma);
        const ir = paso >= 0 ? `<button type="button" class="armado-ir" data-armado-paso="${paso}">Paso ${paso + 1} →</button>` : "";
        return `<li class="forma">
          <div class="forma__general"><code>${formaHtml(f.forma)}</code></div>
          <div class="forma__ejemplo"><span class="forma__flecha" aria-hidden="true">↳</span><code>${ejemploHtml(f.forma, f.ejemplo)}</code>
            <button type="button" class="copiar-chico" data-copiar="${e(f.ejemplo)}">Copiar</button></div>
          <p class="forma__que">${e(f.que)} ${ir}</p></li>`;
      })
      .join("");
    return `<ul class="formas">${filas}</ul>`;
  }

  // --- El árbol del proyecto en cada paso -------------------------------------------

  function arbol(rutas, estados) {
    const raiz = {};
    rutas.forEach((r) => {
      let nodo = raiz;
      const partes = r.split("/");
      partes.forEach((p, i) => {
        if (i === partes.length - 1) nodo[p] = r;
        else nodo = nodo[p + "/"] = nodo[p + "/"] || {};
      });
    });
    let n = 0;
    function lista(nodo) {
      const claves = Object.keys(nodo).sort((a, b) => (a.endsWith("/") === b.endsWith("/") ? a.localeCompare(b) : a.endsWith("/") ? -1 : 1));
      return claves
        .map((k) => {
          if (k.endsWith("/")) return `<li><span class="aa-carpeta">${e(k)}</span><ul>${lista(nodo[k])}</ul></li>`;
          const ruta = nodo[k];
          const estado = estados[ruta] || "";
          const anim = estado ? ` style="--i:${n++}"` : "";
          return `<li><button type="button" class="aa-archivo${estado ? ` aa-archivo--${estado}` : ""}" data-armado-ruta="${e(ruta)}"${anim}>${
            estado ? `<i class="estado estado--${estado}"></i>` : ""
          }${e(k)}</button></li>`;
        })
        .join("");
    }
    return `<ul class="aa-arbol">${lista(raiz)}</ul>`;
  }

  // --- Datos de ejemplo de las vistas -----------------------------------------------

  function nuevaApp() {
    const demo = est.armado.demo;
    const filas = {};
    Object.keys(demo).forEach((r) => (filas[r] = demo[r].filas.map((f) => ({ ...f }))));
    return { filas, nuevo: null };
  }

  const campos = (recurso) => est.armado.demo[recurso].campos;
  const plural = (recurso) => recurso + (recurso.endsWith("a") || recurso.endsWith("o") ? "s" : "es");

  function texto(recurso, fila) {
    const c = campos(recurso).find((x) => x.tipo === "str" || x.tipo === "email");
    return c ? fila[c.nombre] : `${recurso} ${fila.id}`;
  }

  function valor(campo, fila) {
    const v = fila[campo.nombre];
    if (campo.tipo === "fk") {
      const destino = (est.app.filas[campo.nombre] || []).find((x) => x.id === v);
      return destino ? texto(campo.nombre, destino) : "—";
    }
    if (campo.tipo === "bool") return v ? "Sí" : "No";
    if (campo.tipo === "decimal") return Number(v).toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return v === undefined || v === null || v === "" ? "—" : String(v);
  }

  // --- La app de ejemplo: navegador (React) o celular (React Native) ------------------

  /** Las pantallas que existen hasta el paso i (cada página o pantalla con --datos). */
  function pantallas(hasta) {
    const lista = [];
    est.armado.pasos.slice(0, hasta + 1).forEach((p) => {
      const v = p.vista;
      if (!v || (v.tipo !== "web" && v.tipo !== "movil")) return;
      lista.push(v);
      // El crud trae lista, detalle y formulario.
      if (p.comando.includes(" nuevo crud ")) {
        lista.push({ ...v, pantalla: "detalle", url: `/${plural(v.recurso)}/1`, deCrud: true });
        lista.push({ ...v, pantalla: "form", url: `/${plural(v.recurso)}/nuevo`, titulo: `Agregar: ${v.recurso}`, deCrud: true });
      }
    });
    return lista;
  }

  const buscar = (lista, recurso, pantalla) => lista.find((p) => p.recurso === recurso && p.pantalla === pantalla);

  function contenidoApp(vista, lista, movil) {
    const r = vista.recurso;
    const filas = est.app.filas[r];
    const detalle = buscar(lista, r, "detalle");
    const form = buscar(lista, r, "form");
    if (vista.pantalla === "lista") {
      const items = filas
        .map((f) => {
          const nuevo = est.app.nuevo === `${r}:${f.id}` ? " app-item--nuevo" : "";
          const etiqueta = e(texto(r, f));
          return detalle
            ? `<li><button type="button" class="app-item${nuevo}" data-app-ir="detalle" data-app-id="${f.id}" data-app-recurso="${r}">${etiqueta}${movil ? "<span>›</span>" : ""}</button></li>`
            : `<li><span class="app-item${nuevo}">${etiqueta}</span></li>`;
        })
        .join("");
      const agregar = form ? `<button type="button" class="app-boton" data-app-ir="form" data-app-recurso="${r}">Agregar</button>` : "";
      return `<div class="app-encabezado"><h4>${e(vista.titulo)}</h4>${agregar}</div>${filas.length ? `<ul class="app-lista">${items}</ul>` : "<p>Todavía no hay registros.</p>"}`;
    }
    if (vista.pantalla === "detalle") {
      const f = filas.find((x) => x.id === Number(est.app.id || 1)) || filas[0];
      if (!f) return "<p>No hay registros.</p>";
      const datos = campos(r)
        .map((c) => (movil ? `<p class="app-etiqueta">${e(c.titulo)}</p><p>${e(valor(c, f))}</p>` : `<dt>${e(c.titulo)}</dt><dd>${e(valor(c, f))}</dd>`))
        .join("");
      const editar = form ? `<button type="button" class="app-boton" data-app-ir="form" data-app-id="${f.id}" data-app-recurso="${r}">Editar</button>` : "";
      return `<h4>${e(vista.titulo)} ${f.id}</h4>${movil ? `<div>${datos}</div>` : `<dl class="app-dl">${datos}</dl>`}${editar}`;
    }
    // Formulario: crear, o editar si hay un id.
    const id = est.app.id ? Number(est.app.id) : null;
    const f = id ? filas.find((x) => x.id === id) : null;
    const controles = campos(r)
      .map((c) => {
        const actual = f ? f[c.nombre] : "";
        let control;
        if (c.tipo === "fk") {
          const opciones = est.app.filas[c.nombre] || [];
          control = movil
            ? `<div class="app-chips" data-app-chips="${c.nombre}">${opciones
                .map((o) => `<button type="button" class="app-chip${o.id === actual ? " app-chip--elegida" : ""}" data-app-chip="${o.id}">${e(texto(c.nombre, o))}</button>`)
                .join("")}<input type="hidden" name="${c.nombre}" value="${actual || ""}"></div>`
            : `<select name="${c.nombre}"><option value="">(sin elegir)</option>${opciones
                .map((o) => `<option value="${o.id}"${o.id === actual ? " selected" : ""}>${e(texto(c.nombre, o))}</option>`)
                .join("")}</select>`;
        } else if (c.tipo === "bool") {
          control = `<input type="checkbox" name="${c.nombre}"${actual ? " checked" : ""}>`;
        } else {
          const numero = ["int", "decimal", "float"].includes(c.tipo);
          control = `<input name="${c.nombre}" ${numero ? `inputmode="decimal"` : ""} value="${e(actual ?? "")}" autocomplete="off">`;
        }
        return `<label class="app-campo"><span>${e(c.titulo)}</span>${control}<small class="app-error" data-app-error="${c.nombre}"></small></label>`;
      })
      .join("");
    return `<h4>${f ? "Editar" : "Agregar"}: ${e(r)}</h4>
      <form class="app-form" data-app-form="${r}" data-app-id="${f ? f.id : ""}" novalidate>${controles}
        <div class="app-acciones"><button type="submit" class="app-boton app-boton--lleno">${f ? "Guardar cambios" : "Agregar"}</button></div></form>`;
  }

  function dibujarApp(contenedor, i, actual) {
    const lista = pantallas(i);
    if (!lista.length) return;
    const vista = actual || lista[lista.length - 1];
    est.app.vista = vista;
    const movil = vista.tipo === "movil";
    const menu = lista
      .filter((p) => p.pantalla !== "detalle" && !(p.deCrud && p.pantalla === "form"))
      .map((p) => `<button type="button" class="app-menu__link${p === vista ? " app-menu__link--actual" : ""}" data-app-pantalla="${lista.indexOf(p)}">${e(p.titulo)}</button>`)
      .join("");
    const url = vista.pantalla === "detalle" ? vista.url.replace(/\/\d+$/, `/${est.app.id || 1}`) : vista.url + (vista.pantalla === "form" && est.app.id && !vista.deCrud ? `/${est.app.id}` : "");
    const cuerpo = contenidoApp(vista, lista, movil);
    contenedor.innerHTML = movil
      ? `<div class="movil"><div class="movil__pantalla"><div class="movil__barra">${
          vista.pantalla === "lista" ? "" : `<button type="button" class="movil__volver" data-app-volver>‹</button>`
        }<b>${e(vista.titulo)}</b></div><div class="movil__contenido app-anima">${cuerpo}</div>
        <nav class="movil__tabs">${menu}</nav><div class="app-aviso" data-app-aviso hidden></div></div></div>`
      : `<div class="navegador navegador--app"><div class="navegador__barra"><span class="terminal__puntos" aria-hidden="true"><i></i><i></i><i></i></span><span class="navegador__url">localhost:5173${e(url)}</span></div>
        <div class="app"><nav class="app-menu"><span class="app-menu__marca">Mi tienda</span>${menu}</nav><div class="app-contenido app-anima">${cuerpo}</div></div>
        <div class="app-aviso" data-app-aviso hidden></div></div>`;
    contenedor.dataset.paso = i;
  }

  async function aviso(contenedor, metodo, url, estado) {
    const caja = contenedor.querySelector("[data-app-aviso]");
    if (!caja) return;
    caja.innerHTML = `<span class="metodo metodo--${metodo.toLowerCase()}">${metodo}</span> ${e(url)} <b class="estado-http estado-http--${String(estado)[0]}">${estado}</b>`;
    caja.hidden = false;
    caja.classList.remove("app-aviso--sale");
    void caja.offsetWidth;
    caja.classList.add("app-aviso--entra");
    await A.esperar(1600);
    caja.classList.add("app-aviso--sale");
  }

  async function enviarFormulario(contenedor, formulario) {
    const r = formulario.dataset.appForm;
    const id = formulario.dataset.appId ? Number(formulario.dataset.appId) : null;
    const datos = {};
    let errores = 0;
    formulario.querySelectorAll("[data-app-error]").forEach((x) => (x.textContent = ""));
    campos(r).forEach((c) => {
      const control = formulario.elements[c.nombre];
      const error = (texto) => {
        errores++;
        const lugar = formulario.querySelector(`[data-app-error="${c.nombre}"]`);
        lugar.textContent = texto;
        lugar.classList.remove("app-error--sacude");
        void lugar.offsetWidth;
        lugar.classList.add("app-error--sacude");
      };
      if (c.tipo === "bool") return (datos[c.nombre] = control.checked);
      const v = String(control.value).trim();
      if (c.tipo === "fk") return (datos[c.nombre] = v ? Number(v) : null);
      if (!v) return error("Este campo es obligatorio.");
      if (["int", "decimal", "float"].includes(c.tipo)) {
        const n = Number(v.replace(",", "."));
        if (Number.isNaN(n)) return error("Ingrese un número válido.");
        if (c.tipo === "int" && !Number.isInteger(n)) return error("Ingrese un número entero válido.");
        datos[c.nombre] = n;
      } else datos[c.nombre] = v;
    });
    const base = `/api/${plural(r)}/`;
    if (errores) return aviso(contenedor, id ? "PATCH" : "POST", id ? `${base}${id}/` : base, 400);
    const filas = est.app.filas[r];
    let nuevoId = id;
    if (id) Object.assign(filas.find((x) => x.id === id), datos);
    else {
      nuevoId = Math.max(0, ...filas.map((x) => x.id)) + 1;
      filas.push({ id: nuevoId, ...datos });
    }
    est.app.nuevo = `${r}:${nuevoId}`;
    aviso(contenedor, id ? "PATCH" : "POST", id ? `${base}${id}/` : base, id ? 200 : 201);
    await A.esperar(700);
    const lista = pantallas(Number(contenedor.dataset.paso));
    est.app.id = null;
    dibujarApp(contenedor, Number(contenedor.dataset.paso), buscar(lista, r, "lista") || est.app.vista);
  }

  // --- Las otras vistas: la API y la consola ---------------------------------------

  function apiHtml(pedidos) {
    return `<div class="api">${pedidos
      .map(
        (p, k) => `<div class="api-pedido" data-api="${k}">
        <div class="api-pedido__linea"><span class="metodo metodo--${p.metodo.toLowerCase()}">${p.metodo}</span><code>${e(p.url)}</code>
          <button type="button" class="app-boton" data-api-enviar="${k}">Enviar</button></div>
        ${p.cuerpo ? `<pre class="api-cuerpo"><code>${A.resaltar(p.cuerpo, "json")}</code></pre>` : ""}
        <div class="api-respuesta" hidden><p><b class="estado-http estado-http--${String(p.estado)[0]}">${p.estado}</b> ${e(
          { 200: "OK", 201: "Created", 400: "Bad Request", 405: "Method Not Allowed" }[p.estado] || "",
        )}</p><pre><code>${A.resaltar(p.respuesta, "json")}</code></pre></div></div>`,
      )
      .join("")}</div>`;
  }

  async function enviarPedido(caja) {
    const respuesta = caja.querySelector(".api-respuesta");
    respuesta.hidden = true;
    caja.classList.add("api-pedido--enviando");
    await A.esperar(650);
    caja.classList.remove("api-pedido--enviando");
    respuesta.hidden = false;
    respuesta.classList.remove("aparece");
    void respuesta.offsetWidth;
    respuesta.classList.add("aparece");
  }

  async function consola(pre, comando, salida, juego) {
    pre.innerHTML = "";
    const agregar = (html) => {
      pre.insertAdjacentHTML("beforeend", html);
      pre.scrollTop = pre.scrollHeight;
    };
    agregar(`<span class="t-tenue">C:\\Users\\alumno\\proyecto&gt;</span> `);
    const cmd = document.createElement("span");
    cmd.className = "t-comando";
    pre.appendChild(cmd);
    for (const letra of comando) {
      if (juego.cancelado) return;
      cmd.textContent += letra;
      await A.esperar(22);
    }
    agregar("\n");
    for (const linea of salida.split("\n")) {
      if (juego.cancelado) return;
      agregar(A.ansiAHtml(linea) + "\n");
      await A.esperar(linea.trim() ? 28 : 8);
    }
  }

  // --- Un paso --------------------------------------------------------------------

  function vistaAcumulada(i) {
    const pasos = est.armado.pasos.slice(0, i + 1);
    const conVista = pasos.filter((p) => p.vista);
    if (!conVista.length) return null;
    const ultima = conVista[conVista.length - 1].vista;
    if (ultima.tipo === "api") return { tipo: "api", pedidos: conVista.flatMap((p) => p.vista.pedidos) };
    return ultima;
  }

  function escena(i) {
    const p = est.armado.pasos[i];
    const total = est.armado.pasos.length;
    const ultimo = i === total - 1;
    const vista = p.vista || (ultimo ? vistaAcumulada(i) : null);
    const partes = [];
    partes.push(`<header class="escena__cabeza"><p class="escena__numero">Paso ${i + 1} de ${total}</p><h3>${e(p.titulo)}</h3><p>${e(p.texto)}</p></header>`);
    if (p.forma) {
      partes.push(`<div class="escena__forma"><p class="escena__rotulo">La forma general</p><code>${formaHtml(p.forma)}</code>
        <p class="escena__rotulo">Aplicada a este proyecto</p><code class="escena__aplicada">${ejemploHtml(p.forma, p.comando)}</code></div>`);
    }
    if (p.andamio) {
      partes.push(`<div class="terminal escena__terminal"><div class="terminal__barra"><span class="terminal__puntos" aria-hidden="true"><i></i><i></i><i></i></span>
        <button class="terminal__boton" type="button" data-copiar="${e(p.comando)}">Copiar</button></div><pre class="terminal__cuerpo" data-escena-terminal></pre></div>`);
      const estados = Object.fromEntries(p.archivos.map((a) => [a.ruta, a.estado]));
      const pestanas = p.archivos
        .map((a, k) => `<button type="button" role="tab" class="visor-pestana" data-armado-archivo="${k}" aria-selected="${k === 0}"><i class="estado estado--${a.estado}"></i>${e(a.ruta.split("/").pop())}</button>`)
        .join("");
      partes.push(`<div class="escena__codigo">
        <div class="escena__arbol"><p class="escena__rotulo">El proyecto en este paso</p>${arbol(p.proyecto, estados)}
          <ul class="leyenda"><li><i class="estado estado--nuevo"></i>nuevo</li><li><i class="estado estado--modificado"></i>modificado</li></ul></div>
        <div class="visor-codigo escena__visor">${p.archivos.length ? `<div class="visor-codigo__pestanas" role="tablist">${pestanas}</div>` : ""}
          <div class="visor-codigo__info"><code data-escena-ruta></code><span data-escena-desc></span></div>
          <pre class="codigo__cuerpo visor-codigo__cuerpo escena__cuerpo"><code data-escena-codigo></code></pre></div></div>`);
    } else {
      partes.push(A.comandoHtml(p.comando));
    }
    if (vista) {
      const titulo = { web: "Así se ve (probala: es una demostración)", movil: "Así se ve en el celular (probala)", api: "Probá la API", consola: "Así se usa (una sesión real)" }[vista.tipo];
      partes.push(`<div class="escena__vista"><p class="escena__rotulo">${e(titulo)}</p><div data-escena-vista></div></div>`);
    }
    const anterior = i > 0 ? `<button type="button" class="boton boton--borde" data-armado-paso="${i - 1}">← ${e(est.armado.pasos[i - 1].titulo)}</button>` : "<span></span>";
    const siguiente = i < total - 1 ? `<button type="button" class="boton" data-armado-paso="${i + 1}">${e(est.armado.pasos[i + 1].titulo)} →</button>` : "";
    partes.push(`<nav class="escena__nav">${anterior}${siguiente}</nav>`);
    return { html: partes.join(""), vista };
  }

  function mostrarArchivo(k) {
    const p = est.armado.pasos[est.paso];
    const a = p.archivos[k];
    const raiz = est.raiz;
    if (!a) return;
    raiz.querySelectorAll("[data-armado-archivo]").forEach((b) => b.setAttribute("aria-selected", String(Number(b.dataset.armadoArchivo) === k)));
    raiz.querySelectorAll(".aa-archivo").forEach((b) => b.classList.toggle("aa-archivo--actual", b.dataset.armadoRuta === a.ruta));
    const nuevas = a.agregadas.length;
    raiz.querySelector("[data-escena-ruta]").textContent = a.ruta;
    raiz.querySelector("[data-escena-desc]").textContent =
      a.estado === "modificado" ? `Ya existía: andamio le agregó ${nuevas} línea${nuevas === 1 ? "" : "s"} (resaltadas).` : a.descripcion || "Archivo nuevo.";
    const codigo = raiz.querySelector("[data-escena-codigo]");
    codigo.innerHTML = A.resaltar(a.contenido, a.lenguaje);
    const lineas = codigo.querySelectorAll(".l");
    let n = 0;
    a.agregadas.forEach((num) => {
      const l = lineas[num - 1];
      if (l) {
        l.classList.add("l--nueva");
        l.style.setProperty("--i", n++);
      }
    });
    const pre = codigo.parentElement;
    const primera = codigo.querySelector(".l--nueva");
    pre.scrollTop = primera ? Math.max(0, primera.offsetTop - 60) : 0;
  }

  function mostrarPaso(i, reproducir = true) {
    if (est.juego) est.juego.cancelado = true;
    est.paso = i;
    const raiz = est.raiz;
    raiz.querySelectorAll(".armado__chip").forEach((b) => {
      const k = Number(b.dataset.armadoPaso);
      b.setAttribute("aria-current", String(k === i));
      b.classList.toggle("armado__chip--hecho", k < i);
    });
    raiz.querySelector(".armado__progreso span").style.width = `${((i + 1) / est.armado.pasos.length) * 100}%`;
    const { html, vista } = escena(i);
    const lugar = raiz.querySelector("[data-escena]");
    lugar.innerHTML = html;
    lugar.classList.remove("escena--entra");
    void lugar.offsetWidth;
    lugar.classList.add("escena--entra");
    if (est.armado.pasos[i].archivos && est.armado.pasos[i].archivos.length) mostrarArchivo(0);
    est.vista = vista;
    if (vista && (vista.tipo === "web" || vista.tipo === "movil")) {
      est.app.id = vista.pantalla === "detalle" ? 1 : null;
      dibujarApp(lugar.querySelector("[data-escena-vista]"), i, est.armado.pasos[i].vista ? undefined : pantallas(i)[0]);
    } else if (vista && vista.tipo === "api") {
      lugar.querySelector("[data-escena-vista]").innerHTML = apiHtml(vista.pedidos);
    } else if (vista && vista.tipo === "consola") {
      lugar.querySelector("[data-escena-vista]").innerHTML = `<div class="terminal"><div class="terminal__barra"><span class="terminal__puntos" aria-hidden="true"><i></i><i></i><i></i></span>
        <button class="terminal__boton" type="button" data-consola-otra-vez>Ver de nuevo</button></div><pre class="terminal__cuerpo escena__sesion" data-escena-sesion></pre></div>`;
    }
    return reproducir ? reproducirPaso() : Promise.resolve();
  }

  /** La animación de un paso: el comando, su consola, los archivos y la vista. */
  async function reproducirPaso() {
    const juego = { cancelado: false };
    est.juego = juego;
    const p = est.armado.pasos[est.paso];
    const lugar = est.raiz.querySelector("[data-escena]");
    const term = lugar.querySelector("[data-escena-terminal]");
    lugar.classList.remove("escena--codigo", "escena--vista");
    if (term) await consola(term, p.comando, p.salida, juego);
    else if (p.andamio === false) await A.esperar(300);
    if (juego.cancelado) return;
    lugar.classList.add("escena--codigo");
    await A.esperar(p.archivos && p.archivos.length ? 900 : 100);
    if (juego.cancelado) return;
    lugar.classList.add("escena--vista");
    const v = est.vista;
    if (v && v.tipo === "consola") {
      await consola(lugar.querySelector("[data-escena-sesion]"), v.comando, v.salida, juego);
    } else if (v && v.tipo === "api") {
      for (const caja of lugar.querySelectorAll(".api-pedido")) {
        if (juego.cancelado) return;
        await enviarPedido(caja);
        await A.esperar(350);
      }
    }
  }

  async function reproducirTodo(boton) {
    const juego = { cancelado: false };
    est.todo = juego;
    boton.textContent = "■ Detener";
    for (let i = est.paso; i < est.armado.pasos.length; i++) {
      if (juego.cancelado) break;
      est.raiz.querySelector(".armado__escena").scrollIntoView({ block: "start", behavior: A.sinMovimiento ? "auto" : "smooth" });
      await mostrarPaso(i);
      if (juego.cancelado || est.juego.cancelado) break;
      await A.esperar(2200);
    }
    est.todo = null;
    boton.textContent = "▶ Todo el recorrido";
  }

  // --- El panel --------------------------------------------------------------------

  function panel(armado) {
    const chips = armado.pasos
      .map((p, i) => `<li><button type="button" class="armado__chip" data-armado-paso="${i}"><b>${i + 1}</b><span>${e(p.titulo)}</span></button></li>`)
      .join("");
    return `
      <p class="leccion__intro"><b>${e(armado.titulo)}.</b> ${e(armado.intro)}</p>
      <div class="bloque"><h3>Todos los comandos: primero la forma general, después un ejemplo</h3>
        <p class="bajada">Lo que va entre <span class="ph">&lt; &gt;</span> lo elegís vos; abajo, el mismo comando con valores de ejemplo (pasá el mouse por un valor para ver qué ocupa).</p>
        ${formasHtml(armado)}</div>
      <div class="bloque armado" data-armado>
        <h3>Paso a paso: armá el proyecto</h3>
        <p class="bajada">Cada comando se ejecutó de verdad para armar esta guía. Mirá la consola, cómo crece el proyecto, el código que se agrega (resaltado) y cómo se ve.</p>
        <div class="armado__controles">
          <div class="armado__progreso" aria-hidden="true"><span></span></div>
          <button type="button" class="boton boton--borde" data-armado-otra-vez>↻ Repetir el paso</button>
          <button type="button" class="boton" data-armado-todo>▶ Todo el recorrido</button>
        </div>
        <ol class="armado__chips">${chips}</ol>
        <div class="armado__escena" data-escena aria-live="polite"></div>
      </div>`;
  }

  /** Engancha los eventos del panel (una sola vez) y muestra el primer paso. */
  function iniciar(raiz, armado) {
    est = { armado, raiz, paso: 0, juego: null, app: null };
    est.app = nuevaApp();
    raiz.addEventListener("click", (evento) => {
      const b = evento.target.closest("button");
      if (!b || !raiz.contains(b)) return;
      if (b.dataset.armadoPaso !== undefined) {
        if (est.todo) est.todo.cancelado = true;
        const ir = Number(b.dataset.armadoPaso);
        if (b.classList.contains("armado-ir") || b.closest(".escena__nav")) raiz.querySelector(".armado__escena").scrollIntoView({ block: "start" });
        mostrarPaso(ir);
      } else if (b.dataset.armadoArchivo !== undefined) {
        mostrarArchivo(Number(b.dataset.armadoArchivo));
      } else if (b.dataset.armadoRuta) {
        const k = est.armado.pasos[est.paso].archivos.findIndex((a) => a.ruta === b.dataset.armadoRuta);
        if (k >= 0) mostrarArchivo(k);
        else {
          raiz.querySelector("[data-escena-ruta]").textContent = b.dataset.armadoRuta;
          raiz.querySelector("[data-escena-desc]").textContent = "";
          raiz.querySelector("[data-escena-codigo]").innerHTML = '<span class="l t-nota">Este archivo no cambia en este paso.</span>';
        }
      } else if (b.hasAttribute("data-armado-otra-vez")) {
        mostrarPaso(est.paso);
      } else if (b.hasAttribute("data-armado-todo")) {
        if (est.todo) {
          est.todo.cancelado = true;
          if (est.juego) est.juego.cancelado = true;
        } else reproducirTodo(b);
      } else if (b.hasAttribute("data-consola-otra-vez")) {
        const v = est.vista;
        consola(raiz.querySelector("[data-escena-sesion]"), v.comando, v.salida, (est.juego = { cancelado: false }));
      } else if (b.dataset.apiEnviar !== undefined) {
        enviarPedido(b.closest(".api-pedido"));
      } else if (b.dataset.appPantalla !== undefined) {
        const lugar = raiz.querySelector("[data-escena-vista]");
        est.app.id = null;
        dibujarApp(lugar, Number(lugar.dataset.paso), pantallas(Number(lugar.dataset.paso))[Number(b.dataset.appPantalla)]);
      } else if (b.dataset.appIr) {
        const lugar = raiz.querySelector("[data-escena-vista]");
        const lista = pantallas(Number(lugar.dataset.paso));
        est.app.id = b.dataset.appId || null;
        dibujarApp(lugar, Number(lugar.dataset.paso), buscar(lista, b.dataset.appRecurso, b.dataset.appIr));
      } else if (b.hasAttribute("data-app-volver")) {
        const lugar = raiz.querySelector("[data-escena-vista]");
        est.app.id = null;
        const lista = pantallas(Number(lugar.dataset.paso));
        dibujarApp(lugar, Number(lugar.dataset.paso), buscar(lista, est.app.vista.recurso, "lista") || lista[0]);
      } else if (b.dataset.appChip) {
        const chips = b.closest("[data-app-chips]");
        chips.querySelectorAll(".app-chip").forEach((c) => c.classList.toggle("app-chip--elegida", c === b));
        chips.querySelector("input").value = b.dataset.appChip;
      }
    });
    raiz.addEventListener("submit", (evento) => {
      const formulario = evento.target.closest("[data-app-form]");
      if (!formulario) return;
      evento.preventDefault();
      enviarFormulario(raiz.querySelector("[data-escena-vista]"), formulario);
    });
    mostrarPaso(0, false);
  }

  /** Al abrir la pestaña: reproduce el paso que se está viendo. */
  function alMostrar() {
    if (est && !est.reproducido) {
      est.reproducido = true;
      mostrarPaso(est.paso);
    }
  }

  window.AndamioArmado = { panel, iniciar, alMostrar, alinear };
})();
