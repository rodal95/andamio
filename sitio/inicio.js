/* andamio · sitio: portada (index.html). */
(function () {
  "use strict";

  const A = window.Andamio;
  const e = A.escapar;
  const datos = A.datos;

  // --- Terminal animada con una sesión real del menú --------------------------------

  const terminal = document.getElementById("terminal-menu");
  let reproduccion = { cancelada: false };

  async function escribir(destino, texto, ms) {
    for (const letra of texto) {
      destino.textContent += letra;
      await A.esperar(ms);
    }
  }

  async function reproducir() {
    reproduccion.cancelada = true;
    const actual = { cancelada: false };
    reproduccion = actual;
    terminal.innerHTML = "";
    const cursor = document.createElement("span");
    cursor.className = "cursor";
    terminal.appendChild(cursor);
    const agregar = (html) => {
      cursor.insertAdjacentHTML("beforebegin", html);
      terminal.scrollTop = terminal.scrollHeight;
    };
    agregar('<span class="t-tenue">C:\\Users\\alumno\\mi-api&gt;</span> ');
    const comando = document.createElement("span");
    comando.className = "t-comando";
    terminal.insertBefore(comando, cursor);
    await A.esperar(500);
    await escribir(comando, "python -m andamio", 70);
    await A.esperar(300);
    agregar("\n");
    for (const evento of datos.menu) {
      if (actual.cancelada) return;
      if (evento.tipo === "salida") {
        const lineas = evento.texto.split("\n");
        for (let i = 0; i < lineas.length; i++) {
          agregar(A.ansiAHtml(lineas[i]) + (i < lineas.length - 1 ? "\n" : ""));
          await A.esperar(45);
          if (actual.cancelada) return;
        }
      } else {
        agregar(A.ansiAHtml(evento.pregunta));
        await A.esperar(450);
        const respuesta = document.createElement("span");
        respuesta.className = "t-respuesta";
        terminal.insertBefore(respuesta, cursor);
        await escribir(respuesta, evento.respuesta, 85);
        if (!evento.respuesta) {
          respuesta.className = "t-tenue";
          respuesta.textContent = "↵";
        }
        await A.esperar(250);
        agregar("\n");
      }
    }
  }

  // --- Tarjetas de tecnologías, agrupadas por lo que se construye ----------------------

  const GRUPOS = [
    { titulo: "La API (el servidor)", texto: "Guarda los datos y los entrega en /api/. La usan las webs y las apps.", claves: ["django", "fastapi", "express"] },
    { titulo: "La interfaz (web y celular)", texto: "Lo que ve el usuario. Pide los datos a una API.", claves: ["web", "react", "vue", "next", "react-native"] },
    { titulo: "Todo en uno (full stack)", texto: "La interfaz y la API en el mismo proyecto.", claves: ["django-web", "next-fullstack", "reflex"] },
    { titulo: "Para empezar", texto: "Un programa de consola con base de datos: solo Python.", claves: ["python"] },
  ];

  function tarjeta(t) {
    const variante = t.variantes[0];
    const lenguajes = t.variantes.length > 1 ? `<p><b>${t.variantes.map((v) => e(v.nombre)).join(" o ")}</b></p>` : "";
    return `<a class="tecnologia" href="${t.clave}.html">
          <h4>${e(t.titulo)}</h4>
          <p>${e(t.resumen)}</p>
          ${lenguajes}
          <ul class="tecnologia__piezas" aria-label="Piezas">${variante.piezas.map((p) => `<li>${e(p.clave)}</li>`).join("")}</ul>
          <span class="tecnologia__ir">Ver la guía paso a paso →</span>
        </a>`;
  }

  function tarjetas() {
    const porClave = Object.fromEntries(datos.tecnologias.map((t) => [t.clave, t]));
    const usadas = new Set(GRUPOS.flatMap((g) => g.claves));
    // Una tecnología nueva que nadie agrupó igual se muestra (al final).
    const otras = datos.tecnologias.filter((t) => !usadas.has(t.clave)).map((t) => t.clave);
    const grupos = otras.length ? [...GRUPOS, { titulo: "Otras", texto: "", claves: otras }] : GRUPOS;
    document.getElementById("lista-tecnologias").innerHTML = grupos
      .map(
        (g) => `<div class="grupo-tecnologias">
          <h3>${e(g.titulo)}</h3>${g.texto ? `<p>${e(g.texto)}</p>` : ""}
          <div class="tecnologias">${g.claves.filter((c) => porClave[c]).map((c) => tarjeta(porClave[c])).join("")}</div>
        </div>`,
      )
      .join("");
  }

  // --- Inicio -------------------------------------------------------------------------

  document.querySelectorAll("[data-version]").forEach((el) => (el.textContent = A.version));
  document.querySelectorAll("[data-instalar]").forEach((el) => {
    const comando = el.dataset.instalar === "pipx" ? `pipx install ${A.urlWhl}` : `${el.dataset.instalar} -m pip install ${A.urlWhl}`;
    el.outerHTML = A.comandoHtml(comando);
  });

  A.pestanas(document.getElementById("pestanas-instalar"), (boton) => {
    document.querySelectorAll(".instalar__panel").forEach((panel) => {
      panel.hidden = panel.id !== boton.dataset.panel;
    });
  });

  if (!datos) {
    terminal.textContent = "Faltan los datos de la página. Generalos con: python scripts/sitio.py";
    return;
  }
  tarjetas();
  reproducir();
  document.getElementById("repetir-menu").addEventListener("click", reproducir);
})();
