/* andamio · sitio: guía de una tecnología (python, django, fastapi, express, react y react-native .html). */
(function () {
  "use strict";

  const A = window.Andamio;
  const clave = document.body.dataset.tecnologia;
  const main = document.getElementById("contenido");

  // Capturas reales de los proyectos generados funcionando (scripts/capturas_sitio.py).
  const CAPTURAS = {
    django: {
      marcha: [
        { src: "img/django-swagger.jpg", url: "http://127.0.0.1:8000/api/docs/", titulo: "Documentación interactiva (Swagger)", texto: "Ahí podés probar cada operación de la API desde el navegador." },
      ],
      piezas: {
        recurso: [
          { src: "img/django-api.jpg", url: "http://127.0.0.1:8000/api/productos/", titulo: "La API del recurso", texto: "La lista de productos en JSON, lista para que la use React o React Native." },
          { src: "img/django-admin.jpg", url: "http://127.0.0.1:8000/admin/productos/producto/", titulo: "El panel de administración", texto: "Columnas, búsqueda y alta de productos sin escribir código." },
        ],
      },
    },
    fastapi: {
      marcha: [
        { src: "img/fastapi-swagger.jpg", url: "http://127.0.0.1:8000/docs", titulo: "Documentación interactiva (Swagger)", texto: "Ahí podés probar cada operación de la API desde el navegador." },
      ],
      piezas: {
        recurso: [
          { src: "img/fastapi-api.jpg", url: "http://127.0.0.1:8000/docs", titulo: "Probar el recurso en Swagger", texto: "GET /api/productos/ → Try it out → Execute: la lista en JSON, con la misma forma que la API de Django (los precios como número)." },
        ],
      },
    },
    express: {
      marcha: [
        { src: "img/express-swagger.jpg", url: "http://localhost:8000/docs", titulo: "Documentación interactiva (Swagger)", texto: "Ahí podés probar cada operación de la API desde el navegador, sin internet." },
      ],
      piezas: {
        recurso: [
          { src: "img/express-api.jpg", url: "http://localhost:8000/docs", titulo: "Probar el recurso en Swagger", texto: "GET /api/productos/ → Try it out → Execute: la lista en JSON, con la misma forma que las APIs de Django y FastAPI." },
        ],
      },
    },
    react: {
      marcha: [{ src: "img/react-inicio.jpg", url: "http://localhost:5173", titulo: "La app recién creada", texto: "El menú y la página de inicio, al abrir el navegador después de npm run dev." }],
      piezas: {
        crud: [
          { src: "img/react-crud-lista.jpg", url: "http://localhost:5173/productos", titulo: "La lista", texto: "Los productos llegan de la API (Django, FastAPI o Express). Cada uno enlaza a su detalle." },
          { src: "img/react-crud-detalle.jpg", url: "http://localhost:5173/productos/1", titulo: "El detalle", texto: "Con los botones Editar y Eliminar." },
          { src: "img/react-crud-formulario.jpg", url: "http://localhost:5173/productos/nuevo", titulo: "El formulario", texto: "Si la API rechaza un dato, el error aparece debajo del campo." },
        ],
      },
    },
    "react-native": {
      marcha: [{ src: "img/react-native-inicio.jpg", telefono: true, titulo: "La app recién creada", texto: "La pantalla de inicio, en el navegador o en tu celular con Expo Go." }],
      piezas: {
        pantalla: [{ src: "img/react-native-detalle.jpg", telefono: true, titulo: "La pantalla generada", texto: "Con su título en la barra superior y el botón para volver." }],
      },
      final: {
        src: "img/react-native-final.jpg",
        telefono: true,
        titulo: "Componente y servicio trabajando juntos",
        texto: "La pantalla de inicio lista los productos de la API con el componente Tarjeta. Esto es lo que escribiste vos:",
        ejemplos: [["react-native-index.tsx", "app/index.tsx"]],
      },
    },
  };

  const PROBLEMAS = {
    python: [
      ["ModuleNotFoundError: No module named 'entidades'", "Ejecutá python main.py desde la carpeta del proyecto (donde está main.py)."],
      ["Agregué un campo y no aparece en la tabla", "CREATE TABLE IF NOT EXISTS no modifica una tabla que ya existe. Mientras desarrollás, borrá datos.db (se pierden los datos de prueba) y volvé a ejecutar."],
      ["¿Dónde se guardan los datos?", "En el archivo datos.db, que se crea solo la primera vez. Está en .gitignore para no subirlo a git."],
    ],
    django: [
      ["No module named 'django'", "No está activado el entorno virtual. Ejecutá .venv\\Scripts\\activate (Windows) o source .venv/bin/activate, y pip install -r requirements.txt."],
      ["Falta SECRET_KEY", "Falta el archivo .env (por ejemplo, al clonar el repo de un compañero). Copiá .env.example con el nombre .env."],
      ["no such table: productos_producto", "Faltan las migraciones: python manage.py makemigrations productos y python manage.py migrate (o generá el recurso con --migrar)."],
      ["React no puede leer la API (error de CORS)", "La dirección de la web tiene que estar en CORS_ALLOWED_ORIGINS del .env (ya vienen localhost:5173 y localhost:8081)."],
      ["Invalid HTTP_HOST header / 400 desde el celular", "Agregá la IP de tu PC a ALLOWED_HOSTS en el .env y ejecutá python manage.py runserver 0.0.0.0:8000."],
    ],
    fastapi: [
      ["No module named 'fastapi'", "No está activado el entorno virtual. Ejecutá .venv\\Scripts\\activate (Windows) o source .venv/bin/activate, y pip install -r requirements.txt."],
      ["Agregué un campo al modelo y la tabla no lo tiene", "No hay migraciones: las tablas se crean al arrancar, pero no se modifican. Mientras desarrollás, borrá datos.db (se pierden los datos de prueba) y volvé a arrancar."],
      ["React no puede leer la API (error de CORS)", "La dirección de la web tiene que estar en CORS_ALLOWED_ORIGINS del .env (ya vienen localhost:5173 y localhost:8081)."],
      ["Desde el celular no conecta", "Arrancá la API escuchando en la red: python -m uvicorn app.main:app --reload --host 0.0.0.0, y poné la IP de tu PC en la app."],
      ["La hora vuelve distinta de la que mandé", "Sin zona horaria se toma como hora local (ZONA_HORARIA del .env, por defecto Argentina) y vuelve con su zona: 10:30 sale como 10:30:00-03:00."],
    ],
    express: [
      ["npm install falla", "Revisá la versión de Node con node --version: Express con Prisma necesita 22.12 o más nueva."],
      ["The table `main.productos` does not exist", "Falta la migración: npx prisma migrate dev --name productos (o generá el recurso con --migrar)."],
      ["Cambié prisma/schema.prisma y la API no lo ve", "Creá una migración (npx prisma migrate dev --name <qué cambió>) y volvé a ejecutar npm run dev, que genera el cliente de Prisma de nuevo."],
      ["React no puede leer la API (error de CORS)", "La dirección de la web tiene que estar en CORS_ALLOWED_ORIGINS del .env (ya vienen localhost:5173 y localhost:8081)."],
      ["EADDRINUSE: el puerto 8000 está ocupado", "Ya hay otra API andando en el 8000 (quizás Django o FastAPI). Cerrala, o cambiá PORT en el .env (y la dirección en la app)."],
    ],
    react: [
      ["npm install falla", "Revisá la versión de Node con node --version: necesitás 20.19 o más nueva."],
      ["El servicio no trae datos", "La API (Django, FastAPI o Express) tiene que estar andando y VITE_API_URL del .env tiene que apuntar a ella."],
      ["Cambié el .env y no toma el valor nuevo", "Cortá npm run dev con Ctrl+C y volvé a ejecutarlo: el .env se lee al arrancar."],
      ["Error 400 al crear", "Los campos del servicio no coinciden con los del recurso de la API: el error dice qué campo falta o está mal."],
      ["Mi proyecto lo creé con npm create vite", "andamio lo reconoce igual: si tiene tsconfig.json genera TypeScript; si no, JavaScript."],
    ],
    "react-native": [
      ["Network request failed", "En el emulador de Android tu PC es 10.0.2.2 (ya viene en el .env). En un celular real, poné la IP de tu PC en EXPO_PUBLIC_API_URL y hacé que la API escuche en la red: python manage.py runserver 0.0.0.0:8000 (Django) o python -m uvicorn app.main:app --host 0.0.0.0 (FastAPI)."],
      ["Cambié el .env y no toma el valor nuevo", "Cortá Expo y ejecutá npx expo start -c (la -c borra la caché)."],
      ["npm install falla", "Expo SDK 58 necesita Node 22.13 o más nuevo: revisalo con node --version."],
      ["La pantalla nueva no aparece", "Con Expo Router el nombre del archivo es la ruta: app/productos/detalle-producto.tsx se abre con router.push('/productos/detalle-producto')."],
    ],
  };

  const tecnologia = A.datos && A.datos.tecnologias.find((t) => t.clave === clave);
  if (!tecnologia) {
    main.innerHTML = '<div class="contenedor"><p class="aviso-caja">Faltan los datos de la página. Generalos con: python scripts/sitio.py</p></div>';
    return;
  }

  const parametros = new URLSearchParams(location.search);
  let variante = tecnologia.variantes.find((v) => v.clave === parametros.get("v")) || tecnologia.variantes[0];
  const capturas = CAPTURAS[clave] || {};

  // --- Piezas de HTML -------------------------------------------------------------

  const e = A.escapar;

  function captura(c) {
    const imagen = `<a href="${c.src}" target="_blank" rel="noopener" title="Ver en tamaño completo"><img src="${c.src}" alt="${e(c.titulo)}" loading="lazy" width="${c.telefono ? 390 : 1200}" height="${c.telefono ? 760 : 700}"></a>`;
    const marco = c.telefono
      ? `<div class="telefono">${imagen}</div>`
      : `<div class="navegador"><div class="navegador__barra"><span class="terminal__puntos" aria-hidden="true"><i></i><i></i><i></i></span><span class="navegador__url">${e(c.url || "")}</span></div>${imagen}</div>`;
    return `<figure class="captura">${marco}<figcaption><b>${e(c.titulo)}.</b> ${e(c.texto || "")}</figcaption></figure>`;
  }

  function listaArchivos(rutas, origen, compacta = false) {
    return `<ul class="archivos${compacta ? " archivos--compactos" : ""}">${rutas
      .map((item) => {
        const ruta = typeof item === "string" ? item : item.ruta;
        const archivo = origen.find((a) => a.ruta === ruta) || { estado: "nuevo" };
        const desc = typeof item === "string" ? archivo.descripcion : item.que ? `Se agrega: ${item.que}.` : archivo.descripcion;
        const estado = typeof item === "string" ? archivo.estado === "proyecto" ? "proyecto" : "nuevo" : "modificado";
        // Una carpeta vacía (con .gitkeep) se muestra como carpeta.
        const visible = ruta.endsWith(".gitkeep") ? ruta.slice(0, -".gitkeep".length) : ruta;
        return `<li><button type="button" data-archivo="${e(ruta)}" data-origen="${origen === variante.archivos_crear ? "crear" : "final"}">
          <i class="estado estado--${estado}"></i><span class="archivos__ruta">${e(visible)}</span><span class="archivos__ver">ver código</span>
          <span class="archivos__desc">${e(desc || "")}</span></button></li>`;
      })
      .join("")}</ul>`;
  }

  function seccion(id, numero, titulo, contenido, bajada = "") {
    const marca = numero ? `<span class="paso__numero">${numero}</span>` : "";
    return `<section class="paso-guia" id="${id}"><div class="contenedor">
      <div class="paso-guia__titulo">${marca}<h2>${titulo}</h2></div>
      ${bajada ? `<p class="bajada">${bajada}</p>` : ""}${contenido}</div></section>`;
  }

  // --- Secciones -----------------------------------------------------------------

  function portada() {
    const selector = tecnologia.variantes.length > 1
      ? `<div class="variante"><span class="variante__etiqueta">Lenguaje:</span>
          <div class="segmentado" role="group" aria-label="Lenguaje">${tecnologia.variantes
            .map((v) => `<button type="button" data-variante="${v.clave}" aria-pressed="${v.clave === variante.clave}">${e(v.nombre)}</button>`)
            .join("")}</div>
          <span class="variante__nota">Cambia los comandos, los archivos y el código de toda la guía.</span></div>`
      : "";
    const indice = [
      ["instalar", "1", "Instalá andamio"],
      ["crear", "2", "Creá el proyecto"],
      ["marcha", "3", "Ponelo en marcha"],
      ["piezas", "4", "Generá piezas"],
      ["completo", "✓", "Proyecto completo"],
      ["comandos", "⌘", "Comandos"],
      ["problemas", "?", "Problemas comunes"],
    ];
    return `<section class="guia-portada"><div class="contenedor">
      <p class="migas"><a href="index.html">andamio</a> / guía</p>
      <h1>andamio con ${e(tecnologia.titulo)}</h1>
      <p class="guia-portada__resumen">${e(tecnologia.resumen)}</p>
      <ul class="requisitos" aria-label="Qué necesitás">${tecnologia.requisitos.map((r) => `<li>${e(r)}</li>`).join("")}</ul>
      ${selector}
      <ol class="indice">${indice.map(([id, n, t]) => `<li><a href="#${id}"><b>${n}</b>${t}</a></li>`).join("")}</ol>
    </div></section>`;
  }

  function instalar() {
    const contenido = `
      ${A.comandoHtml(`python -m pip install ${A.urlWhl}`)}
      <p class="bajada">Para comprobar que quedó instalado:</p>
      ${A.comandoHtml("python -m andamio --version")}
      <p class="nota">andamio es un programa de Python: por eso todos los comandos de esta guía empiezan con
        <code>python -m andamio</code>, que funciona en cualquier PC. ¿Sin permisos o sin internet? Mirá
        <a href="index.html#instalar">las otras formas de instalarlo</a>.</p>`;
    return seccion("instalar", 1, "Instalá andamio", contenido, "Una sola vez en la PC. En Windows, en CMD o PowerShell (en Linux o Mac, con python3):");
  }

  function crear() {
    const archivos = variante.archivos_crear.map((a) => a.ruta);
    const contenido = `
      ${A.comandoHtml(variante.crear.comando, "comando--grande")}
      <div class="dos-columnas">
        <div>
          <span class="etiqueta-chica">Lo que muestra la terminal</span>
          <pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(variante.crear.comando, variante.crear.salida)}</pre>
        </div>
        <div>
          <span class="etiqueta-chica">Qué crea y para qué sirve cada archivo</span>
          ${listaArchivos(archivos, variante.archivos_crear, true)}
        </div>
      </div>`;
    return seccion(
      "crear",
      2,
      "Creá el proyecto",
      contenido,
      "En la carpeta donde guardás tus trabajos. andamio crea la carpeta del proyecto con todo lo necesario para ejecutarlo.",
    );
  }

  function marcha() {
    const descripciones = Object.fromEntries(tecnologia.comandos_proyecto.map((c) => [c.comando, c.descripcion]));
    const pasos = variante.pasos_proyecto
      .map((paso) => {
        if (paso.startsWith("# ")) return `<li><p>${e(paso.slice(2))}</p></li>`;
        if (/^https?:/.test(paso)) return `<li><span class="enlace-navegador">Abrí en el navegador: ${e(paso)}</span></li>`;
        const desc = paso.startsWith("cd ") ? "Entrá a la carpeta del proyecto." : descripciones[paso] || "";
        return `<li>${A.comandoHtml(paso)}${desc ? `<p>${e(desc)}</p>` : ""}</li>`;
      })
      .join("");
    let vista = "";
    if (tecnologia.ejecucion) {
      vista = `<span class="etiqueta-chica">Así se ve la aplicación (después de generar una entidad)</span>
        <pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(tecnologia.ejecucion.comando, tecnologia.ejecucion.salida)}</pre>`;
    } else if (capturas.marcha) {
      vista = `<span class="etiqueta-chica">Así se ve</span><div class="capturas">${capturas.marcha.map(captura).join("")}</div>`;
    }
    const contenido = `<div class="dos-columnas"><div><ol class="pasos-marcha">${pasos}</ol></div><div>${vista}</div></div>`;
    return seccion("marcha", 3, "Ponelo en marcha", contenido, "Son los mismos pasos que te muestra andamio al terminar de crear el proyecto.");
  }

  function pieza(p) {
    const capturasPieza = (capturas.piezas || {})[p.clave] || [];
    const modificados = p.modificados.length
      ? `<span class="etiqueta-chica">Qué modifica</span>${listaArchivos(p.modificados, variante.archivos, true)}`
      : "";
    return `<article class="pieza" id="pieza-${p.clave}">
      <div class="pieza__encabezado"><h3>${e(p.titulo)}</h3><span class="pieza__clave">andamio nuevo ${e(p.clave)}</span></div>
      <p class="pieza__explicacion">${e(p.explicacion)}</p>
      ${A.comandoHtml(p.comando)}
      <div class="dos-columnas">
        <div>
          <span class="etiqueta-chica">Qué crea</span>
          ${listaArchivos(p.creados, variante.archivos, true)}
          ${modificados}
        </div>
        <div>
          <span class="etiqueta-chica">Cómo se usa</span>
          ${A.codigoHtml(p.uso, p.uso_lenguaje)}
          <details><summary>Ver lo que muestra la terminal</summary>
            <pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(p.comando, p.salida)}</pre></details>
        </div>
      </div>
      ${capturasPieza.length ? `<span class="etiqueta-chica">Así se ve</span><div class="capturas">${capturasPieza.map(captura).join("")}</div>` : ""}
    </article>`;
  }

  function piezas() {
    const atajos = variante.piezas.map((p) => `<li><a href="#pieza-${p.clave}"><b>${e(p.titulo[0])}</b>${e(p.titulo)}</a></li>`).join("");
    const contenido = `<ol class="indice">${atajos}</ol>${variante.piezas.map(pieza).join("")}`;
    return seccion(
      "piezas",
      4,
      "Generá piezas",
      contenido,
      "Adentro de la carpeta del proyecto (o de cualquier subcarpeta). andamio detecta el tipo de proyecto y genera el código que corresponde. Tocá un archivo para ver su código.",
    );
  }

  function completo() {
    let final = "";
    if (capturas.final) {
      const f = capturas.final;
      const codigos = f.ejemplos
        .map(([archivo, ruta]) => {
          const lenguaje = archivo.endsWith(".css") ? "css" : "ts";
          return `<span class="etiqueta-chica">${e(ruta)}</span>${A.codigoHtml(A.datos.ejemplos[archivo] || "", lenguaje, true)}`;
        })
        .join("");
      const notaJs = variante.clave === "js" ? '<p class="nota">En JavaScript es igual, sin los tipos (por ejemplo, <code>useState([])</code> en lugar de <code>useState&lt;Producto[]&gt;([])</code>).</p>' : "";
      final = `<h3 class="titulo-final">Así queda funcionando</h3>
        <div class="dos-columnas"><div>${captura(f)}</div><div>${codigos}${notaJs}</div></div>`;
    }
    const contenido = `
      <div class="explorador">
        <div class="explorador__arbol">
          <p class="explorador__titulo">${e(variante.crear.comando.split(" ")[3])}/</p>
          <ul class="arbol" data-arbol>${A.arbolHtml(A.armarArbol(variante.archivos))}</ul>
          <ul class="leyenda" aria-label="Referencias">
            <li><i class="estado estado--nuevo"></i>lo agregó una pieza</li>
            <li><i class="estado estado--modificado"></i>modificado</li>
            <li><i class="estado estado--proyecto"></i>del proyecto</li>
          </ul>
        </div>
        <div class="codigo">
          <div class="codigo__barra"><span class="codigo__nombre" data-codigo-nombre></span>
            <button class="terminal__boton" type="button" data-codigo-copiar>Copiar</button></div>
          <p class="codigo__descripcion" data-codigo-desc></p>
          <pre class="codigo__cuerpo"><code data-codigo></code></pre>
        </div>
      </div>
      ${final}`;
    return `<section class="paso-guia seccion--oscura" id="completo"><div class="contenedor">
      <div class="paso-guia__titulo"><span class="paso__numero">✓</span><h2>El proyecto completo</h2></div>
      <p class="bajada">Así queda el proyecto después de generar todas las piezas de esta guía. Recorré los archivos.</p>
      ${contenido}</div></section>`;
  }

  function tablaComandos(comandos) {
    return `<table class="tabla-comandos"><thead><tr><th>Comando</th><th>Para qué sirve</th></tr></thead><tbody>${comandos
      .map((c) => `<tr><td><code>${e(c.comando)}</code><button type="button" class="copiar-chico" data-copiar="${e(c.comando)}">Copiar</button></td><td>${e(c.descripcion)}</td></tr>`)
      .join("")}</tbody></table>`;
  }

  function comandos() {
    const tipos = Object.keys(tecnologia.tipos).length
      ? `<h3 id="tipos">Tipos de campo</h3><p class="bajada">Los campos se escriben <code>nombre:tipo</code>. Si no ponés el tipo, se usa <code>str</code>.</p>
        <table class="tabla-comandos"><thead><tr><th>Tipo</th><th>Qué guarda</th></tr></thead><tbody>${Object.entries(tecnologia.tipos)
          .map(([t, d]) => `<tr><td><code>${e(t)}</code></td><td>${e(d)}</td></tr>`)
          .join("")}</tbody></table>`
      : "";
    const contenido = `
      <h3>De andamio</h3>${tablaComandos(variante.comandos_andamio)}
      <h3 style="margin-top:32px">Del proyecto</h3>${tablaComandos(tecnologia.comandos_proyecto)}
      <div style="margin-top:32px">${tipos}</div>`;
    return seccion("comandos", "⌘", "Todos los comandos", contenido, "Para tener a mano.");
  }

  function problemas() {
    const lista = (PROBLEMAS[clave] || []).map(([p, r]) => `<details><summary>${e(p)}</summary><p>${e(r)}</p></details>`).join("");
    const otras = A.datos.tecnologias
      .filter((t) => t.clave !== clave)
      .map((t) => `<a class="boton boton--borde" href="${t.clave}.html">${e(t.titulo)} →</a>`)
      .join("");
    return seccion("problemas", "?", "Problemas comunes", `${lista}<h3 style="margin-top:40px">Otras guías</h3><div class="otras-guias">${otras}</div>`);
  }

  // --- Dibujo e interacción -------------------------------------------------------------

  function mostrarEnExplorador(ruta) {
    const archivo = variante.archivos.find((a) => a.ruta === ruta);
    if (!archivo) return;
    main.querySelector("[data-codigo-nombre]").textContent = ruta;
    main.querySelector("[data-codigo-desc]").textContent = archivo.descripcion || "";
    main.querySelector("[data-codigo]").innerHTML =
      archivo.lenguaje === "imagen" ? `<img class="visor__imagen" src="${archivo.contenido}" alt="${e(ruta)}">` : A.resaltar(archivo.contenido, archivo.lenguaje);
    main.querySelector("[data-codigo-copiar]").dataset.copiar = archivo.lenguaje === "imagen" ? "" : archivo.contenido;
    main.querySelectorAll("[data-arbol] .archivo").forEach((b) => b.setAttribute("aria-current", String(b.dataset.ruta === ruta)));
  }

  function dibujar() {
    document.title = `andamio con ${tecnologia.titulo}${variante.nombre ? ` (${variante.nombre})` : ""}`;
    main.innerHTML = portada() + instalar() + crear() + marcha() + piezas() + completo() + comandos() + problemas();
    const inicial = variante.piezas.find((p) => p.creados.length);
    mostrarEnExplorador(inicial ? inicial.creados[0] : variante.archivos[0].ruta);
  }

  main.addEventListener("click", (evento) => {
    const boton = evento.target.closest("button");
    if (!boton) return;
    if (boton.dataset.variante) {
      variante = tecnologia.variantes.find((v) => v.clave === boton.dataset.variante);
      const url = new URL(location.href);
      url.searchParams.set("v", variante.clave);
      history.replaceState(null, "", url);
      const y = window.scrollY;
      dibujar();
      window.scrollTo(0, y);
      main.querySelector(`[data-variante="${variante.clave}"]`).focus();
    } else if (boton.dataset.archivo) {
      const lista = boton.dataset.origen === "crear" ? variante.archivos_crear : variante.archivos;
      const archivo = lista.find((a) => a.ruta === boton.dataset.archivo);
      if (archivo) A.abrirArchivo(archivo);
    } else if (boton.classList.contains("carpeta")) {
      const abierta = boton.getAttribute("aria-expanded") === "true";
      boton.setAttribute("aria-expanded", String(!abierta));
      boton.nextElementSibling.hidden = abierta;
    } else if (boton.classList.contains("archivo")) {
      mostrarEnExplorador(boton.dataset.ruta);
    }
  });

  dibujar();
  if (location.hash) document.querySelector(location.hash)?.scrollIntoView();
})();
