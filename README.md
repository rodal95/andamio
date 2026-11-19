# andamio

Genera el código repetitivo de tus proyectos (carpetas, tablas, menús, APIs,
componentes, pantallas) para que te concentres en la lógica. Funciona con
**Python + SQLite**, **Django** (API REST con login JWT, o sitio con plantillas), **FastAPI**,
**Express**, **HTML + CSS + JS**, **React**, **Vue**, **React Native (Expo)**, **Next.js** y **Reflex**.

**Instalar** (en Windows, en CMD o PowerShell):

```
python -m pip install https://github.com/rodal95/andamio/releases/download/v1.3.0/andamio-1.3.0-py3-none-any.whl
```

En Linux o Mac, escribí `python3` en lugar de `python`.

**Usar.** andamio es un programa de Python: los comandos empiezan con `python -m andamio`
y así funcionan en cualquier PC.

```
python -m andamio                            menú: te pregunta todo, paso a paso
python -m andamio crear django mi-api        crea un proyecto nuevo
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int
```

¿No podés instalar? Descargá [andamio.pyz](https://github.com/rodal95/andamio/releases/latest/download/andamio.pyz)
y usá `python andamio.pyz` en lugar de `python -m andamio`.

---

## Qué podés crear y generar

Con `python -m andamio crear <tipo> <nombre>` creás un proyecto. Adentro del proyecto
(en cualquier subcarpeta), `python -m andamio nuevo <pieza> <nombre>` agrega piezas. Para ver qué se puede generar
en tu proyecto, escribí `python -m andamio info`.

| Tipo de proyecto | `crear` | Piezas (`nuevo`) |
|---|---|---|
| Python + SQLite (consola) | `python` | `entidad` |
| Django REST (API) | `django` | `recurso`, `login` |
| Django con plantillas (sitio, monolito) | `django-web` | `crud`, `pagina` |
| FastAPI + SQLModel | `fastapi` | `recurso` |
| Express + Prisma (TS o JS) | `express` | `recurso` |
| HTML + CSS + JavaScript (sin instalar nada) | `web` | `pagina`, `componente`, `servicio`, `crud` |
| React + Vite | `react` | `componente`, `pagina`, `hook`, `servicio`, `crud` |
| Vue + Vite | `vue` | `componente`, `pagina`, `composable`, `servicio`, `crud` |
| React Native + Expo | `react-native` | `pantalla`, `componente`, `hook`, `servicio` |
| Next.js, frontend que usa una API | `next` | `componente`, `pagina`, `hook`, `servicio`, `crud` |
| Next.js full stack (API y base propias) | `next-fullstack` | `recurso`, `crud`, `pagina`, `componente`, `hook`, `servicio` |
| Reflex (web solo con Python) | `reflex` | `crud`, `crud-api`, `pagina`, `componente`, `estado`, `servicio` |

**Guías paso a paso** (en [docs/guias/](docs/guias/README.md)): [todos los comandos con
ejemplos](docs/guias/comandos.md), [cómo combinar piezas y proyectos](docs/guias/combinaciones.md),
[reglas para no romper nada](docs/guias/reglas.md), [API con Django + login JWT](docs/guias/django-api-jwt.md)
y [sitio con Django y plantillas](docs/guias/django-plantillas.md).

**`crud` (React, Vue y Next.js):** con un comando genera la lista, el detalle (con eliminar) y el
formulario para crear y editar, conectados a la API (Django, FastAPI o Express) y con sus rutas
(`/productos`, `/productos/nuevo`, `/productos/3`, `/productos/3/editar`). Las
páginas usan el servicio; el componente `ProductoDetalle` solo muestra los datos y
avisa con `onEditar` / `onEliminar`. Cada `pagina` también queda con su ruta y su
enlace en el menú.

**Django REST con login:** `python -m andamio nuevo login` agrega el registro de usuarios y
los tokens JWT (SimpleJWT: `/api/token/`, `/api/token/refresh/`, `/api/registro/`, `/api/yo/`).
Un recurso generado con `--protegido` deja leer a cualquiera, pero crear, modificar y eliminar
piden el token (`Authorization: Bearer <token>`).

**Django con plantillas (`django-web`):** la otra forma de usar Django, sin frontend aparte:
el servidor arma las páginas HTML. Trae login, registro y admin. `crud` genera la app con modelo,
formulario, cinco vistas (lista, detalle, crear, editar y eliminar), sus plantillas, rutas, admin y
tests, y el enlace en el menú; `pagina` una plantilla con su ruta. `--protegido` pide iniciar sesión.

**HTML + CSS + JavaScript (`web`):** sin Node ni npm. Cada `pagina` es un `.html` con su `.js`;
`servicio` y `crud` usan una API de andamio. Se ve con `python -m http.server 5173`.

**Next.js full stack:** `recurso` crea la API en `app/api/` (Route Handlers, con su
tabla de Prisma) y `crud` las páginas que la usan; generalos con los mismos campos.
La API tiene la misma forma que las otras, así que también la puede usar React Native.

**Reflex:** la web se escribe solo en Python. `crud` guarda los datos en su propia base
(con migraciones) y `crud-api` muestra los de una API hecha con andamio (Django, FastAPI
o Express). Necesita Python 3.11 o más nuevo, y la primera vez que se ejecuta descarga lo
que usa para el navegador (hace falta internet).

React, React Native, Express y Next.js se crean en **TypeScript** (por defecto) o en
**JavaScript** con `--js`: `python -m andamio crear react mi-web --js`. En un proyecto que ya existe (por
ejemplo, uno creado con `npm create vite`), andamio se da cuenta solo: si tiene
`tsconfig.json` genera `.tsx`; si no, `.jsx`.

Ejemplos:

```
python -m andamio nuevo entidad cliente nombre:str telefono:str
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int
python -m andamio nuevo pantalla detalle-producto --carpeta productos
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

**En inglés:** los comandos, las piezas y las opciones también se escriben en inglés
(`create`, `new`, `resource`, `page`, `--dry-run`, `--migrate`...):
`python -m andamio new resource product name:str --plural products`. Para ver el árbol
completo de comandos, opciones y piezas: `python -m andamio comandos` (o `commands`), o
[la guía de comandos](docs/guias/comandos.md#el-árbol-de-comandos).

Opciones útiles:

- `--simular`: muestra qué archivos crearía o modificaría, sin tocar nada.
- `--plural`: indica el plural cuando el automático no sirve (`--plural paises`).
- `--protegido` (Django y Django con plantillas): crear, modificar y eliminar piden login.
- `--migrar` (Django, Django con plantillas, Express, Next.js full stack y Reflex): después de generar el recurso, crea
  y aplica la migración (`makemigrations` y `migrate` en Django, `npx prisma migrate dev` en
  Express y Next.js, `reflex db` en Reflex).
- `--carpeta` (React Native): crea la pantalla dentro de una carpeta de `app/`.

Los nombres se escriben como quieras (`Línea Venta`, `linea-venta`) y andamio
los adapta (`LineaVenta`, `linea_venta`). Van **en singular**: `producto`, no `productos`.

## Tipos de campo

Los campos se escriben `nombre:tipo`. Si no ponés el tipo, se usa `str`.

| Tipo | Python + SQLite | Todos los demás (Django, FastAPI, Express, HTML, React, Vue, React Native, Next.js y Reflex) |
|---|---|---|
| `str` | texto | texto corto (hasta 200 caracteres) |
| `text` | — | texto largo |
| `int` | número entero | número entero |
| `decimal` | — | número con 2 decimales exactos (precios) |
| `float` | número con decimales | número con decimales |
| `bool` | — | verdadero o falso |
| `date` | — | fecha (`2025-03-15`) |
| `datetime` | — | fecha y hora |
| `email` | — | correo electrónico |

**Para que una web o una app usen tu API** (HTML, React, Vue, Next.js, React Native o Reflex),
generá el servicio (o el `crud`) con **los mismos campos** que el recurso:

```
python -m andamio nuevo recurso producto nombre:str precio:decimal     (en la API: Django, FastAPI o Express)
python -m andamio nuevo servicio producto nombre:str precio:decimal    (en la web o la app)
```

Las APIs de Django, FastAPI y Express que genera andamio responden igual (mismas
rutas `/api/productos/` en el puerto 8000, mismos errores en español), así que el
frontend funciona con cualquiera de las tres sin cambiar nada.

## Modificar el código que se genera

```
python -m andamio plantillas exportar
```

Copia las plantillas a `.andamio/plantillas/` dentro de tu proyecto. Si las
modificás, andamio usa tu versión. Cada carpeta tiene un `LEEME.md` que explica
los marcadores `@@...@@` que podés usar. Para volver a la original, borrá la carpeta.

## Preguntas frecuentes

**¿Por qué `python -m andamio` y no solo `andamio`?**
`python -m andamio` funciona en cualquier PC. Si querés escribir solo `andamio`,
ejecutá una vez `python -m andamio configurar`: agrega la carpeta de andamio al
PATH de tu usuario (sin permisos de administrador). Después cerrá la terminal (y
VS Code, si lo usás) y abrí una nueva. Es opcional.

**"python" no se reconoce como un comando.**
Probá con `py` en lugar de `python` (`py -m pip install ...`, `py -m andamio`).
Si tampoco funciona, falta instalar Python (python.org o Microsoft Store, versión
3.10 o más nueva).

**No tengo permisos de administrador / no tengo internet en el laboratorio.**
Descargá `andamio.pyz` desde la [última versión](https://github.com/rodal95/andamio/releases/latest)
(en un pendrive, si hace falta) y usalo así: `python C:\ruta\andamio.pyz crear python mi-tienda`.
No necesita instalación ni internet.

**Dice "No encontré un proyecto".**
Tenés que estar dentro de la carpeta del proyecto (o de una subcarpeta). Entrá con
`cd mi-proyecto`. Si todavía no lo creaste: `python -m andamio crear <tipo> <nombre>`.

**Cambié `prisma/schema.prisma` (Express o Next.js) y la API no ve el cambio.**
Creá una migración con `npx prisma migrate dev --name <qué cambió>` y volvé a
ejecutar `npm run dev` (genera el cliente de Prisma de nuevo).

**Cambié un modelo de FastAPI y la tabla no tiene el campo nuevo.**
El proyecto de FastAPI no tiene migraciones: las tablas se crean al arrancar, pero
no se modifican. Mientras desarrollás, borrá `datos.db` y volvé a arrancar la API
(se pierden los datos de prueba).

**Dice que los archivos ya existen.**
python -m andamio nunca sobrescribe archivos. Elegí otro nombre o borrá los archivos que
generaste antes.

**Borré una línea que decía `andamio:... (no borrar esta línea)`.**
No pasa nada grave: andamio genera igual los archivos y te muestra exactamente qué
línea pegar y en qué archivo. Si querés, volvé a escribir la línea marcador.

**La app de React Native no se conecta a la API.**
En el emulador de Android, tu PC es `10.0.2.2` (ya viene configurado en `.env`).
En un celular real, poné la IP de tu PC en `EXPO_PUBLIC_API_URL` y hacé que la API
escuche en la red: en Django, agregá la IP a `ALLOWED_HOSTS` en su `.env` y ejecutá
`python manage.py runserver 0.0.0.0:8000`; en FastAPI, `python -m uvicorn app.main:app --reload --host 0.0.0.0`;
Express ya escucha en la red.

**El servicio da error 400.**
Los campos del servicio no coinciden con los del recurso de la API. El error
dice qué campo falta o está mal.

**La página HTML queda en blanco o dice "Cannot use import statement".**
No la abras con doble clic: serví la carpeta con `python -m http.server 5173` y abrí
http://localhost:5173 (los `import` de JavaScript necesitan un servidor).

**La API responde 401 o 403 al crear.**
El recurso se generó con `--protegido`: hay que mandar el token del login
(`Authorization: Bearer <token>`). Pedilo con `POST /api/token/`; en Swagger, con el botón
Authorize. Las webs de andamio lo mandan solas si lo guardaste (en React, Vue y Next.js, con
`guardarToken()` de `services/http`). Ver [la guía de Django + JWT](docs/guias/django-api-jwt.md).

**`npm install` falla.**
Revisá la versión de Node con `node --version`: React y Vue necesitan 20.19 o más
nueva, Next.js 20.9 (22.12 el full stack), Express 22.12, y React Native (Expo) 22.13.

**¿Cómo actualizo andamio?**
Repetí el comando de instalación con la dirección de la versión nueva, que está
en [Releases](https://github.com/rodal95/andamio/releases).

---

Página con demostraciones: https://rodal95.github.io/andamio/
Para docentes: cómo agregar piezas o tipos de proyecto en [docs/docente.md](docs/docente.md).
Cambios de cada versión en [CHANGELOG.md](CHANGELOG.md).
Licencia [MIT](LICENSE): podés usarlo, modificarlo y compartirlo libremente.
