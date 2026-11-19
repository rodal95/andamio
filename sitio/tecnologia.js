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

  // Cómo se llama cada pieza en el índice (la lección).
  const LECCIONES = {
    componente: "Componentes",
    pagina: "Páginas",
    pantalla: "Pantallas",
    hook: "Hooks",
    servicio: "Servicios",
    estado: "Estados",
    entidad: "Entidades",
    recurso: "Recursos (la API)",
  };

  // --- El índice: las lecciones de la guía, en orden --------------------------------

  /** Todas las secciones de la guía, agrupadas como en el índice lateral. */
  function indice() {
    const grupos = [
      {
        titulo: "Empezar",
        items: [
          { id: "instalar", titulo: "Instalá andamio" },
          { id: "crear", titulo: "Creá el proyecto" },
          { id: "marcha", titulo: "Ponelo en marcha" },
        ],
      },
      {
        titulo: "Paso a paso",
        items: variante.camino.map((l) => {
          if (l.tipo === "tema") return { id: `tema-${l.id}`, titulo: l.titulo, tema: l };
          const pieza = variante.piezas.find((p) => p.clave === l.clave);
          return { id: `pieza-${l.clave}`, titulo: LECCIONES[l.clave] || pieza.titulo, pieza };
        }),
      },
    ];
    if (variante.combinaciones.length) {
      grupos.push({
        titulo: "Combinaciones",
        letras: true,
        items: variante.combinaciones.map((c) => ({ id: `combinacion-${c.id}`, titulo: c.titulo, combinacion: c })),
      });
    }
    grupos.push({
      titulo: "Referencia",
      sinNumero: true,
      items: [
        { id: "completo", titulo: "El proyecto completo" },
        { id: "comandos", titulo: "Todos los comandos" },
        { id: "problemas", titulo: "Problemas comunes" },
      ],
    });
    let numero = 0;
    for (const grupo of grupos) {
      grupo.items.forEach((item, i) => {
        if (grupo.letras) item.marca = String.fromCharCode(65 + i);
        else if (!grupo.sinNumero) item.marca = String(++numero);
      });
    }
    return grupos;
  }

  function indiceLateral(grupos) {
    return `<nav class="indice-lateral" aria-label="Índice de la guía">
      <details class="indice-lateral__plegable" data-indice>
        <summary>Índice de la guía</summary>
        ${grupos
          .map(
            (g) => `<p class="indice-lateral__grupo">${e(g.titulo)}</p><ol>${g.items
              .map((i) => `<li><a href="#${i.id}">${i.marca ? `<b>${i.marca}</b>` : ""}<span>${e(i.titulo)}</span></a></li>`)
              .join("")}</ol>`,
          )
          .join("")}
      </details>
    </nav>`;
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
        // Una carpeta vacía (con .gitkeep) se muestra como carpeta.
        const visible = ruta.endsWith(".gitkeep") ? ruta.slice(0, -".gitkeep".length) : ruta;
        return `<li><button type="button" data-archivo="${e(ruta)}" data-origen="${origen === variante.archivos_crear ? "crear" : "final"}">
          <i class="estado estado--${estado}"></i><span class="archivos__ruta">${e(visible)}</span><span class="archivos__ver">ver código</span>
          <span class="archivos__desc">${e(desc || "")}</span></button></li>`;
      })
      .join("")}</ul>`;
  }

  /** Una lección: antetítulo (Paso 4, Combinación A...), título, introducción y contenido. */
  function leccion(item, antetitulo, contenido, intro = "", clase = "") {
    return `<section class="leccion ${clase}" id="${item.id}" data-leccion>
      <p class="leccion__ante">${item.marca ? `<b>${item.marca}</b>` : ""}${e(antetitulo)}</p>
      <h2>${e(item.titulo)}</h2>
      ${intro ? `<p class="leccion__intro">${intro}</p>` : ""}
      ${contenido}
      <nav class="leccion__nav" aria-label="Seguir la guía" data-nav="${item.id}"></nav>
    </section>`;
  }

  // --- Empezar ---------------------------------------------------------------------

  function instalar(item) {
    const contenido = `
      ${A.comandoHtml(`python -m pip install ${A.urlWhl}`)}
      <p class="bajada">Para comprobar que quedó instalado:</p>
      ${A.comandoHtml("python -m andamio --version")}
      <p class="nota">andamio es un programa de Python: por eso todos los comandos de esta guía empiezan con
        <code>python -m andamio</code>, que funciona en cualquier PC. ¿Sin permisos o sin internet? Mirá
        <a href="index.html#instalar">las otras formas de instalarlo</a>.</p>`;
    return leccion(item, "Empezar", contenido, "Una sola vez en la PC. En Windows, en CMD o PowerShell (en Linux o Mac, con python3):");
  }

  function crear(item) {
    const contenido = `
      ${A.comandoHtml(variante.crear.comando, "comando--grande")}
      <h3>Qué crea y para qué sirve cada archivo</h3>
      ${listaArchivos(variante.archivos_crear.map((a) => a.ruta), variante.archivos_crear)}
      <details><summary>Ver lo que muestra la terminal</summary>
        <pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(variante.crear.comando, variante.crear.salida)}</pre></details>`;
    return leccion(
      item,
      "Empezar",
      contenido,
      "En la carpeta donde guardás tus trabajos. andamio crea la carpeta del proyecto con todo lo necesario para ejecutarlo.",
    );
  }

  function marcha(item) {
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
      vista = `<h3>Así se ve la aplicación (después de generar una entidad)</h3>
        <pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(tecnologia.ejecucion.comando, tecnologia.ejecucion.salida)}</pre>`;
    } else if (capturas.marcha) {
      vista = `<h3>Así se ve</h3><div class="capturas">${capturas.marcha.map(captura).join("")}</div>`;
    }
    return leccion(item, "Empezar", `<ol class="pasos-marcha">${pasos}</ol>${vista}`, "Son los mismos pasos que te muestra andamio al terminar de crear el proyecto.");
  }

  // --- Paso a paso -------------------------------------------------------------------

  function pieza(item) {
    const p = item.pieza;
    const capturasPieza = (capturas.piezas || {})[p.clave] || [];
    const modificados = p.modificados.length ? `<h3>Qué modifica</h3>${listaArchivos(p.modificados, variante.archivos)}` : "";
    const contenido = `
      <h3>Generalo</h3>
      ${A.comandoHtml(p.comando)}
      <details><summary>Ver lo que muestra la terminal</summary>
        <pre class="terminal terminal__cuerpo terminal--chica">${A.terminalHtml(p.comando, p.salida)}</pre></details>
      <h3>Qué crea</h3>
      ${listaArchivos(p.creados, variante.archivos)}
      ${modificados}
      <h3>Cómo se usa</h3>
      ${A.codigoHtml(p.uso, p.uso_lenguaje)}
      ${capturasPieza.length ? `<h3>Así se ve</h3><div class="capturas">${capturasPieza.map(captura).join("")}</div>` : ""}`;
    return leccion(item, `Paso ${item.marca} · andamio nuevo ${p.clave}`, contenido, e(p.explicacion));
  }

  function tema(item) {
    const t = item.tema;
    const archivos = t.archivos
      .map((ruta) => {
        const archivo = variante.archivos.find((a) => a.ruta === ruta);
        return `<h3><code>${e(ruta)}</code></h3>${A.codigoHtml(archivo.contenido, archivo.lenguaje, true)}`;
      })
      .join("");
    const texto = t.texto.map((p) => `<p>${e(p)}</p>`).join("");
    return leccion(item, `Paso ${item.marca} · cómo funciona`, `<div class="leccion__texto">${texto}</div>${archivos}`, "", "leccion--tema");
  }

  // --- Combinaciones -------------------------------------------------------------------

  function combinacion(item) {
    const c = item.combinacion;
    const usa = c.usa
      .map((clavePieza) => {
        const enCamino = variante.camino.some((l) => l.clave === clavePieza);
        const nombre = LECCIONES[clavePieza] || clavePieza;
        return enCamino ? `<a href="#pieza-${clavePieza}">${e(nombre)}</a>` : `<span>${e(nombre)}</span>`;
      })
      .join("");
    const pasos = c.pasos
      .map((p) => `<li><div>${p.lugar ? `<p class="paso-lugar">${e(p.lugar)}</p>` : ""}${A.comandoHtml(p.comando)}</div></li>`)
      .join("");
    const archivos = c.archivos
      .map((a) => `<p class="combinacion__archivo">En <code>${e(a.ruta)}</code>:</p>${A.codigoHtml(a.contenido, a.lenguaje, true)}`)
      .join("");
    const claves = c.claves.map((k) => `<li>${e(k)}</li>`).join("");
    const foto = (capturas.combinaciones || {})[c.id];
    const contenido = `
      <p class="combinacion__usa">Usa: ${usa}</p>
      <h3>${c.archivos.length ? "1. Generá las piezas" : "Pasos"}</h3>
      <ol class="pasos-marcha">${pasos}</ol>
      ${c.archivos.length ? `<h3>2. Escribí el código</h3>${archivos}` : ""}
      <h3>Qué hace cada parte</h3>
      <ul class="combinacion__claves">${claves}</ul>
      ${foto ? `<div class="capturas">${captura(foto)}</div>` : ""}`;
    return leccion(item, `Combinación ${item.marca}`, contenido, e(c.texto), "leccion--combinacion");
  }

  // --- Referencia ----------------------------------------------------------------------

  function completo(item) {
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
      </div>`;
    return leccion(item, "Referencia", contenido, "Así queda el proyecto después de generar todas las piezas de esta guía. Recorré los archivos.");
  }

  function tablaComandos(comandos) {
    return `<table class="tabla-comandos"><thead><tr><th>Comando</th><th>Para qué sirve</th></tr></thead><tbody>${comandos
      .map((c) => `<tr><td><code>${e(c.comando)}</code><button type="button" class="copiar-chico" data-copiar="${e(c.comando)}">Copiar</button></td><td>${e(c.descripcion)}</td></tr>`)
      .join("")}</tbody></table>`;
  }

  function comandos(item) {
    const tipos = Object.keys(tecnologia.tipos).length
      ? `<h3 id="tipos">Tipos de campo</h3><p class="bajada">Los campos se escriben <code>nombre:tipo</code>. Si no ponés el tipo, se usa <code>str</code>.</p>
        <table class="tabla-comandos"><thead><tr><th>Tipo</th><th>Qué guarda</th></tr></thead><tbody>${Object.entries(tecnologia.tipos)
          .map(([t, d]) => `<tr><td><code>${e(t)}</code></td><td>${e(d)}</td></tr>`)
          .join("")}</tbody></table>`
      : "";
    const contenido = `<h3>De andamio</h3>${tablaComandos(variante.comandos_andamio)}<h3>Del proyecto</h3>${tablaComandos(tecnologia.comandos_proyecto)}${tipos}`;
    return leccion(item, "Referencia", contenido, "Para tener a mano.");
  }

  function problemas(item) {
    const lista = (PROBLEMAS[clave] || []).map(([p, r]) => `<details><summary>${e(p)}</summary><p>${e(r)}</p></details>`).join("");
    const otras = A.datos.tecnologias
      .filter((t) => t.clave !== clave)
      .map((t) => `<a class="boton boton--borde" href="${t.clave}.html">${e(t.titulo)} →</a>`)
      .join("");
    return leccion(item, "Referencia", `${lista}<h3>Otras guías</h3><div class="otras-guias">${otras}</div>`);
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

  const DIBUJAR = { instalar, crear, marcha, completo, comandos, problemas };

  function seccion(item) {
    if (item.pieza) return pieza(item);
    if (item.tema) return tema(item);
    if (item.combinacion) return combinacion(item);
    return DIBUJAR[item.id](item);
  }

  /** Abajo de cada lección: la anterior y la siguiente, para seguir la guía en orden. */
  function navegacion(items) {
    items.forEach((item, i) => {
      const nav = main.querySelector(`[data-nav="${item.id}"]`);
      const antes = items[i - 1];
      const despues = items[i + 1];
      nav.innerHTML =
        (antes ? `<a class="leccion__anterior" href="#${antes.id}"><span>Anterior</span>${e(antes.titulo)}</a>` : "<span></span>") +
        (despues ? `<a class="leccion__siguiente" href="#${despues.id}"><span>Siguiente</span>${e(despues.titulo)}</a>` : "");
    });
  }

  /** Marca en el índice la lección que se está leyendo: la última que empieza en el tercio de arriba. */
  let pendiente = false;
  function marcarLeccionActual() {
    pendiente = false;
    const secciones = Array.from(main.querySelectorAll("[data-leccion]"));
    let actual = secciones[0];
    for (const seccion of secciones) {
      if (seccion.getBoundingClientRect().top <= Math.max(140, window.innerHeight / 3)) actual = seccion;
      else break;
    }
    main.querySelectorAll(".indice-lateral a").forEach((a) => a.toggleAttribute("aria-current", actual && a.hash === `#${actual.id}`));
  }

  window.addEventListener(
    "scroll",
    () => {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(marcarLeccionActual);
    },
    { passive: true },
  );

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

  const ancho = window.matchMedia("(min-width: 1000px)");

  function dibujar() {
    document.title = `andamio con ${tecnologia.titulo}${variante.nombre ? ` (${variante.nombre})` : ""}`;
    const grupos = indice();
    const items = grupos.flatMap((g) => g.items);
    main.innerHTML = `${portada()}<div class="contenedor guia">
      <aside class="guia__lateral">${indiceLateral(grupos)}</aside>
      <div class="guia__contenido">${items.map(seccion).join("")}</div>
    </div>`;
    navegacion(items);
    main.querySelector("[data-indice]").open = ancho.matches;
    const inicial = variante.piezas.find((p) => p.creados.length);
    mostrarEnExplorador(inicial ? inicial.creados[0] : variante.archivos[0].ruta);
    marcarLeccionActual();
  }

  ancho.addEventListener("change", () => {
    const plegable = main.querySelector("[data-indice]");
    if (plegable) plegable.open = ancho.matches;
  });

  main.addEventListener("click", (evento) => {
    // En el celular, el índice se cierra al elegir una lección.
    if (evento.target.closest(".indice-lateral a") && !ancho.matches) main.querySelector("[data-indice]").open = false;
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
