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
│   ├── python.py  django.py  react.py  react_native.py
│   └── _js.py          ayudas compartidas por react y react-native
└── plantillas/<stack>/
    ├── _proyecto/      el proyecto que crea "andamio crear"
    └── <pieza>/        lo que genera "andamio nuevo <pieza>"
tests/unit/             núcleo, CLI, menú, control de plantillas
tests/integracion/      un archivo por stack, exportación, empaquetado, coherencia
scripts/empaquetar.py   arma andamio.pyz y el .zip de la Release
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
| `opciones`, `normalizar_opcion` | opciones extra (`--carpeta`, `--migrar`) |
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
  `comentario="//"` en la `Insercion`). Se busca por la clave `andamio:apps`,
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
4. Agregá `tests/integracion/test_<clave>.py`: crear el proyecto, generar cada
   pieza y verificar los archivos; con `@pytest.mark.lento`, instalar y compilar.
5. Sumalo a las tablas del README (hay un test que lo controla).

## Tests

```
python -m pip install -e ".[dev]"
python -m pytest                    # rápido: no instala nada
python -m pytest --lento            # además instala y compila los proyectos generados (Node)
```

- Los tests de Django que ejecutan `manage.py` se saltean si Django no está
  instalado: `pip install -r andamio/plantillas/django/_proyecto/requirements.txt`.
- `--lento` necesita Node (22.13 o más nuevo, por Expo): `npm install` + `npm run build`
  en React, `tsc` y `expo install --check` en React Native, y los servicios de
  ambos ejecutados contra la API generada en Django.
- El CI (GitHub Actions) corre los tests en Ubuntu y Windows con Python 3.10 y
  3.13, y un trabajo aparte con `--lento`.

## Actualizar versiones de las dependencias

- Django: `andamio/plantillas/django/_proyecto/requirements.txt`. Tienen que
  funcionar con Python 3.10 (Django 6 ya pide 3.12).
- React: `andamio/plantillas/react/_proyecto/package.json` (versiones exactas;
  guiarse por la plantilla oficial `npm create vite@latest -- --template react-ts`).
- React Native: `andamio/plantillas/react-native/_proyecto/package.json`, todas
  del mismo SDK de Expo (`bundledNativeModules.json` del paquete `expo`).

Después, `python -m pytest --lento` confirma que todo instala y compila.

## Publicar una versión

1. Cambiá `__version__` en `andamio/__init__.py` (versionado semántico: un
   cambio que rompe algo sube el MAYOR, algo nuevo el MENOR, una corrección el PARCHE).
2. En `CHANGELOG.md`, pasá lo de "Sin publicar" a una sección `## [X.Y.Z] - fecha`.
3. En `README.md`, actualizá la dirección de instalación (`.../vX.Y.Z/andamio-X.Y.Z-py3-none-any.whl`).
   Un test falla si te olvidás.
4. Subí los cambios, y después el tag:

   ```
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

El workflow `Release` verifica que el tag coincida con `__version__`, corre los
tests, arma el `.whl`, `andamio.pyz` y el `.zip`, los prueba y publica la
Release con las notas del `CHANGELOG.md`. El enlace
`https://github.com/rodal95/andamio/releases/latest/download/andamio.pyz`
siempre apunta a la última versión.
