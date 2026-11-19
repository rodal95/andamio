"""Genera sitio/datos.js con demostraciones reales de andamio para la página web.

    python scripts/sitio.py

Ejecuta andamio de verdad (crea un proyecto de cada tipo y variante, genera cada
pieza, simula una sesión del menú y ejecuta la app de consola generada) y guarda
lo que muestra la terminal y los archivos que genera, con una explicación de para
qué sirve cada uno. Así la página nunca muestra algo distinto de lo que hace la
herramienta. El workflow del sitio lo ejecuta antes de publicar.

Las capturas de pantalla de los proyectos funcionando (sitio/img/) las genera
scripts/capturas_sitio.py, que necesita Django, Node y Chromium.
"""

from __future__ import annotations

import base64
import builtins
import contextlib
import fnmatch
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import andamio  # noqa: E402
from andamio import stacks  # noqa: E402
from andamio.cli import main  # noqa: E402
from andamio.nucleo import consola  # noqa: E402
from andamio.nucleo.generador import contexto_proyecto, pasos_proyecto  # noqa: E402

DESTINO = RAIZ / "sitio" / "datos.js"

# Los comandos se muestran siempre con Python adelante: funcionan en cualquier PC.
PROGRAMA = "python -m andamio"

# La demo se ejecuta en una carpeta temporal; en la página se muestra una ruta
# típica de un alumno en Windows.
CARPETA_EJEMPLO = "C:\\Users\\alumno"
_base_actual = ""

# --- Qué se muestra de cada tecnología ---------------------------------------------------

# Por pieza: el comando de ejemplo, para qué sirve y cómo se usa lo generado (lo que
# escribe el alumno después).
TECNOLOGIAS = {
    "python": {
        "carpeta": "mi-tienda",
        "resumen": "Aplicación de consola con menús y una base de datos SQLite. Ideal para aprender CRUD y SQL sin instalar nada más que Python.",
        "requisitos": ["Python 3.10 o más nuevo"],
        "piezas": {
            "entidad": {
                "comando": "nuevo entidad producto nombre:str precio:float stock:int",
                "explicacion": "Una entidad es una tabla de la base de datos con todo lo necesario para usarla: las funciones para guardar, listar, buscar, modificar y borrar registros, y un menú de consola para hacerlo desde el teclado. Aparece sola como opción del menú principal.",
                "uso": 'from entidades import producto\n\nnuevo_id = producto.crear("Yerba", 1500.0, 10)\nfor fila in producto.listar():\n    print(fila["nombre"], fila["precio"])',
                "uso_lenguaje": "python",
            },
        },
        "extra": [
            ("python main.py", "Ejecuta la aplicación: muestra el menú principal."),
        ],
    },
    "django": {
        "carpeta": "mi-api",
        "resumen": "API REST con Django y Django REST Framework, con documentación interactiva (Swagger), panel de administración y tests. Es el backend que usan las apps de React y React Native.",
        "requisitos": ["Python 3.10 o más nuevo"],
        "piezas": {
            "recurso": {
                "comando": "nuevo recurso producto nombre:str precio:decimal stock:int",
                "explicacion": "Un recurso es una tabla publicada como API: con un solo comando tenés /api/productos/ para listar, crear, ver, modificar y eliminar, con filtros, búsqueda y orden. Además queda en el panel /admin/ y trae 5 tests automáticos.",
                "uso": "GET    /api/productos/                  lista (un array JSON)\nPOST   /api/productos/                  crea\nGET    /api/productos/1/                ve uno\nPATCH  /api/productos/1/                modifica\nDELETE /api/productos/1/                elimina\n\nGET    /api/productos/?search=yerba     busca\nGET    /api/productos/?ordering=-precio ordena\nGET    /api/productos/?stock=10         filtra",
                "uso_lenguaje": "texto",
            },
        },
        "extra": [
            ("python -m venv .venv", "Crea el entorno virtual del proyecto (una sola vez)."),
            (".venv\\Scripts\\activate", "Activa el entorno virtual en Windows (en Linux o Mac: source .venv/bin/activate)."),
            ("pip install -r requirements.txt", "Instala Django y las demás librerías."),
            ("python manage.py makemigrations productos", "Prepara los cambios de la base de datos de una app."),
            ("python manage.py migrate", "Aplica los cambios a la base de datos."),
            ("python manage.py runserver", "Levanta la API en http://127.0.0.1:8000"),
            ("python manage.py test", "Ejecuta los tests de todas las apps."),
            ("python manage.py createsuperuser", "Crea un usuario para entrar al panel /admin/."),
        ],
    },
    "react": {
        "carpeta": "mi-web",
        "resumen": "Aplicación web con React y Vite, en TypeScript o JavaScript. Genera componentes, páginas, hooks y servicios para usar la API de Django.",
        "requisitos": ["Node.js 20.19 o más nuevo", "Python 3.10 o más nuevo (para andamio)"],
        "piezas": {
            "componente": {
                "comando": "nuevo componente Tarjeta",
                "explicacion": "Un componente es una parte reutilizable de la interfaz: una tarjeta, un botón, un formulario. Se genera con sus propios estilos, que no afectan al resto de la página, y queda exportado para importarlo desde cualquier lado.",
                "uso": "import { Tarjeta } from './components';\n\n<Tarjeta>\n  <h3>Yerba</h3>\n  <p>$ 1500</p>\n</Tarjeta>",
                "uso_lenguaje": "ts",
            },
            "pagina": {
                "comando": "nuevo pagina Productos",
                "explicacion": "Una página es una pantalla completa de la aplicación (inicio, listado, detalle). Se genera en src/pages/ con sus estilos.",
                "uso": "import { ProductosPage } from './pages/ProductosPage';\n\nfunction App() {\n  return <ProductosPage />;\n}",
                "uso_lenguaje": "ts",
            },
            "hook": {
                "comando": "nuevo hook contador",
                "explicacion": "Un hook guarda estado y lógica para reutilizarlos en varios componentes. andamio arma el esqueleto (el valor, cambiarlo y reiniciarlo) para que le agregues tu lógica.",
                "uso": "import { useContador } from './hooks/useContador';\n\nconst { valor, setValor, reiniciar } = useContador(0);\n<button onClick={() => setValor(valor + 1)}>{valor}</button>",
                "uso_lenguaje": "ts",
            },
            "servicio": {
                "comando": "nuevo servicio producto nombre:str precio:decimal stock:int",
                "explicacion": "Un servicio conecta la aplicación con un recurso de la API de Django: funciones para listar, obtener, crear, modificar y eliminar. Generalo con los mismos campos que el recurso de Django.",
                "uso": "import { productoService } from './services/productoService';\n\nconst productos = await productoService.listar();\nawait productoService.crear({ nombre: 'Yerba', precio: 1500, stock: 10 });\nawait productoService.actualizar(1, { stock: 7 });",
                "uso_lenguaje": "ts",
            },
        },
        "extra": [
            ("npm install", "Instala las dependencias (una vez, o cuando cambia package.json)."),
            ("npm run dev", "Levanta la aplicación en http://localhost:5173 y la recarga cada vez que guardás."),
            ("npm run build", "Arma la versión final en la carpeta dist/ (en TypeScript, además controla los tipos)."),
        ],
    },
    "react-native": {
        "carpeta": "mi-app",
        "resumen": "Aplicación móvil con Expo y Expo Router, en TypeScript o JavaScript. Se prueba en el emulador de Android, en el navegador o en tu celular con Expo Go.",
        "requisitos": ["Node.js 22.13 o más nuevo", "Python 3.10 o más nuevo (para andamio)", "Expo Go en el celular o el emulador de Android"],
        "piezas": {
            "pantalla": {
                "comando": 'nuevo pantalla "detalle producto" --carpeta productos',
                "explicacion": "Con Expo Router, cada archivo de la carpeta app/ es una pantalla con su propia ruta. andamio la crea con el título en la barra superior; con --carpeta la ubica dentro de una sección (y admite grupos como (tabs)).",
                "uso": "import { router } from 'expo-router';\n\nrouter.push('/productos/detalle-producto');",
                "uso_lenguaje": "ts",
            },
            "componente": {
                "comando": "nuevo componente Tarjeta",
                "explicacion": "Un componente es una parte reutilizable de la interfaz. En React Native los estilos van en un StyleSheet dentro del mismo archivo (no se usa CSS).",
                "uso": "import { Tarjeta } from '@/components';\n\n<Tarjeta>\n  <Text>Yerba</Text>\n</Tarjeta>",
                "uso_lenguaje": "ts",
            },
            "hook": {
                "comando": "nuevo hook contador",
                "explicacion": "Un hook guarda estado y lógica para reutilizarlos en varias pantallas.",
                "uso": "import { useContador } from '@/hooks/useContador';\n\nconst { valor, setValor } = useContador(0);",
                "uso_lenguaje": "ts",
            },
            "servicio": {
                "comando": "nuevo servicio producto nombre:str precio:decimal stock:int",
                "explicacion": "Conecta la app con un recurso de la API de Django. http explica qué dirección usar en el emulador (10.0.2.2), en el navegador (localhost) o en un celular real (la IP de tu PC).",
                "uso": "import { productoService } from '@/services/productoService';\n\nconst productos = await productoService.listar();",
                "uso_lenguaje": "ts",
            },
        },
        "extra": [
            ("npm install", "Instala las dependencias (una vez, o cuando cambia package.json)."),
            ("npx expo start", "Levanta la app: a abre el emulador de Android, w el navegador, o escaneá el QR con Expo Go."),
        ],
    },
}

# Para qué sirve cada archivo. Se busca en orden: el primero que coincide gana
# (en fnmatch, "*" también abarca subcarpetas).
_COMUNES = [
    (".env", "Configuración de tu PC (direcciones, claves). No se sube a git."),
    (".env.example", "Modelo del .env sin datos privados. Se sube a git para que tus compañeros sepan qué completar."),
    (".gitignore", "Lista de archivos que git no sube: dependencias, base de datos, .env."),
    ("README.md", "Explica cómo instalar y ejecutar el proyecto."),
    ("*.gitkeep", "Archivo vacío para que git guarde la carpeta aunque todavía esté vacía."),
]

# Carpetas que el proyecto trae vacías (con un .gitkeep): se explica para qué son.
CARPETAS = {
    "react": {
        "public/.gitkeep": "Carpeta para archivos que se sirven tal cual: imágenes, íconos, fuentes.",
        "src/hooks/.gitkeep": "Carpeta para los hooks: acá los crea python -m andamio nuevo hook.",
        "src/pages/.gitkeep": "Carpeta para las páginas: acá las crea python -m andamio nuevo pagina.",
        "src/services/.gitkeep": "Carpeta para los servicios: acá los crea python -m andamio nuevo servicio.",
    },
    "react-native": {
        "hooks/.gitkeep": "Carpeta para los hooks: acá los crea python -m andamio nuevo hook.",
        "services/.gitkeep": "Carpeta para los servicios: acá los crea python -m andamio nuevo servicio.",
    },
}

DESCRIPCIONES = {
    "python": [
        ("main.py", "Punto de entrada: muestra el menú principal. El diccionario MENUS tiene una opción por entidad (andamio las agrega solo)."),
        ("db.py", "Conexión a SQLite: get_conexion() guarda los cambios, los deshace si hay un error y siempre cierra la conexión."),
        ("sql/schema.sql", "Las tablas de la base de datos. Se ejecuta al arrancar; cada entidad agrega su CREATE TABLE."),
        ("menus/entrada.py", "Funciones de consola: pedir(texto, tipo) pide un dato y lo valida; mostrar_filas() muestra registros como tabla."),
        ("*/__init__.py", "Convierte la carpeta en un paquete de Python, para poder hacer import desde ella."),
        ("entidades/*.py", "Funciones de la tabla: crear, listar, obtener, actualizar y eliminar, con consultas parametrizadas."),
        ("menus/menu_*.py", "Menú de consola de la entidad: listar, agregar, modificar y eliminar desde el teclado."),
    ],
    "django": [
        ("manage.py", "Herramienta de Django: runserver, migrate, makemigrations, test, createsuperuser."),
        ("requirements.txt", "Librerías del proyecto con sus versiones. Se instalan con pip install -r requirements.txt."),
        ("config/settings.py", "Configuración: apps (LOCAL_APPS), base de datos, REST Framework, CORS y Swagger. Lee los valores del .env."),
        ("config/urls.py", "Rutas del proyecto: /admin/, /api/docs/ (Swagger) y una línea por cada recurso."),
        ("config/wsgi.py", "Punto de entrada para publicar el proyecto en un servidor."),
        ("config/asgi.py", "Punto de entrada para publicar el proyecto en un servidor (modo asíncrono)."),
        ("*/migrations/__init__.py", "Carpeta donde Django guarda las migraciones: los cambios de la base de datos."),
        ("*/__init__.py", "Convierte la carpeta en un paquete de Python."),
        ("*/models.py", "El modelo: la tabla y sus campos. Django la crea en la base con makemigrations y migrate."),
        ("*/serializers.py", "Convierte los registros a JSON y valida los datos que llegan a la API."),
        ("*/views.py", "La API: un ModelViewSet con listar, crear, ver, modificar y eliminar, más filtros, búsqueda y orden."),
        ("*/urls.py", "Rutas del recurso: /api/productos/ y /api/productos/<id>/."),
        ("*/admin.py", "Registra el modelo en el panel /admin/ con columnas, búsqueda y filtros."),
        ("*/apps.py", "Configuración de la app (el nombre que muestra el panel de administración)."),
        ("*/tests.py", "5 tests de la API: listar, crear, ver, modificar y eliminar. Se ejecutan con python manage.py test."),
    ],
    "react": [
        ("package.json", "Dependencias (React, Vite) con versiones fijas, y los comandos npm run dev y npm run build."),
        ("index.html", 'La página que carga el navegador: React se dibuja dentro de <div id="root">.'),
        ("vite.config.*", "Configuración de Vite: el servidor de desarrollo y el empaquetador."),
        ("tsconfig*.json", "Configuración de TypeScript (modo estricto)."),
        ("src/main.*", "Punto de entrada: monta el componente App en la página."),
        ("src/App.module.css", "Estilos de App. Las clases de un .module.css solo afectan a ese componente."),
        ("src/App.*", "Componente principal: acá empezás a armar tu aplicación."),
        ("src/index.css", "Estilos globales de toda la aplicación."),
        ("src/components/index.*", "Exporta todos los componentes desde un lugar: import { Tarjeta } from './components'."),
        ("src/components/*/index.*", "Permite importar el componente por el nombre de su carpeta."),
        ("src/components/*.module.css", "Estilos propios del componente (clase .root): no afectan al resto."),
        ("src/components/*", "El componente: una función que recibe props y devuelve lo que se ve."),
        ("src/pages/*/index.*", "Permite importar la página por el nombre de su carpeta."),
        ("src/pages/*.module.css", "Estilos propios de la página."),
        ("src/pages/*", "Una página completa de la aplicación."),
        ("src/hooks/use*", "Un hook: estado y lógica para reutilizar en varios componentes."),
        ("src/services/http.*", "Funciones para pedir datos a la API de Django (GET, POST, PATCH, DELETE) con manejo de errores. Usa VITE_API_URL del .env."),
        ("src/services/*Service.*", "Funciones para un recurso de la API: listar, obtener, crear, actualizar y eliminar, con los tipos de cada campo."),
    ],
    "react-native": [
        ("package.json", "Dependencias de Expo SDK 58 (todas compatibles entre sí) y los comandos de inicio."),
        ("app.json", "Configuración de la app: nombre, ícono, esquema de enlaces y el plugin de Expo Router."),
        ("tsconfig.json", "Configuración de TypeScript y el atajo @/ para importar desde la raíz."),
        ("jsconfig.json", "Configura el atajo @/ para importar desde la raíz (import { Tarjeta } from '@/components')."),
        ("expo-env.d.ts", "Tipos de Expo para TypeScript (por ejemplo, process.env.EXPO_PUBLIC_API_URL)."),
        ("app/_layout.*", "Layout principal: todas las pantallas se muestran en un Stack, con botón para volver."),
        ("app/index.*", "Pantalla de inicio (la ruta /)."),
        ("app/*", "Una pantalla: con Expo Router, cada archivo de app/ es una ruta de la aplicación."),
        ("assets/icon.png", "Ícono de la aplicación."),
        ("constants/app.*", "Datos generales de la app, como el nombre."),
        ("components/index.*", "Exporta todos los componentes desde un lugar: import { Tarjeta } from '@/components'."),
        ("components/*", "Componente con sus estilos en un StyleSheet (React Native no usa CSS)."),
        ("hooks/use*", "Un hook: estado y lógica para reutilizar en varias pantallas."),
        ("services/http.*", "Funciones para pedir datos a la API de Django. Explica qué dirección usar en el emulador, el navegador o un celular."),
        ("services/*Service.*", "Funciones para un recurso de la API: listar, obtener, crear, actualizar y eliminar, con los tipos de cada campo."),
    ],
}

LENGUAJES = {".py": "python", ".ts": "ts", ".tsx": "ts", ".js": "ts", ".jsx": "ts", ".json": "json", ".sql": "sql", ".css": "css", ".html": "html", ".md": "md"}


def descripcion(clave: str, ruta: str) -> str | None:
    if ruta in CARPETAS.get(clave, {}):
        return CARPETAS[clave][ruta]
    for patron, texto in DESCRIPCIONES[clave] + _COMUNES:
        if fnmatch.fnmatchcase(ruta, patron):
            return texto
    return None


# --- Ejecución ---------------------------------------------------------------------------


def _limpiar(texto: str) -> str:
    if _base_actual:
        texto = re.sub(
            re.escape(_base_actual) + r"[/\\]?([^\s]*)",
            lambda m: CARPETA_EJEMPLO + "\\" + m.group(1).replace("/", "\\"),
            texto,
        )
    return texto


def _ejecutar(argumentos: list[str]) -> str:
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
        main(argumentos)
    return _limpiar(salida.getvalue().rstrip("\n"))


def _instantanea(carpeta: Path) -> dict[str, bytes]:
    return {
        p.relative_to(carpeta).as_posix(): p.read_bytes()
        for p in sorted(carpeta.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.name != "datos.db"
    }


def _archivo(clave: str, ruta: str, datos: bytes, estado: str, origen: str) -> dict:
    base = {"ruta": ruta, "estado": estado, "origen": origen, "descripcion": descripcion(clave, ruta)}
    if ruta.endswith(".png"):
        return {**base, "lenguaje": "imagen", "contenido": "data:image/png;base64," + base64.b64encode(datos).decode()}
    texto = datos.decode("utf-8")
    if ruta == ".env":
        texto = re.sub(r"^SECRET_KEY=.*$", "SECRET_KEY=(se genera al azar al crear el proyecto)", texto, flags=re.M)
    if not texto and ruta.endswith(".gitkeep"):
        texto = "(archivo vacío: sirve para que git guarde la carpeta)"
    return {**base, "lenguaje": LENGUAJES.get(Path(ruta).suffix, "texto"), "contenido": texto}


def demo_variante(base: Path, stack, variante: str) -> dict:
    info = TECNOLOGIAS[stack.clave]
    carpeta = info["carpeta"] + (f"-{variante}" if variante else "")
    opcion = f" --{variante}" if variante and variante != next(iter(stack.variantes)) else ""
    comando_crear = f"{PROGRAMA} crear {stack.clave} {info['carpeta']}{opcion}"
    os.chdir(base)
    salida_crear = _ejecutar(["crear", stack.clave, carpeta, *(["--variante", variante] if variante else [])])
    salida_crear = salida_crear.replace(carpeta, info["carpeta"])
    proyecto = base / carpeta
    os.chdir(proyecto)
    recien_creado = _instantanea(proyecto)
    estado = {ruta: "proyecto" for ruta in recien_creado}
    origen = {ruta: "crear" for ruta in estado}

    piezas = []
    for clave_pieza, pieza in stack.piezas.items():
        datos_pieza = info["piezas"][clave_pieza]
        antes = _instantanea(proyecto)
        salida = _ejecutar(shlex.split(datos_pieza["comando"]))
        despues = _instantanea(proyecto)
        creados = [r for r in despues if r not in antes]
        modificados = [r for r in despues if r in antes and antes[r] != despues[r]]
        for ruta in creados:
            estado[ruta], origen[ruta] = "nuevo", clave_pieza
        for ruta in modificados:
            if estado[ruta] == "proyecto":
                estado[ruta] = "modificado"
        piezas.append(
            {
                "clave": clave_pieza,
                "titulo": pieza.titulo,
                "descripcion": pieza.descripcion,
                "explicacion": datos_pieza["explicacion"],
                "comando": f"{PROGRAMA} " + datos_pieza["comando"],
                "salida": salida,
                "creados": creados,
                "modificados": [{"ruta": r, "que": _que_se_modifico(salida, r)} for r in modificados],
                "uso": datos_pieza["uso"],
                "uso_lenguaje": datos_pieza["uso_lenguaje"],
            }
        )
    archivos = [_archivo(stack.clave, r, d, estado[r], origen[r]) for r, d in _instantanea(proyecto).items()]
    contexto = contexto_proyecto(stack, info["carpeta"], variante)
    contexto["activar"] = r".venv\Scripts\activate"  # en la página se muestran los pasos de Windows
    comandos = [(comando_crear, "Crea el proyecto en una carpeta nueva.")]
    comandos += [(p["comando"], f"{p['titulo']}: {p['descripcion']}.") for p in piezas]
    if any("migrar" in pieza.opciones for pieza in stack.piezas.values()):
        comandos.append((f"{piezas[0]['comando']} --migrar", "Genera el recurso y además ejecuta makemigrations y migrate."))
    comandos += [
        (PROGRAMA, "Abre el menú: te pregunta qué generar y te pide cada dato."),
        (f"{PROGRAMA} info", "Muestra qué tipo de proyecto detectó y qué piezas podés generar."),
        (f"{piezas[0]['comando']} --simular", "Muestra qué archivos crearía o modificaría, sin tocar nada."),
        (f"{PROGRAMA} plantillas exportar", "Copia las plantillas al proyecto para modificar el código que se genera."),
        (f"{PROGRAMA} configurar", "Opcional: hace que funcione escribiendo solo andamio (una vez por PC)."),
    ]
    return {
        "clave": variante,
        "nombre": stack.variantes.get(variante, ""),
        "crear": {"comando": comando_crear, "salida": salida_crear},
        "pasos_proyecto": pasos_proyecto(stack, contexto),
        "archivos_crear": [_archivo(stack.clave, r, d, "nuevo", "crear") for r, d in recien_creado.items()],
        "piezas": piezas,
        "archivos": archivos,
        "comandos_andamio": [{"comando": c, "descripcion": d} for c, d in comandos],
    }


def _que_se_modifico(salida: str, ruta: str) -> str:
    """Lo que andamio dice que cambió: "  ~ main.py  (import del menú, opción en MENUS)"."""
    limpia = re.sub(r"\x1b\[[\d;]*m", "", salida).replace("\\", "/")
    encontrado = re.search(rf"~ {re.escape(ruta)}\s+\((.*)\)", limpia)
    return encontrado.group(1) if encontrado else ""


def _ejemplos() -> dict[str, str]:
    """Código de ejemplo que "escribe el alumno" (sitio/ejemplos/), usado en las capturas."""
    carpeta = RAIZ / "sitio" / "ejemplos"
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(carpeta.glob("*")) if p.is_file()}


def demo_tecnologia(base: Path, stack) -> dict:
    info = TECNOLOGIAS[stack.clave]
    variantes = list(stack.variantes) or [""]
    return {
        "clave": stack.clave,
        "titulo": stack.titulo,
        "resumen": info["resumen"],
        "requisitos": info["requisitos"],
        "carpeta": info["carpeta"],
        "tipos": stack.tipos if any(p.usa_campos for p in stack.piezas.values()) else {},
        "comandos_proyecto": [{"comando": c, "descripcion": d} for c, d in info["extra"]],
        "variantes": [demo_variante(base, stack, v) for v in variantes],
    }


def ejecucion_python(base: Path) -> dict:
    """Ejecuta la app de consola generada, como si un alumno la usara."""
    proyecto = base / TECNOLOGIAS["python"]["carpeta"]
    respuestas = ["1", "2", "Yerba Mate", "1500,50", "diez", "10", "2", "Mate de calabaza", "4200", "3", "1", "0", "0"]
    codigo = (
        "import builtins, runpy\n"
        f"respuestas = {respuestas!r}\n"
        "def falso_input(pregunta=''):\n"
        "    r = respuestas.pop(0)\n"
        "    print(pregunta + '\\x1b[33;1m' + r + '\\x1b[0m')\n"
        "    return r\n"
        "builtins.input = falso_input\n"
        "runpy.run_path('main.py', run_name='__main__')\n"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=proyecto,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=60,
    )
    if resultado.returncode != 0:
        raise SystemExit(f"La app de consola generada falló:\n{resultado.stderr}")
    return {"comando": "python main.py", "salida": resultado.stdout.rstrip()}


def demo_menu(base: Path) -> list[dict]:
    """Una sesión real del menú interactivo: lo que se ve y lo que escribe el alumno."""
    os.chdir(base)
    _ejecutar(["crear", "django", "mi-api"])
    os.chdir(base / "mi-api")
    respuestas = ["1", "producto", "", "nombre", "1", "precio", "4", "stock", "3", "", "s", "n"]
    eventos: list[dict] = []
    salida = io.StringIO()

    def volcar() -> None:
        texto = salida.getvalue()
        if texto:
            eventos.append({"tipo": "salida", "texto": _limpiar(texto)})
            salida.seek(0)
            salida.truncate()

    def falso_input(pregunta: str = "") -> str:
        volcar()
        respuesta = respuestas.pop(0)
        eventos.append({"tipo": "entrada", "pregunta": pregunta, "respuesta": respuesta})
        return respuesta

    original = builtins.input
    builtins.input = falso_input
    try:
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            main([])
    finally:
        builtins.input = original
    volcar()
    return eventos


def generar() -> dict:
    global _base_actual
    # Con los códigos de color ANSI que ve el alumno; la página los convierte a HTML.
    consola._usar_color = True
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as temporal:
        # En Windows no se puede borrar la carpeta en la que está parado el proceso:
        # hay que volver a la original antes de que se borre la temporal.
        try:
            menu = Path(temporal) / "menu"
            proyectos = Path(temporal) / "proyectos"
            menu.mkdir()
            proyectos.mkdir()
            _base_actual = str(menu.resolve())
            sesion = demo_menu(menu)
            _base_actual = str(proyectos.resolve())
            tecnologias = [demo_tecnologia(proyectos, stack) for stack in stacks.ORDEN_MENU]
            tecnologias[0]["ejecucion"] = ejecucion_python(proyectos)
            return {"version": andamio.__version__, "menu": sesion, "tecnologias": tecnologias, "ejemplos": _ejemplos()}
        finally:
            _base_actual = ""
            consola._usar_color = None
            os.chdir(cwd)


def main_sitio() -> None:
    datos = generar()
    texto = "// Generado por scripts/sitio.py: no editar a mano.\nwindow.ANDAMIO = " + json.dumps(
        datos, ensure_ascii=False, indent=1
    ) + ";\n"
    DESTINO.write_text(texto, encoding="utf-8")
    print(f"{DESTINO.relative_to(RAIZ)}  ({len(texto) // 1024} KB)")


if __name__ == "__main__":
    main_sitio()
