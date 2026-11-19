# andamio

Genera el código repetitivo de tus proyectos (carpetas, tablas, menús, APIs,
componentes, pantallas) para que te concentres en la lógica. Funciona con
**Python + SQLite**, **Django REST**, **React** y **React Native (Expo)**.

**Instalar en Windows** (en CMD o PowerShell):

```
py -m pip install https://github.com/rodal95/andamio/releases/download/v1.0.0/andamio-1.0.0-py3-none-any.whl
```

En Linux o Mac: `python3 -m pip install` con la misma dirección.
¿No podés instalar? Descargá [andamio.pyz](https://github.com/rodal95/andamio/releases/latest/download/andamio.pyz)
y escribí `py andamio.pyz` en lugar de `andamio`.

**Usar:**

```
andamio                            menú: te pregunta todo, paso a paso
andamio crear django mi-api        crea un proyecto nuevo
andamio nuevo recurso producto nombre:str precio:decimal stock:int
```

¿`andamio` no se reconoce? Usá `py -m andamio` (ver [preguntas frecuentes](#preguntas-frecuentes)).

---

## Qué podés crear y generar

Con `andamio crear <tipo> <nombre>` creás un proyecto. Adentro del proyecto,
`andamio nuevo <pieza> <nombre>` agrega piezas. Para ver qué se puede generar
en tu proyecto, escribí `andamio info`.

| Tipo de proyecto | `crear` | Piezas (`nuevo`) |
|---|---|---|
| Python + SQLite (consola) | `python` | `entidad` |
| Django REST | `django` | `recurso` |
| React + Vite | `react` | `componente`, `pagina`, `hook`, `servicio` |
| React Native + Expo | `react-native` | `pantalla`, `componente`, `hook`, `servicio` |

Ejemplos:

```
andamio nuevo entidad cliente nombre:str telefono:str
andamio nuevo componente Tarjeta
andamio nuevo pantalla detalle-producto --carpeta productos
andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

Opciones útiles:

- `--simular`: muestra qué archivos crearía o modificaría, sin tocar nada.
- `--plural`: indica el plural cuando el automático no sirve (`--plural paises`).
- `--migrar` (Django): ejecuta `makemigrations` y `migrate` después de generar el recurso.
- `--carpeta` (React Native): crea la pantalla dentro de una carpeta de `app/`.

Los nombres se escriben como quieras (`Línea Venta`, `linea-venta`) y andamio
los adapta (`LineaVenta`, `linea_venta`). Van **en singular**: `producto`, no `productos`.

## Tipos de campo

Los campos se escriben `nombre:tipo`. Si no ponés el tipo, se usa `str`.

| Tipo | Python + SQLite | Django, React y React Native |
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

**Para que React o React Native usen tu API de Django**, generá el servicio con
**los mismos campos** que el recurso:

```
andamio nuevo recurso producto nombre:str precio:decimal     (en el proyecto Django)
andamio nuevo servicio producto nombre:str precio:decimal    (en el proyecto React)
```

## Modificar el código que se genera

```
andamio plantillas exportar
```

Copia las plantillas a `.andamio/plantillas/` dentro de tu proyecto. Si las
modificás, andamio usa tu versión. Cada carpeta tiene un `LEEME.md` que explica
los marcadores `@@...@@` que podés usar. Para volver a la original, borrá la carpeta.

## Preguntas frecuentes

**"andamio" no se reconoce como un comando.**
Windows no encuentra el programa porque la carpeta donde se instaló no está en
el PATH. Usá `py -m andamio` en su lugar: hace lo mismo
(`py -m andamio nuevo recurso producto nombre:str`).

**"pip" o "py" no se reconocen.**
Probá con `python -m pip install ...` y `python -m andamio`. Si tampoco funciona,
falta instalar Python (python.org, versión 3.10 o más nueva).

**No tengo permisos de administrador / no tengo internet en el laboratorio.**
Descargá `andamio.pyz` desde la [última versión](https://github.com/rodal95/andamio/releases/latest)
(en un pendrive, si hace falta) y usalo así: `py C:\ruta\andamio.pyz crear python mi-tienda`.
No necesita instalación ni internet.

**Dice "No encontré un proyecto".**
Tenés que estar dentro de la carpeta del proyecto (o de una subcarpeta). Entrá con
`cd mi-proyecto`. Si todavía no lo creaste: `andamio crear <tipo> <nombre>`.

**Dice que los archivos ya existen.**
andamio nunca sobrescribe archivos. Elegí otro nombre o borrá los archivos que
generaste antes.

**Borré una línea que decía `andamio:... (no borrar esta línea)`.**
No pasa nada grave: andamio genera igual los archivos y te muestra exactamente qué
línea pegar y en qué archivo. Si querés, volvé a escribir la línea marcador.

**La app de React Native no se conecta a Django.**
En el emulador de Android, tu PC es `10.0.2.2` (ya viene configurado en `.env`).
En un celular real, poné la IP de tu PC en `EXPO_PUBLIC_API_URL`, agregala a
`ALLOWED_HOSTS` en el `.env` de Django y ejecutá `python manage.py runserver 0.0.0.0:8000`.

**El servicio da error 400.**
Los campos del servicio no coinciden con los del recurso de Django. El error
dice qué campo falta o está mal.

**`npm install` falla.**
Revisá la versión de Node con `node --version`: React necesita 20.19 o más
nueva, y React Native (Expo) necesita 22.13 o más nueva.

**¿Cómo actualizo andamio?**
Repetí el comando de instalación con la dirección de la versión nueva, que está
en [Releases](https://github.com/rodal95/andamio/releases).

---

Página con demostraciones: https://rodal95.github.io/andamio/
Para docentes: cómo agregar piezas o tipos de proyecto en [docs/docente.md](docs/docente.md).
Cambios de cada versión en [CHANGELOG.md](CHANGELOG.md).
Licencia [MIT](LICENSE): podés usarlo, modificarlo y compartirlo libremente.
