# andamio para docentes

Cómo está armado andamio y cómo agregarle piezas o tipos de proyecto (stacks).
Todo se hace con archivos de plantilla y un diccionario por stack: el núcleo no
se toca.

## Estructura del repositorio

```
andamio/
├── cli.py              línea de comandos (argparse, mensajes en español)
├── menu.py             menú interactivo (andamio sin argumentos)
├── acciones.py         crear / nuevo / info: lo que comparten la CLI y el menú
├── exportar.py         andamio plantillas exportar + LEEME.md de cada pieza
├── nucleo/             no depende de ningún stack
│   ├── nombres.py      normalización, plural, palabras reservadas
│   ├── campos.py       "precio:decimal" -> Campo
│   ├── motor.py        reemplazo de @@marcadores@@
│   ├── plantillas.py   lectura de plantillas (paquete o .andamio/ del alumno)
│   ├── generador.py    arma el Plan a partir de una pieza y los datos
│   ├── plan.py         valida, muestra y escribe (con vuelta atrás)
│   ├── insercion.py    líneas marcador en archivos existentes
│   ├── deteccion.py    tipo de proyecto, subiendo por las carpetas
│   └── consola.py      colores, preguntas, mensajes
├── stacks/
│   ├── __init__.py     REGISTRO (orden de detección) y ORDEN_MENU
│   ├── base.py         Stack, Pieza, Insercion, Solicitud
│   ├── python.py  django.py  django_web.py  fastapi.py  express.py  web.py
│   │   react.py  vue.py  react_native.py  next.py  reflex.py
│   └── _js.py          ayudas compartidas por los stacks de JavaScript
└── plantillas/<stack>/[<variante>/]
    ├── _proyecto/      el proyecto que crea "andamio crear"
    └── <pieza>/        lo que genera "andamio nuevo <pieza>"
                        (los de JavaScript tienen las variantes ts/ y js/)
tests/unit/             núcleo, CLI, menú, control de plantillas
tests/integracion/      un archivo por stack, exportación, empaquetado, coherencia
scripts/empaquetar.py   arma andamio.pyz y el .zip de la Release
scripts/sitio.py        genera las demostraciones de la página (sitio/datos.js)
docs/guias/             guías para alumnos: comandos, combinaciones, reglas, Django + JWT, Django con plantillas
sitio/                  página web (HTML, CSS y JS sin librerías) para GitHub Pages
```

## Cómo se genera una pieza

1. Se detecta el proyecto: desde la carpeta actual hacia arriba, se prueba
   `detectar(carpeta)` de cada stack en el orden de `REGISTRO`. Gana la carpeta
   más cercana.
2. Se normaliza el nombre (`"Línea Venta"` → `["linea", "venta"]`), se valida y se
   calculan los marcadores comunes (`@@Nombre@@`, `@@plural@@`, ...).
3. Se leen los campos (`nombre:tipo`) y se validan contra `Stack.tipos`.
4. La función `contexto` de la pieza agrega sus marcadores propios (por ejemplo,
   las líneas del modelo de Django armadas en Python).
5. Se arma un **Plan**: cada archivo de `plantillas/<stack>/<pieza>/` se
   renderiza y se ubica en el proyecto con la misma ruta relativa; cada
   `Insercion` agrega líneas a un archivo existente.
6. Se valida todo junto (ningún archivo existe, ningún marcador desconocido),
   se muestra el resumen y recién ahí se escribe. Si algo falla al escribir, se
   deshace todo.

## Plantillas y marcadores

- Una plantilla es un archivo real. Su ruta dentro de la carpeta de la pieza es
  la ruta en el proyecto: `plantillas/react/componente/src/components/@@Nombre@@/@@Nombre@@.tsx`.
- `@@marcador@@` se reemplaza en el contenido y en los nombres de archivo. Un
  valor con `/` en una ruta genera subcarpetas; un valor vacío se omite.
- Si un marcador ocupa una línea él solo, cada línea del valor toma la sangría
  de esa línea, y si el valor está vacío, la línea se elimina. Así se insertan
  bloques armados en Python sin preocuparse por la sangría:

  ```python
  class @@Nombre@@(models.Model):
      @@campos_modelo@@
  ```

- Un marcador que no existe es un error (con la lista de los disponibles).
- No se usa `{{ }}` ni `${ }`: las dobles llaves de JSX y los template literals
  de JavaScript quedan intactos. Aun así, en las plantillas de React Native se
  evita escribir `{{` (se usan constantes: `options={opciones}`).
- Los archivos binarios (`.png`, fuentes) se copian sin procesar.
- `.gitignore` se guarda como `gitignore` (sin punto) y se renombra al
  generarlo; un `.gitignore` real dentro del paquete afectaría a este repo.
- El `.env` del proyecto no se guarda: se genera a partir de `.env.example`
  con los valores de `Stack.contexto_env` (en Django, una `SECRET_KEY` al azar).

Marcadores disponibles en todas las piezas (para `línea venta`):

| Marcador | Valor | Marcador | Valor |
|---|---|---|---|
| `@@Nombre@@` | `LineaVenta` | `@@Plural@@` | `LineasVenta` |
| `@@nombre@@` | `linea_venta` | `@@plural@@` | `lineas_venta` |
| `@@nombreCamel@@` | `lineaVenta` | `@@pluralCamel@@` | `lineasVenta` |
| `@@nombreKebab@@` | `linea-venta` | `@@pluralKebab@@` | `lineas-venta` |
| `@@nombreTitulo@@` | `Linea venta` | `@@titulo@@` | `Lineas venta` |

En `_proyecto/`: `@@proyecto@@` (kebab), `@@proyecto_snake@@`, `@@Proyecto@@`,
`@@proyectoTitulo@@`, `@@carpeta@@` y los de `Stack.contexto_proyecto`.

## Variantes (TypeScript / JavaScript)

Un stack puede tener variantes: otra versión de todas sus plantillas. React y
React Native tienen `ts` (la primera, que se usa por defecto) y `js`:

```python
STACK = Stack(
    ...,
    variantes={"ts": "TypeScript", "js": "JavaScript"},
    detectar_variante=_js.detectar_variante,   # "ts" si hay tsconfig.json o la dependencia typescript
    marcadores_variante={"ts": {"ext": "ts", "extx": "tsx"}, "js": {"ext": "js", "extx": "jsx"}},
)
```

- Las plantillas van en `plantillas/<stack>/<variante>/_proyecto/` y
  `plantillas/<stack>/<variante>/<pieza>/`. Cada variante tiene que tener las
  mismas piezas (hay un test que lo controla).
- La variante de un proyecto nuevo se elige con `--variante js` (o el atajo
  `--js`), y en el menú con la pregunta "¿En qué lenguaje?". En un proyecto que
  ya existe, se detecta con `detectar_variante`.
- Las rutas de la definición de la pieza (`existe_si`, `inserciones`) usan
  `@@ext@@` y `@@extx@@` para no depender de la variante:
  `existe_si=("src/hooks/use@@Nombre@@.@@ext@@",)`.
- Las plantillas exportadas (`.andamio/plantillas/<stack>/<pieza>/`) son las de la
  variante del proyecto.
- `tests/unit/test_plantillas.py` controla que las plantillas `js` no tengan
  sintaxis de TypeScript (`interface`, `: string`, `import type`...).

Para agregar una variante: creá su carpeta con todas las piezas, sumala a
`variantes` y `marcadores_variante`, y agregá sus tests (como
`tests/integracion/test_variantes_js.py`).

## Agregar una pieza

Ejemplo: una pieza `contexto` para React que genera un Context de React.

**1. Plantillas.** Creá `andamio/plantillas/react/contexto/` con los archivos,
en la misma ruta que tendrán en el proyecto:

```
andamio/plantillas/react/contexto/src/contexts/@@Nombre@@Context.tsx
```

```tsx
import { createContext, useContext, useState, type ReactNode } from 'react';

interface @@Nombre@@Valor {
  valor: string;
  setValor: (valor: string) => void;
}

const @@Nombre@@Context = createContext<@@Nombre@@Valor | null>(null);

export function @@Nombre@@Provider({ children }: { children: ReactNode }) {
  const [valor, setValor] = useState('');
  return <@@Nombre@@Context.Provider value={{ valor, setValor }}>{children}</@@Nombre@@Context.Provider>;
}

export function use@@Nombre@@() {
  const contexto = useContext(@@Nombre@@Context);
  if (!contexto) throw new Error('use@@Nombre@@ tiene que usarse dentro de <@@Nombre@@Provider>');
  return contexto;
}
```

(En React, `value={{ ... }}` no molesta: el motor solo reemplaza `@@...@@`.)

**2. Registro.** En `andamio/stacks/react.py`, definí la pieza y agregala al
diccionario `piezas`:

```python
CONTEXTO = Pieza(
    clave="contexto",
    titulo="Contexto",
    descripcion="estado compartido entre componentes (React Context)",
    ejemplo="sesion",
    formas=("@@Nombre@@Context",),
    existe_si=("src/contexts/@@Nombre@@Context.tsx",),
    siguiente_paso=["import { @@Nombre@@Provider } from './contexts/@@Nombre@@Context';"],
)

STACK = Stack(..., piezas={..., "contexto": CONTEXTO})
```

Campos de `Pieza` que más se usan:

| Campo | Para qué |
|---|---|
| `usa_campos`, `usa_plural` | la pieza recibe `nombre:tipo` / usa el plural (y avisa si el nombre parece plural) |
| `contexto` | función `(Solicitud) -> dict` con marcadores propios (bloques armados en Python) |
| `marcadores` | descripción de esos marcadores: aparecen en el `LEEME.md` al exportar |
| `existe_si` | rutas que, si existen, indican que la pieza ya se generó |
| `si_no_existe` | archivos de la plantilla que se crean solo si faltan (ej.: `http.ts`) |
| `inserciones` | líneas que se agregan a archivos existentes (ver abajo) |
| `ajustar_palabras` | ej.: quitar `use` de `useContador` para no generar `useUseContador` |
| `validar_nombre`, `campos_reservados` | nombres que romperían el código generado |
| `opciones`, `normalizar_opcion` | opciones extra (`--carpeta`, `--migrar`, `--protegido`) |
| `nombre_defecto` | la pieza no necesita nombre (`nuevo login`); el menú no lo pregunta |
| `siguiente_paso` | comandos a mostrar al final (`# ` = nota, `http...` = enlace) |
| `despues`, `confirmaciones` | acción posterior (como `--migrar`) y su pregunta en el menú |

**3. Test.** `tests/unit/test_plantillas.py` ya controla, para todas las piezas,
que exista la carpeta y que cada marcador usado esté declarado. Agregá un test
de integración mínimo en `tests/integracion/test_react.py`:

```python
def test_contexto(proyecto):
    assert main(["nuevo", "contexto", "sesion"]) == 0
    archivo = proyecto / "src/contexts/SesionContext.tsx"
    assert "export function SesionProvider(" in archivo.read_text(encoding="utf-8")
```

Si la pieza genera TypeScript, sumala a `APP_QUE_USA_TODO` en ese archivo para
que `pytest --lento` la compile.

## Insertar en archivos existentes

```python
Insercion(
    "config/settings.py",                # archivo (con marcadores)
    '"@@plural@@",',                     # texto a insertar (puede tener varias líneas)
    marcador="apps",                     # se inserta antes de la línea que contiene "andamio:apps"
    descripcion="app en LOCAL_APPS",     # se muestra en el resumen
    ubicacion="dentro de la lista LOCAL_APPS",  # se explica si falta el marcador
)
```

- Sin `marcador`, el texto se agrega al final del archivo (`crear_si_falta=True`
  crea el archivo si no existe).
- La línea marcador va en la plantilla del proyecto:
  `# --- andamio:apps (no borrar esta línea) ---` (o `//` en TypeScript, con
  `comentario="//"` en la `Insercion`). Para otros archivos: `"{/*"` (JSX), `"{#"`
  (plantillas de Django), `"<!--"` (HTML y `.vue`) y `"/*"` (CSS). Se busca por la clave `andamio:apps`,
  así que cambiar el resto del comentario no la rompe.
- El texto se inserta con la sangría de la línea marcador y no se duplica si ya
  está.
- Si falta el marcador o el archivo, la pieza se genera igual y se muestra qué
  pegar y dónde.

## Agregar un stack

1. Creá `andamio/plantillas/<clave>/_proyecto/` con el proyecto inicial y una
   carpeta por pieza.
2. Creá `andamio/stacks/<clave>.py` con una variable `STACK = Stack(...)`:
   `clave`, `titulo`, `senal` (qué archivos lo identifican, para el mensaje de
   error), `detectar(carpeta) -> bool`, `tipos` (tipo de campo → descripción),
   `piezas` y `siguiente_paso_proyecto`.
3. Registralo en `andamio/stacks/__init__.py`: en `REGISTRO`, en la posición
   correcta para la detección (lo más específico primero), y en `ORDEN_MENU`.
   Ojo con las subcarpetas: la detección sube desde la carpeta actual, así que
   una subcarpeta de tu proyecto no puede parecerse a otro stack (por ejemplo,
   `app/` de FastAPI tiene `main.py` y `db.py`, igual que un proyecto de consola:
   por eso el stack `python` mira que `main.py` no use FastAPI). Probalo con
   `buscar_proyecto(raiz / "subcarpeta")`.
4. Agregá `tests/integracion/test_<clave>.py`: crear el proyecto, generar cada
   pieza y verificar los archivos; con `@pytest.mark.lento`, instalar y compilar.
5. Sumalo a las tablas del README (hay un test que lo controla).
Un stack puede **extender** a otro con `extiende="<clave>"` (así hace
`next-fullstack` con `next`): su proyecto junta los archivos de `_proyecto` de los
dos (si se repiten, gana el suyo: por ejemplo, su `package.json`), y las piezas que
no tiene en su carpeta (componente, página, crud...) se toman de las del otro. Así
las dos formas de Next.js comparten las mismas plantillas de interfaz.

6. En la página: `sitio/<clave>.html` (copiá otra guía y cambiá
   `data-tecnologia`), el enlace en `GUIAS` de `sitio/comun.js` (el menú desplegable,
   por grupo) y en `GRUPOS` de `sitio/inicio.js` (la portada), y sus textos en
   `TECNOLOGIAS` y `DESCRIPCIONES` de `scripts/sitio.py` (los tests del sitio
   fallan hasta que esté todo).
7. En `docs/guias/comandos.md`, su sección con cada pieza (hay un test que lo controla).
8. Si cambiás `ORDEN_MENU`, cambian los números del menú: revisá los tests que
   simulan el menú (`respuestas([...])`) y `demo_menu` en `scripts/sitio.py`.

## Tests

```
python -m pip install -e ".[dev]"
python -m pytest                    # rápido: no instala nada
python -m pytest --lento            # además instala y compila los proyectos generados (Node)
```

- Los tests que ejecutan los proyectos de Django o de FastAPI se saltean si sus
  dependencias no están instaladas:
  `pip install -r andamio/plantillas/django/_proyecto/requirements.txt` (y lo mismo
  con `andamio/plantillas/fastapi/_proyecto/requirements.txt`).
- `--lento` necesita Node (22.13 o más nuevo, por Expo): `npm install` + `npm run build`
  en React, `tsc` y `expo install --check` en React Native, y los servicios de
  ambos y el `crud` en Chromium ejecutados contra la API generada en Django, en
  FastAPI **y** en Express (`tests/integracion/apis.py` levanta cualquiera de las
  tres). En Express, además, `npm install`, la migración de Prisma, `npm test` y
  `tsc` del proyecto generado, en TypeScript y en JavaScript. En Next.js, `next build`
  (que revisa los tipos), `next start` y el mismo CRUD en Chromium: el frontend
  contra FastAPI y el full stack contra su propia API (después de `npm test`). En
  Reflex, `--migrar`, `reflex run` y sus dos páginas en Chromium (`crud` con su base
  y `crud-api` contra FastAPI): necesita Reflex instalado (Python 3.11+).
- Django con plantillas (`django-web`) usa las mismas dependencias que Django
  (sin REST Framework). Sus tests generan los crud, ejecutan los tests generados y
  arman cada página con el cliente de pruebas de Django. El login con JWT necesita
  `djangorestframework-simplejwt` (se saltea si no está).
- La web HTML (`web`) no compila: `node --check` revisa la sintaxis de cada `.js` y
  las combinaciones controlan que cada `import` apunte a un archivo que existe.
  Vue, con `--lento`, hace `npm install` y `npm run build`.
- Las tres APIs cumplen el mismo contrato: rutas `/api/<plural>/` con barra final,
  lista sin paginación, decimales como número, fechas con hora en hora local con su
  zona, errores 400 `{campo: [mensajes]}` en español, 404 `{"detail": ...}`, 204 al
  eliminar, y `?search=`, `?ordering=` y `?campo=valor`, en el puerto 8000. Si
  cambiás una, cambiá las otras: `test_coherencia.py` y `test_crud_navegador.py` lo
  controlan.
- El CI (GitHub Actions) corre los tests en Ubuntu y Windows con Python 3.10 y
  3.13, y un trabajo aparte con `--lento`.

## Actualizar versiones de las dependencias

- Django: `andamio/plantillas/django/_proyecto/requirements.txt`. Tienen que
  funcionar con Python 3.10 (Django 6 ya pide 3.12).
- FastAPI: `andamio/plantillas/fastapi/_proyecto/requirements.txt`, también con
  Python 3.10. `fastapi-offline` sirve la documentación (`/docs`) sin internet.
- Next.js: `andamio/plantillas/next/{ts,js}/_proyecto/package.json` y el de
  `next-fullstack`. Guiarse por `npx create-next-app@<versión>`, pero sin
  `next/font/google` (descarga fuentes al compilar: falla sin internet). Next.js
  usa TypeScript 5.x (no la 7). Las APIs aceptan pedidos de `localhost:3000` (CORS).
- Reflex: `andamio/plantillas/reflex/_proyecto/requirements.txt`. Cambia rápido
  (0.9, 0.10 y 0.11 salieron en dos meses): después de actualizarlo, ejecutá
  `python -m pytest --lento tests/integracion/test_reflex.py`. No uses `rx.Model`
  (obsoleto desde 0.9.2): los modelos son de SQLModel directamente. La parte de
  Python de Reflex usa el puerto 8001, para dejar el 8000 a las APIs de andamio.
- Express: `andamio/plantillas/express/{ts,js}/_proyecto/package.json` (versiones
  exactas). Ojo: en npm, `prisma@latest` puede apuntar a una versión candidata
  (`8.0.0-rc...`); usá la última estable (`npm view prisma dist-tags`). Prisma 7
  no genera el cliente al migrar: por eso los scripts `postinstall`, `predev` y
  `pretest` ejecutan `prisma generate`. Los tests de los proyectos usan `test.db`,
  que `npm test` borra y vuelve a crear con `prisma db push` (sin `--force-reset`,
  que Prisma bloquea cuando lo ejecuta un asistente de IA).
- React: `andamio/plantillas/react/_proyecto/package.json` (versiones exactas;
  guiarse por la plantilla oficial `npm create vite@latest -- --template react-ts`).
- Vue: `andamio/plantillas/vue/_proyecto/package.json` (versiones exactas; guiarse por
  `npm create vue@latest`). Misma versión de Vite que React.
- Login de Django: `VERSION_SIMPLEJWT` en `andamio/stacks/django.py` (se agrega al
  `requirements.txt` del proyecto con `nuevo login`).
- React Native: `andamio/plantillas/react-native/_proyecto/package.json`, todas
  del mismo SDK de Expo (`bundledNativeModules.json` del paquete `expo`).

Después, `python -m pytest --lento` confirma que todo instala y compila.

## Publicar una versión

1. Cambiá `__version__` en `andamio/__init__.py` (versionado semántico: un
   cambio que rompe algo sube el MAYOR, algo nuevo el MENOR, una corrección el PARCHE).
2. En `CHANGELOG.md`, pasá lo de "Sin publicar" a una sección `## [X.Y.Z] - fecha`.
3. En `README.md`, actualizá la dirección de instalación (`.../vX.Y.Z/andamio-X.Y.Z-py3-none-any.whl`).
   Un test falla si te olvidás.
4. Subí los cambios y creá el tag, de una de estas dos formas:
   - Con git:

     ```
     git tag vX.Y.Z
     git push origin vX.Y.Z
     ```

   - Desde la web: en el repositorio, **Releases → Draft a new release →
     Choose a tag**, escribí `vX.Y.Z`, elegí "Create new tag", dejá el título y
     la descripción vacíos y tocá **Publish release**.

El workflow `Release` verifica que el tag coincida con `__version__`, corre los
tests, arma el `.whl`, `andamio.pyz` y el `.zip`, los prueba y publica la
Release con las notas del `CHANGELOG.md`. El enlace
`https://github.com/rodal95/andamio/releases/latest/download/andamio.pyz`
siempre apunta a la última versión.

## Página web

La página `https://rodal95.github.io/andamio/` está en `sitio/` (HTML, CSS y
JavaScript, sin librerías):

| Archivo | Qué es |
|---|---|
| `index.html` + `inicio.js` | portada: menú animado, elegir tecnología, instalar, cómo se escriben los comandos |
| `python.html`, `django.html`, `django-web.html`, `fastapi.html`, `express.html`, `web.html`, `react.html`, `vue.html`, `react-native.html`, `next.html`, `next-fullstack.html`, `reflex.html` | una guía por tecnología, armada por `tecnologia.js` |
| `comun.js` | utilidades compartidas: barra (con el menú desplegable de guías, `GUIAS`), colores de la terminal, resaltado de código, visor de archivos |
| `datos.js` | lo genera `scripts/sitio.py` (no se versiona) |
| `img/` | capturas de los proyectos funcionando (las genera `scripts/capturas_sitio.py`) |
| `ejemplos/` | el código de las combinaciones de cada guía (lo que escribe el alumno), en TypeScript y JavaScript |

Cada guía tiene un índice lateral (en el celular, plegable arriba) que sigue la
línea: **Empezar** (instalar, crear el proyecto, ponerlo en marcha), **Paso a paso**
(una lección por pieza, en el orden de `CAMINO`, con temas como el router
intercalados), **Combinaciones** (recetas que usan varias piezas juntas, con su
código) y **Referencia** (el proyecto completo, todos los comandos y problemas
comunes). Cada lección termina con enlaces a la anterior y la siguiente. Las guías de
las tecnologías con variantes tienen un selector TypeScript / JavaScript.

**Nada se escribe a mano.** `scripts/sitio.py` ejecuta andamio de verdad: crea un
proyecto de cada tipo y variante, genera cada pieza, simula una sesión del menú y
ejecuta la app de consola generada. Lo que cambia en las plantillas aparece solo en
la página. Lo único escrito a mano en ese archivo es:

- `TECNOLOGIAS`: el comando de ejemplo de cada pieza, para qué sirve y cómo se usa.
- `DESCRIPCIONES` y `CARPETAS`: para qué sirve cada archivo generado. **Si agregás
  un archivo a una plantilla, agregale su descripción**: hay un test que falla si
  algún archivo generado queda sin explicación.
- `CAMINO`: el orden de las lecciones de cada guía (el índice lateral). Tiene que
  tener todas las piezas del stack (hay un test); `"tema:router"` intercala una
  lección de un concepto, definida en `TEMAS`, que muestra archivos reales del
  proyecto (si un archivo deja de existir, `sitio.py` falla).
- `COMBINACIONES`: las recetas del final de cada guía (página + servicio, componente
  con datos, hook propio...). Su código está en `sitio/ejemplos/<tecnología>/<ts|js>/`,
  numerado por paso, porque cada receta se arma sobre la anterior.
  `tests/integracion/test_combinaciones.py` arma el proyecto como dice la guía, aplica
  cada receta y compila después de cada una (`npm run build`, `tsc`, `reflex compile`
  o la ejecución, según la tecnología). **Si cambiás una plantilla, ese test te avisa
  si alguna receta dejó de funcionar.**

El workflow `Sitio` ejecuta `scripts/sitio.py` y publica la página cada vez que
cambia algo en `sitio/` o en `andamio/`.

**Capturas.** `scripts/capturas_sitio.py` genera los proyectos, los pone en marcha
(API de Django con datos y panel de administración, APIs de FastAPI y de Express
con su Swagger, webs de React y Next.js compiladas, Next.js full stack, Reflex, app de
Expo exportada para web) y les saca fotos con Chromium. Se ejecuta a mano cuando cambia cómo se ven los proyectos, y las imágenes
se suben al repositorio. Necesita las dependencias de Django y de FastAPI en ese
Python, Node 22.13+ y Playwright para Node.

```
python scripts/capturas_sitio.py
```

Para ver la página en tu PC:

```
python scripts/sitio.py
cd sitio
python -m http.server
```

y abrí http://localhost:8000.
