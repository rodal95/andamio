/* andamio · sitio: guía de una tecnología (python, django, django-web, fastapi, express, web, react, vue, react-native, next, next-fullstack y reflex .html). */
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
    next: {
      marcha: [{ src: "img/next-inicio.jpg", url: "http://localhost:3000", titulo: "La app recién creada", texto: "El menú y la página de inicio, al abrir el navegador después de npm run dev." }],
      piezas: {
        crud: [{ src: "img/next-crud-lista.jpg", url: "http://localhost:3000/productos", titulo: "La lista", texto: "Los productos llegan de la API (acá, la de Django). Cada uno enlaza a su detalle, y el menú tiene un enlace por página." }],
      },
    },
    "next-fullstack": {
      piezas: {
        crud: [
          { src: "img/next-fullstack-crud-detalle.jpg", url: "http://localhost:3000/productos/2/", titulo: "El detalle", texto: "Con los datos que guardó la API de este mismo proyecto, y los botones Editar y Eliminar." },
          { src: "img/next-fullstack-crud-formulario.jpg", url: "http://localhost:3000/productos/nuevo/", titulo: "El formulario", texto: "Si la API rechaza un dato, el error aparece debajo del campo, en español." },
        ],
      },
    },
    reflex: {
      piezas: {
        crud: [{ src: "img/reflex-crud.jpg", url: "http://localhost:3000/productos", titulo: "La página del crud", texto: "El formulario arriba (con el error de validación en español debajo del campo) y la tabla con Editar y Eliminar. Todo escrito en Python." }],
      },
    },
    "react-native": {
      marcha: [{ src: "img/react-native-inicio.jpg", telefono: true, titulo: "La app recién creada", texto: "La pantalla de inicio, en el navegador o en tu celular con Expo Go." }],
      piezas: {
        pantalla: [{ src: "img/react-native-detalle.jpg", telefono: true, titulo: "La pantalla generada", texto: "Con su título en la barra superior y el botón para volver." }],
      },
      combinaciones: {
        "abrir-otra-pantalla": {
          src: "img/react-native-final.jpg",
          telefono: true,
          titulo: "Así queda",
          texto: "La pantalla de inicio con una tarjeta por producto de la API. Tocando una, se abre su detalle.",
        },
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
    next: [
      ["npm install falla", "Revisá la versión de Node con node --version: Next.js necesita 20.9 o más nueva."],
      ["La lista dice Failed to fetch", "La API tiene que estar andando y NEXT_PUBLIC_API_URL del .env tiene que apuntar a ella. Si cambiaste el .env, reiniciá npm run dev."],
      ["React no puede leer la API (error de CORS)", "La dirección de la web (http://localhost:3000) tiene que estar en CORS_ALLOWED_ORIGINS del .env de la API (las APIs nuevas de andamio ya la traen)."],
      ["Error: useState only works in Client Components", "El componente usa estado o eventos: agregá 'use client'; como primera línea del archivo."],
    ],
    "next-fullstack": [
      ["npm install falla", "Revisá la versión de Node con node --version: el full stack (con Prisma) necesita 22.12 o más nueva."],
      ["The table `main.productos` does not exist", "Falta la migración: npx prisma migrate dev --name productos (o generá el recurso con --migrar)."],
      ["Cambié prisma/schema.prisma y no se ve el cambio", "Creá una migración (npx prisma migrate dev --name <qué cambió>) y volvé a ejecutar npm run dev, que genera el cliente de Prisma de nuevo."],
      ["Quiero usar esta API desde React Native", "En el celular usá http://IP-DE-TU-PC:3000/api en EXPO_PUBLIC_API_URL. Para Expo en el navegador, agregá su dirección a CORS_ALLOWED_ORIGINS."],
    ],
    reflex: [
      ["No matching distribution found for reflex", "Reflex 0.11 necesita Python 3.11 o más nuevo. Revisalo con python --version."],
      ["reflex run tarda mucho la primera vez", "Es normal: descarga lo que usa para el navegador (necesita internet). Las siguientes veces arranca enseguida."],
      ["no such table: productos", "Falta la migración: la primera vez reflex db init; después de cambiar un modelo, reflex db makemigrations y reflex db migrate (o generá el crud con --migrar)."],
      ["La página de crud-api dice que no se pudo conectar", "La API (Django, FastAPI o Express) tiene que estar andando y API_URL del .env tiene que apuntar a ella. Si cambiaste el .env, reiniciá reflex run."],
      ["Address already in use (puerto 8001 o 3000)", "Ya hay otra aplicación en ese puerto (por ejemplo, Next.js en el 3000). Cerrala, o cambiá frontend_port o backend_port en rxconfig.py."],
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
  const e = A.escapar;


  // Las piezas de estilos van en su propia pestaña.
  const ESTILOS = new Set(["tema", "ui", "estilo"]);

  // Cómo se llama cada pieza en las pestañas.
  const NOMBRES = {
    componente: "Componentes",
    pagina: "Páginas",
    pantalla: "Pantallas",
    hook: "Hooks",
    composable: "Composables",
    servicio: "Servicios",
    estado: "Estados",
    entidad: "Entidades",
    recurso: "Recursos (la API)",
    login: "Login (JWT)",
    crud: "CRUD",
    "crud-api": "CRUD con una API",
    tema: "Tema",
    ui: "Partes de interfaz",
    estilo: "Estilo propio",
  };

  // --- Las pestañas ------------------------------------------------------------------

  /** Las pestañas de la guía y, adentro de algunas, sus sub-pestañas. */
  function pestanas() {
    const pieza = (clave) => variante.piezas.find((p) => p.clave === clave);
    const comandos = variante.camino
      .filter((l) => l.tipo === "tema" || !ESTILOS.has(l.clave))
      .map((l) =>
        l.tipo === "tema"
          ? { id: `como-${l.id}`, titulo: `Cómo funciona: ${l.titulo}`, tema: l }
          : { id: l.clave, titulo: NOMBRES[l.clave] || pieza(l.clave).titulo, pieza: pieza(l.clave) },
      );
    const estilos = variante.piezas.filter((p) => ESTILOS.has(p.clave)).map((p) => ({ id: p.clave, titulo: NOMBRES[p.clave] || p.titulo, pieza: p }));
    const lista = [{ id: "empezar", titulo: "Empezar" }];
    if (variante.armado && window.AndamioArmado) lista.push({ id: "paso-a-paso", titulo: "Paso a paso" });
    lista.push({ id: "comandos", titulo: "Comandos", sub: comandos });
    if (tecnologia.estilos) {
      lista.push({ id: "estilos", titulo: "Estilos", sub: [{ id: "css", titulo: "El CSS del proyecto", css: true }, ...estilos] });
    }
    lista.push({ id: "proyecto", titulo: "Proyecto completo" });
    if (variante.combinaciones.length) {
      lista.push({
        id: "combinaciones",
        titulo: "Combinaciones",
        sub: variante.combinaciones.map((c, i) => ({ id: c.id, titulo: c.titulo, marca: String.fromCharCode(65 + i), combinacion: c })),
      });
    }
    lista.push({ id: "referencia", titulo: "Todos los comandos" }, { id: "problemas", titulo: "Problemas" });
    return lista;
  }

  // --- Piezas de HTML -------------------------------------------------------------

  function captura(c) {
    const imagen = `<a href="${c.src}" target="_blank" rel="noopener" title="Ver en tamaño completo"><img src="${c.src}" alt="${e(c.titulo)}" loading="lazy" width="${c.telefono ? 390 : 1200}" height="${c.telefono ? 760 : 700}"></a>`;
    const marco = c.telefono
      ? `<div class="telefono">${imagen}</div>`
      : `<div class="navegador"><div class="navegador__barra"><span class="terminal__puntos" aria-hidden="true"><i></i><i></i><i></i></span><span class="navegador__url">${e(c.url || "")}</span></div>${imagen}</div>`;
    return `<figure class="captura">${marco}<figcaption><b>${e(c.titulo)}.</b> ${e(c.texto || "")}</figcaption></figure>`;
  }

  function listaArchivos(rutas, origen) {
    return `<ul class="archivos archivos--compactos">${rutas
      .map((item) => {
        const ruta = typeof item === "string" ? item : item.ruta;
        const archivo = origen.find((a) => a.ruta === ruta) || { estado: "nuevo" };
        const desc = typeof item === "string" ? archivo.descripcion : item.que ? `Se agrega: ${item.que}.` : archivo.descripcion;
        const estado = typeof item === "string" ? (archivo.estado === "proyecto" ? "proyecto" : "nuevo") : "modificado";
        const visible = ruta.endsWith(".gitkeep") ? ruta.slice(0, -".gitkeep".length) : ruta;
        return `<li><button type="button" data-archivo="${e(ruta)}" data-origen="${origen === variante.archivos_crear ? "crear" : "final"}">
          <i class="estado estado--${estado}"></i><span class="archivos__ruta">${e(visible)}</span><span class="archivos__ver">ver código</span>
          <span class="archivos__desc">${e(desc || "")}</span></button></li>`;
      })
      .join("")}</ul>`;
  }

  function terminal(comando, salida, abierta = false) {
    return `<details class="consola"${abierta ? " open" : ""}><summary>Lo que muestra la consola</summary>
      <pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(comando, salida)}</pre></details>`;
  }

  /** Un bloque con título dentro de un panel. */
  function bloque(titulo, contenido, intro = "") {
    return `<div class="bloque"><h3>${e(titulo)}</h3>${intro ? `<p class="bajada">${intro}</p>` : ""}${contenido}</div>`;
  }

  /** El código que arma una pieza: una pestaña por archivo creado o modificado. */
  let visores = 0;
  function visorCodigo(p) {
    const rutas = [...p.creados.map((r) => ({ ruta: r, estado: "nuevo" })), ...p.modificados.map((m) => ({ ruta: m.ruta, estado: "modificado", que: m.que }))].filter(
      (r) => !r.ruta.endsWith(".gitkeep"),
    );
    if (!rutas.length) return "";
    const id = `visor-${++visores}`;
    const botones = rutas
      .map(
        (r, i) =>
          `<button type="button" role="tab" class="visor-pestana" data-visor="${id}" data-ruta="${e(r.ruta)}" aria-selected="${i === 0}"><i class="estado estado--${r.estado}"></i>${e(r.ruta.split("/").pop())}</button>`,
      )
      .join("");
    return `<div class="visor-codigo" id="${id}">
      <div class="visor-codigo__pestanas" role="tablist" aria-label="Archivos">${botones}</div>
      <div class="visor-codigo__info"><code data-visor-ruta></code><span data-visor-desc></span>
        <button class="terminal__boton" type="button" data-visor-copiar>Copiar</button></div>
      <pre class="codigo__cuerpo visor-codigo__cuerpo"><code data-visor-codigo></code></pre>
    </div>`;
  }

  function mostrarEnVisor(visor, ruta) {
    const archivo = variante.archivos.find((a) => a.ruta === ruta);
    if (!archivo) return;
    const boton = visor.querySelector(`[data-ruta="${CSS.escape(ruta)}"]`);
    visor.querySelectorAll(".visor-pestana").forEach((b) => b.setAttribute("aria-selected", String(b === boton)));
    const modificado = boton && boton.querySelector(".estado--modificado");
    visor.querySelector("[data-visor-ruta]").textContent = ruta;
    visor.querySelector("[data-visor-desc]").textContent = archivo.descripcion || "";
    if (modificado) visor.querySelector("[data-visor-desc]").textContent = "Archivo que ya existía: andamio le agregó líneas. " + (archivo.descripcion || "");
    visor.querySelector("[data-visor-codigo]").innerHTML =
      archivo.lenguaje === "imagen" ? `<img class="visor__imagen" src="${archivo.contenido}" alt="${e(ruta)}">` : A.resaltar(archivo.contenido, archivo.lenguaje);
    visor.querySelector("[data-visor-copiar]").dataset.copiar = archivo.lenguaje === "imagen" ? "" : archivo.contenido;
  }

  function tablaComandos(comandos, encabezado = "Para qué sirve") {
    return `<div class="tabla-desliza"><table class="tabla-comandos"><thead><tr><th>Comando</th><th>${e(encabezado)}</th></tr></thead><tbody>${comandos
      .map(
        (c) =>
          `<tr><td><code>${e(c.comando)}</code><button type="button" class="copiar-chico" data-copiar="${e(c.comando)}">Copiar</button></td><td>${e(c.descripcion)}</td></tr>`,
      )
      .join("")}</tbody></table></div>`;
  }

  // --- Paneles ---------------------------------------------------------------------

  function panelEmpezar() {
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
      vista = bloque("Así se ve la aplicación (después de generar una entidad)", `<pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(tecnologia.ejecucion.comando, tecnologia.ejecucion.salida)}</pre>`);
    } else if (capturas.marcha) {
      vista = bloque("Así se ve", `<div class="capturas">${capturas.marcha.map(captura).join("")}</div>`);
    }
    return `
      ${bloque(
        "1. Instalá andamio",
        `${A.comandoHtml(`python -m pip install ${A.urlWhl}`)}
        <p class="bajada">Para comprobar que quedó instalado:</p>${A.comandoHtml("python -m andamio --version")}
        <p class="nota">Todos los comandos empiezan con <code>python -m andamio</code>, que funciona en cualquier PC (en Linux o Mac, <code>python3</code>).
        ¿Sin permisos o sin internet? Mirá <a href="index.html#instalar">las otras formas de instalarlo</a>.</p>
        <details class="consola"><summary>¿En Linux dice <code>externally-managed-environment</code>?</summary>
          <p>No es un error de andamio. Ubuntu, Debian y otras distribuciones nuevas (con Python 3.12 o más nuevo) no dejan que
          <code>pip</code> instale nada en el Python del sistema, porque el sistema operativo también lo usa (es la regla PEP 668):
          el mismo comando va a fallar siempre, con cualquier paquete. Instalalo con <b>pipx</b>, que le arma su propio entorno:</p>
          ${A.comandoHtml("sudo apt install pipx")}${A.comandoHtml(`pipx install ${A.urlWhl}`)}${A.comandoHtml("pipx ensurepath")}
          <p>Cerrá la terminal, abrí una nueva y escribí <code>andamio</code> en lugar de <code>python3 -m andamio</code>
          (por ejemplo: <code>andamio crear ${e(clave)} mi-proyecto</code>). Sin <code>sudo</code>, usá <code>andamio.pyz</code>
          (en <a href="index.html#instalar">Instalar → Sin instalar</a>).</p></details>`,
        "Una sola vez en la PC. En Windows, en CMD o PowerShell:",
      )}
      ${bloque(
        "2. Creá el proyecto",
        `${A.comandoHtml(variante.crear.comando, "comando--grande")}
        ${terminal(variante.crear.comando, variante.crear.salida)}
        <h4>Qué crea y para qué sirve cada archivo</h4>
        ${listaArchivos(variante.archivos_crear.map((a) => a.ruta), variante.archivos_crear)}`,
        `En la carpeta donde guardás tus trabajos: andamio crea la carpeta del proyecto con todo lo necesario. ¿Ya estás en una carpeta vacía para el proyecto? Usá un punto en lugar del nombre: <code>${e(variante.crear.comando.split(" ").slice(0, 5).join(" "))} .</code> (lo crea ahí mismo, sin tener que entrar después).`,
      )}
      ${bloque("3. Ponelo en marcha", `<ol class="pasos-marcha">${pasos}</ol>`, "Son los mismos pasos que muestra andamio al terminar de crear el proyecto.")}
      ${vista}
      ${bloque(
        "4. Y después",
        `<p>Cada cosa que agregues al proyecto es una <b>pieza</b>: <code>python -m andamio nuevo &lt;pieza&gt; &lt;nombre&gt;</code>. En la pestaña
        <a href="#comandos" data-ir="comandos">Comandos</a> está cada una con su consola, su código y sus variantes${
          variante.armado ? '; en <a href="#paso-a-paso" data-ir="paso-a-paso">Paso a paso</a>, un proyecto armado comando por comando, con el código y cómo se ve' : ""
        }${
          tecnologia.estilos ? '; en <a href="#estilos" data-ir="estilos">Estilos</a>, cómo darle diseño' : ""
        }; y en <a href="#proyecto" data-ir="proyecto">Proyecto completo</a>, un proyecto entero armado de punta a punta.</p>`,
      )}`;
  }

  function panelPieza(p) {
    const capturasPieza = (capturas.piezas || {})[p.clave] || [];
    const ingles = p.ingles ? ` En inglés: <code>new ${e(p.ingles)}</code>.` : "";
    const opciones = p.opciones.length ? ` Opciones propias: ${p.opciones.map((o) => `<code>--${e(o)}</code>`).join(", ")}.` : "";
    return `
      <p class="leccion__intro">${e(p.explicacion)}</p>
      ${bloque("La forma general", `${A.comandoHtml(p.forma)}<p class="nota">Lo que va entre <code>&lt; &gt;</code> lo elegís vos: el ejemplo de abajo usa unos nombres, pero sirve cualquiera.${ingles}${opciones}</p>`)}
      ${bloque("Ejecutalo", `${A.comandoHtml(p.comando)}${terminal(p.comando, p.salida, true)}`, e(p.descripcion.charAt(0).toUpperCase() + p.descripcion.slice(1)) + ".")}
      ${bloque("Lo que arma en el código", visorCodigo(p), "Cada archivo que crea (verde) o modifica (amarillo). Tocá un archivo para ver su código.")}
      ${bloque("Todas las variantes", tablaComandos(p.variantes, "Qué cambia"))}
      ${bloque("Cómo se usa", A.codigoHtml(p.uso, p.uso_lenguaje))}
      ${capturasPieza.length ? bloque("Así se ve", `<div class="capturas">${capturasPieza.map(captura).join("")}</div>`) : ""}`;
  }

  function panelTema(t) {
    const archivos = t.archivos
      .map((ruta) => {
        const archivo = variante.archivos.find((a) => a.ruta === ruta);
        return `<h4><code>${e(ruta)}</code></h4>${A.codigoHtml(archivo.contenido, archivo.lenguaje, true)}`;
      })
      .join("");
    return `<div class="leccion__texto">${t.texto.map((p) => `<p>${e(p)}</p>`).join("")}</div>${archivos}`;
  }

  function panelCss() {
    const g = tecnologia.estilos;
    const tiene = (clave) => variante.piezas.some((p) => p.clave === clave);
    const pasos = [];
    if (tiene("componente")) pasos.push(["nuevo componente Tarjeta", "Un componente con su CSS base, listo para modificar."]);
    else if (tiene("pagina")) pasos.push(["nuevo pagina Contacto", "Una página."]);
    if (tiene("tema")) pasos.push(["nuevo tema verde", "Los colores, la letra y el modo oscuro de todo el proyecto: lo que ya generaste cambia de look."]);
    if (tiene("estilo")) pasos.push(["nuevo estilo contacto", "Un CSS propio (con el nombre que quieras) para tu página o componente, ya conectado."]);
    if (tiene("ui")) pasos.push(["nuevo ui responsive", "Mejoras para el celular sobre lo que ya tenés."], ["nuevo ui accesible", "Foco visible, texto para lectores de pantalla y menos movimiento."]);
    const receta = pasos.map(([c, d]) => `<li>${A.comandoHtml(`python -m andamio ${c}`)}<p>${e(d)}</p></li>`).join("");
    const variables = tiene("tema") && tecnologia.clave !== "react-native" && tecnologia.clave !== "reflex"
      ? bloque(
          "Mejorar el CSS de un componente o página",
          A.codigoHtml(
            "/* Cambiá los colores fijos por las variables del tema: */\n.tarjeta {\n  background: var(--superficie);\n  color: var(--texto);\n  border: 1px solid var(--borde);\n  border-radius: var(--radio);\n  box-shadow: var(--sombra);\n}\n\n.tarjeta:hover {\n  border-color: var(--acento);\n}",
            "css",
          ),
          "Con <code>nuevo tema</code>, tu CSS puede usar las mismas variables: si cambiás el tema, cambia con él.",
        )
      : "";
    return `
      ${bloque("Dónde está el CSS", `<ul class="lista-css"><li><b>Base del proyecto.</b> ${e(g.base)}</li><li><b>Componentes.</b> ${e(g.componente)}</li><li><b>Páginas.</b> ${e(g.pagina)}</li></ul>`)}
      ${bloque("Una receta: de CSS base a un diseño propio", `<ol class="pasos-marcha">${receta}</ol>`)}
      ${variables}
      <p class="nota">En las sub-pestañas está cada comando de estilos con su consola, su código y todas sus variantes.</p>`;
  }

  function panelCombinacion(c) {
    const pasos = c.pasos.map((p) => `<li><div>${p.lugar ? `<p class="paso-lugar">${e(p.lugar)}</p>` : ""}${A.comandoHtml(p.comando)}</div></li>`).join("");
    const archivos = c.archivos.map((a) => `<p class="combinacion__archivo">En <code>${e(a.ruta)}</code>:</p>${A.codigoHtml(a.contenido, a.lenguaje, true)}`).join("");
    const foto = (capturas.combinaciones || {})[c.id];
    return `
      <p class="leccion__intro">${e(c.texto)}</p>
      <p class="combinacion__usa">Usa: ${c.usa.map((k) => `<span>${e(NOMBRES[k] || k)}</span>`).join("")}</p>
      ${bloque(c.archivos.length ? "1. Generá las piezas" : "Pasos", `<ol class="pasos-marcha">${pasos}</ol>`)}
      ${c.archivos.length ? bloque("2. Escribí el código", archivos) : ""}
      ${bloque("Qué hace cada parte", `<ul class="combinacion__claves">${c.claves.map((k) => `<li>${e(k)}</li>`).join("")}</ul>`)}
      ${foto ? `<div class="capturas">${captura(foto)}</div>` : ""}`;
  }

  function panelProyecto() {
    const pasos = variante.recorrido
      .map((paso) => {
        if (!paso.andamio) return `<li class="recorrido__paso">${A.comandoHtml(paso.comando)}<p>${e(paso.explicacion)}</p></li>`;
        const archivos = [...(paso.creados || []).map((r) => `<li><i class="estado estado--nuevo"></i>${e(r)}</li>`), ...(paso.modificados || []).map((r) => `<li><i class="estado estado--modificado"></i>${e(r)}</li>`)].join("");
        return `<li class="recorrido__paso recorrido__paso--andamio">${A.comandoHtml(paso.comando)}<p>${e(paso.explicacion)}</p>
          ${terminal(paso.comando, paso.salida)}
          ${archivos ? `<details class="consola"><summary>Archivos que crea y modifica</summary><ul class="recorrido__archivos">${archivos}</ul></details>` : ""}</li>`;
      })
      .join("");
    return `
      <p class="leccion__intro">Un proyecto entero, desde cero, solo con comandos. Los de andamio se ejecutaron de verdad para armar esta guía: lo que ves es lo que muestran.</p>
      ${bloque("Paso a paso", `<ol class="recorrido">${pasos}</ol>`)}
      ${bloque(
        "El proyecto de esta guía, archivo por archivo",
        `<div class="explorador">
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
        </div>`,
        "Así queda el proyecto de la pestaña Comandos, con todas sus piezas. Recorré los archivos.",
      )}`;
  }

  function panelReferencia() {
    const piezas = variante.piezas
      .map((p) => `<h4 id="ref-${p.clave}">${e(NOMBRES[p.clave] || p.titulo)} <span class="ref-forma"><code>${e(p.forma)}</code></span></h4>${tablaComandos(p.variantes, "Qué cambia")}`)
      .join("");
    const tipos = Object.keys(tecnologia.tipos).length
      ? bloque(
          "Tipos de campo",
          `<table class="tabla-comandos"><thead><tr><th>Tipo</th><th>Qué guarda</th></tr></thead><tbody>${Object.entries(tecnologia.tipos)
            .map(([t, d]) => `<tr><td><code>${e(t)}</code></td><td>${e(d)}</td></tr>`)
            .join("")}</tbody></table>`,
          "Los campos se escriben <code>nombre:tipo</code>. Si no ponés el tipo, se usa <code>str</code>.",
        )
      : "";
    return `
      <p class="leccion__intro">Todos los comandos de ${e(tecnologia.titulo)}, para tener a mano. En la terminal: <code>python -m andamio comandos</code>.</p>
      ${bloque("Crear el proyecto y comandos de andamio", tablaComandos(variante.comandos_andamio))}
      ${bloque("Cada pieza, con todas sus variantes", piezas)}
      ${bloque("Del proyecto", tablaComandos(tecnologia.comandos_proyecto))}
      ${tipos}`;
  }

  function panelProblemas() {
    const lista = (PROBLEMAS[clave] || []).map(([p, r]) => `<details><summary>${e(p)}</summary><p>${e(r)}</p></details>`).join("");
    const otras = A.datos.tecnologias
      .filter((t) => t.clave !== clave)
      .map((t) => `<a class="boton boton--borde" href="${t.clave}.html">${e(t.titulo)} →</a>`)
      .join("");
    return `${lista}<h3>Otras guías</h3><div class="otras-guias">${otras}</div>`;
  }

  // --- Dibujo ----------------------------------------------------------------------

  function portada() {
    const selector =
      tecnologia.variantes.length > 1
        ? `<div class="variante"><span class="variante__etiqueta">Lenguaje:</span>
          <div class="segmentado" role="group" aria-label="Lenguaje">${tecnologia.variantes
            .map((v) => `<button type="button" data-variante="${v.clave}" aria-pressed="${v.clave === variante.clave}">${e(v.nombre)}</button>`)
            .join("")}</div>
          <span class="variante__nota">Cambia los comandos, los archivos y el código de toda la guía.</span></div>`
        : "";
    return `<section class="guia-portada"><div class="contenedor">
      <p class="migas"><a href="index.html">andamio</a> / guía</p>
      <h1>andamio con ${e(tecnologia.titulo)}</h1>
      <p class="guia-portada__resumen">${e(tecnologia.resumen)}</p>
      <ul class="requisitos" aria-label="Qué necesitás">${tecnologia.requisitos.map((r) => `<li>${e(r)}</li>`).join("")}</ul>
      ${selector}
    </div></section>`;
  }

  function contenidoSub(sub) {
    if (sub.pieza) return panelPieza(sub.pieza);
    if (sub.tema) return panelTema(sub.tema);
    if (sub.combinacion) return panelCombinacion(sub.combinacion);
    if (sub.css) return panelCss();
    return "";
  }

  const PANELES = {
    empezar: panelEmpezar,
    "paso-a-paso": () => window.AndamioArmado.panel(variante.armado),
    proyecto: panelProyecto,
    referencia: panelReferencia,
    problemas: panelProblemas,
  };

  function panel(p) {
    if (!p.sub) return `<section class="panel" id="panel-${p.id}" role="tabpanel" aria-labelledby="pestana-${p.id}" data-panel="${p.id}" hidden>${PANELES[p.id]()}</section>`;
    const lista = p.sub
      .map(
        (s, i) =>
          `<button type="button" role="tab" class="subpestana" id="sub-${p.id}-${s.id}" data-sub="${p.id}/${s.id}" aria-selected="false" aria-controls="subpanel-${p.id}-${s.id}">${
            s.marca ? `<b>${s.marca}</b>` : `<b>${i + 1}</b>`
          }<span>${e(s.titulo)}</span></button>`,
      )
      .join("");
    const paneles = p.sub
      .map((s, i) => {
        const antes = p.sub[i - 1];
        const despues = p.sub[i + 1];
        const nav = `<nav class="leccion__nav" aria-label="Seguir">${antes ? `<a class="leccion__anterior" href="#${p.id}/${antes.id}" data-ir="${p.id}/${antes.id}"><span>Anterior</span>${e(antes.titulo)}</a>` : "<span></span>"}${
          despues ? `<a class="leccion__siguiente" href="#${p.id}/${despues.id}" data-ir="${p.id}/${despues.id}"><span>Siguiente</span>${e(despues.titulo)}</a>` : ""
        }</nav>`;
        const ante = s.pieza ? `<p class="leccion__ante">python -m andamio nuevo ${e(s.pieza.clave)}</p>` : "";
        return `<section class="subpanel" id="subpanel-${p.id}-${s.id}" role="tabpanel" aria-labelledby="sub-${p.id}-${s.id}" data-subpanel="${p.id}/${s.id}" hidden>
          ${ante}<h2>${e(s.titulo)}</h2>${contenidoSub(s)}${nav}</section>`;
      })
      .join("");
    return `<section class="panel" id="panel-${p.id}" role="tabpanel" aria-labelledby="pestana-${p.id}" data-panel="${p.id}" hidden>
      <div class="con-subpestanas"><div class="subpestanas" role="tablist" aria-orientation="vertical" aria-label="${e(p.titulo)}">${lista}</div>
      <div class="subpaneles">${paneles}</div></div></section>`;
  }

  let lista = [];

  /** Muestra una pestaña (y una sub-pestaña): "comandos/crud", "proyecto"... */
  function mostrar(destino, enfocar = false) {
    let [id, subId] = destino.split("/");
    let pestana = lista.find((p) => p.id === id) || lista[0];
    if (pestana.sub && !pestana.sub.some((s) => s.id === subId)) subId = pestana.sub[0].id;
    main.querySelectorAll("[data-pestana]").forEach((b) => {
      const activa = b.dataset.pestana === pestana.id;
      b.setAttribute("aria-selected", String(activa));
      b.tabIndex = activa ? 0 : -1;
    });
    main.querySelectorAll("[data-panel]").forEach((s) => (s.hidden = s.dataset.panel !== pestana.id));
    if (pestana.sub) {
      const clave = `${pestana.id}/${subId}`;
      const panelActivo = main.querySelector(`[data-panel="${pestana.id}"]`);
      panelActivo.querySelectorAll("[data-sub]").forEach((b) => {
        const activa = b.dataset.sub === clave;
        b.setAttribute("aria-selected", String(activa));
        b.tabIndex = activa ? 0 : -1;
      });
      panelActivo.querySelectorAll("[data-subpanel]").forEach((s) => (s.hidden = s.dataset.subpanel !== clave));
      const visible = panelActivo.querySelector(`[data-subpanel="${clave}"]`);
      visible.querySelectorAll(".visor-codigo").forEach((v) => {
        if (!v.dataset.listo) {
          v.dataset.listo = "1";
          mostrarEnVisor(v, v.querySelector(".visor-pestana").dataset.ruta);
        }
      });
      destino = clave;
    } else {
      destino = pestana.id;
    }
    history.replaceState(null, "", `#${destino}`);
    if (pestana.id === "paso-a-paso") window.AndamioArmado.alMostrar();
    const sub = pestana.sub && pestana.sub.find((s) => `${pestana.id}/${s.id}` === destino);
    const base = `andamio con ${tecnologia.titulo}${variante.nombre ? ` (${variante.nombre})` : ""}`;
    document.title = pestana.id === "empezar" ? base : `${sub ? sub.titulo : pestana.titulo} · ${base}`;
    if (enfocar) main.querySelector(".guia-tabs").scrollIntoView({ block: "start" });
  }

  /** Los enlaces viejos (#pieza-crud, #combinacion-x, #comandos) siguen funcionando. */
  function traducirHash(hash) {
    const h = decodeURIComponent(hash.replace(/^#/, ""));
    if (h.startsWith("pieza-")) {
      const clavePieza = h.slice(6);
      return `${ESTILOS.has(clavePieza) ? "estilos" : "comandos"}/${clavePieza}`;
    }
    if (h.startsWith("combinacion-")) return `combinaciones/${h.slice(12)}`;
    if (h.startsWith("tema-")) return `comandos/como-${h.slice(5)}`;
    return { instalar: "empezar", crear: "empezar", marcha: "empezar", completo: "proyecto", comandos: "comandos", problemas: "problemas" }[h] || h || "empezar";
  }

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

  function dibujar(destino) {
    lista = pestanas();
    visores = 0;
    const barra = lista
      .map(
        (p) =>
          `<button type="button" role="tab" class="guia-tab" id="pestana-${p.id}" data-pestana="${p.id}" aria-controls="panel-${p.id}" aria-selected="false">${e(p.titulo)}</button>`,
      )
      .join("");
    main.innerHTML = `${portada()}<div class="contenedor guia-pestanas">
      <div class="guia-tabs" role="tablist" aria-label="Secciones de la guía">${barra}</div>
      ${lista.map(panel).join("")}
    </div>`;
    const inicial = variante.piezas.find((p) => p.creados.length);
    mostrarEnExplorador(inicial ? inicial.creados[0] : variante.archivos[0].ruta);
    const panelArmado = main.querySelector('[data-panel="paso-a-paso"]');
    if (panelArmado) window.AndamioArmado.iniciar(panelArmado, variante.armado);
    mostrar(destino);
  }

  /** Flechas del teclado en una lista de pestañas (horizontal o vertical). */
  main.addEventListener("keydown", (evento) => {
    const tab = evento.target.closest('[role="tab"]');
    if (!tab) return;
    const teclas = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1, Home: "inicio", End: "fin" };
    const paso = teclas[evento.key];
    if (paso === undefined) return;
    const hermanas = Array.from(tab.parentElement.querySelectorAll('[role="tab"]'));
    let i = hermanas.indexOf(tab);
    i = paso === "inicio" ? 0 : paso === "fin" ? hermanas.length - 1 : (i + paso + hermanas.length) % hermanas.length;
    evento.preventDefault();
    hermanas[i].click();
    hermanas[i].focus();
  });

  main.addEventListener("click", (evento) => {
    const ir = evento.target.closest("[data-ir]");
    if (ir) {
      evento.preventDefault();
      mostrar(ir.dataset.ir, true);
      return;
    }
    const boton = evento.target.closest("button");
    if (!boton) return;
    if (boton.dataset.pestana) {
      mostrar(boton.dataset.pestana);
    } else if (boton.dataset.sub) {
      mostrar(boton.dataset.sub);
    } else if (boton.dataset.visor) {
      mostrarEnVisor(document.getElementById(boton.dataset.visor), boton.dataset.ruta);
    } else if (boton.dataset.variante) {
      variante = tecnologia.variantes.find((v) => v.clave === boton.dataset.variante);
      const url = new URL(location.href);
      url.searchParams.set("v", variante.clave);
      history.replaceState(null, "", url);
      const y = window.scrollY;
      dibujar(location.hash.slice(1) || "empezar");
      window.scrollTo(0, y);
      main.querySelector(`[data-variante="${variante.clave}"]`).focus();
    } else if (boton.dataset.archivo) {
      const listaArch = boton.dataset.origen === "crear" ? variante.archivos_crear : variante.archivos;
      const archivo = listaArch.find((a) => a.ruta === boton.dataset.archivo);
      if (archivo) A.abrirArchivo(archivo);
    } else if (boton.classList.contains("carpeta")) {
      const abierta = boton.getAttribute("aria-expanded") === "true";
      boton.setAttribute("aria-expanded", String(!abierta));
      boton.nextElementSibling.hidden = abierta;
    } else if (boton.classList.contains("archivo")) {
      mostrarEnExplorador(boton.dataset.ruta);
    }
  });

  window.addEventListener("hashchange", () => mostrar(traducirHash(location.hash)));

  dibujar(traducirHash(location.hash));
})();
