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
    await escribir(comando, "andamio", 90);
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

  // --- Tarjetas de tecnologías --------------------------------------------------------

  function tarjetas() {
    const lista = document.getElementById("lista-tecnologias");
    lista.innerHTML = datos.tecnologias
      .map((t) => {
        const variante = t.variantes[0];
        const lenguajes = t.variantes.length > 1 ? `<p><b>${t.variantes.map((v) => e(v.nombre)).join(" o ")}</b></p>` : "";
        return `<a class="tecnologia" href="${t.clave}.html">
          <h3>${e(t.titulo)}</h3>
          <p>${e(t.resumen)}</p>
          ${lenguajes}
          <ul class="tecnologia__piezas" aria-label="Piezas">${variante.piezas.map((p) => `<li>${e(p.clave)}</li>`).join("")}</ul>
          <span class="tecnologia__ir">Ver la guía →</span>
        </a>`;
      })
      .join("");
  }

  // --- Inicio -------------------------------------------------------------------------

  document.querySelectorAll("[data-version]").forEach((el) => (el.textContent = A.version));
  document.querySelectorAll("[data-instalar]").forEach((el) => {
    const comando = `${el.dataset.instalar} -m pip install ${A.urlWhl}`;
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
