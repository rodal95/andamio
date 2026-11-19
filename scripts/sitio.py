"""Genera sitio/datos.js con demostraciones reales de andamio para la página web.

    python scripts/sitio.py

Ejecuta andamio de verdad (crea un proyecto de cada tipo y variante, genera cada
pieza, simula una sesión del menú y ejecuta la app de consola generada) y guarda
lo que muestra la terminal y los archivos que genera, con una explicación de para
qué sirve cada uno. Así la página nunca muestra algo distinto de lo que hace la
herramienta. El workflow del sitio lo ejecuta antes de publicar.

Las capturas de pantalla de los proyectos funcionando (sitio/img/) las genera
scripts/capturas_sitio.py, que necesita Django, FastAPI, Node y Chromium (y npm para Express).
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
    "fastapi": {
        "carpeta": "mi-api",
        "resumen": "API REST con FastAPI y SQLModel: más liviana que Django, con documentación interactiva (Swagger) y tests. Responde igual que la API de Django, así que React y React Native la usan sin cambios.",
        "requisitos": ["Python 3.10 o más nuevo"],
        "piezas": {
            "recurso": {
                "comando": "nuevo recurso producto nombre:str precio:decimal stock:int",
                "explicacion": "Un recurso es una tabla publicada como API: con un solo comando tenés /api/productos/ para listar, crear, ver, modificar y eliminar, con filtros, búsqueda y orden. El modelo define la tabla y los datos que acepta la API (con sus validaciones), el router las rutas, y trae 5 tests automáticos. La tabla se crea sola al arrancar.",
                "uso": "GET    /api/productos/                  lista (un array JSON)\nPOST   /api/productos/                  crea\nGET    /api/productos/1/                ve uno\nPATCH  /api/productos/1/                modifica\nDELETE /api/productos/1/                elimina\n\nGET    /api/productos/?search=yerba     busca\nGET    /api/productos/?ordering=-precio ordena\nGET    /api/productos/?stock=10         filtra",
                "uso_lenguaje": "texto",
            },
        },
        "extra": [
            ("python -m venv .venv", "Crea el entorno virtual del proyecto (una sola vez)."),
            (".venv\\Scripts\\activate", "Activa el entorno virtual en Windows (en Linux o Mac: source .venv/bin/activate)."),
            ("pip install -r requirements.txt", "Instala FastAPI, SQLModel y las demás librerías."),
            ("python -m uvicorn app.main:app --reload", "Levanta la API en http://127.0.0.1:8000 y la reinicia sola cuando cambiás el código."),
            ("python -m pytest", "Ejecuta los tests de todos los recursos (con una base de datos en memoria)."),
        ],
    },
    "express": {
        "carpeta": "mi-api",
        "resumen": "API REST con Express y Prisma, en TypeScript o JavaScript, con validación (Zod), documentación interactiva (Swagger) y tests. Responde igual que Django y FastAPI y en el mismo puerto (8000): React y React Native la usan sin cambios.",
        "requisitos": ["Node.js 22.12 o más nuevo", "Python 3.10 o más nuevo (para andamio)"],
        "piezas": {
            "recurso": {
                "comando": "nuevo recurso producto nombre:str precio:decimal stock:int",
                "explicacion": "Un recurso es una tabla publicada como API: con un solo comando tenés /api/productos/ para listar, crear, ver, modificar y eliminar, con filtros, búsqueda y orden. Agrega el modelo a prisma/schema.prisma, la validación de los datos (con mensajes en español), las rutas y 5 tests. Después, una migración crea la tabla (o usá --migrar para que andamio la cree).",
                "uso": "GET    /api/productos/                  lista (un array JSON)\nPOST   /api/productos/                  crea\nGET    /api/productos/1/                ve uno\nPATCH  /api/productos/1/                modifica\nDELETE /api/productos/1/                elimina\n\nGET    /api/productos/?search=yerba     busca\nGET    /api/productos/?ordering=-precio ordena\nGET    /api/productos/?stock=10         filtra",
                "uso_lenguaje": "texto",
            },
        },
        "extra": [
            ("npm install", "Instala las dependencias (una vez, o cuando cambia package.json) y genera el cliente de Prisma."),
            ("npx prisma migrate dev --name productos", "Crea la migración con los cambios de prisma/schema.prisma y la aplica a la base."),
            ("npm run dev", "Levanta la API en http://localhost:8000 y la reinicia sola cuando guardás un cambio."),
            ("npm test", "Ejecuta los tests de todos los recursos, con otra base (test.db): no toca tus datos."),
            ("npx prisma studio", "Abre una página para ver y editar los datos de la base."),
            ("npm run tipos", "Solo en TypeScript: revisa los tipos de todo el proyecto."),
        ],
    },
    "next": {
        "carpeta": "mi-web",
        "resumen": "Aplicación web con Next.js (App Router), en TypeScript o JavaScript, que usa una API hecha con andamio (Django, FastAPI o Express). Cada carpeta de app/ es una dirección: no hace falta configurar rutas.",
        "requisitos": ["Node.js 20.9 o más nuevo", "Python 3.10 o más nuevo (para andamio)"],
        "piezas": {
            "componente": {
                "comando": "nuevo componente Tarjeta",
                "explicacion": "Un componente es una parte reutilizable de la interfaz: una tarjeta, un botón, un formulario. Se genera con sus propios estilos, que no afectan al resto de la página, y queda exportado para importarlo desde cualquier lado.",
                "uso": "import { Tarjeta } from '@/components';\n\n<Tarjeta>\n  <h3>Yerba</h3>\n  <p>$ 1500</p>\n</Tarjeta>",
                "uso_lenguaje": "ts",
            },
            "pagina": {
                "comando": "nuevo pagina Contacto",
                "explicacion": "Una página es una pantalla completa. En Next.js, la carpeta app/contacto con su page es la dirección /contacto: no hay que registrar nada. andamio además agrega el enlace en el menú (app/layout).",
                "uso": "// Ya queda en el menú. Para enlazarla desde otra página:\nimport Link from 'next/link';\n\n<Link href=\"/contacto\">Escribinos</Link>",
                "uso_lenguaje": "ts",
            },
            "hook": {
                "comando": "nuevo hook contador",
                "explicacion": "Un hook guarda estado y lógica para reutilizarlos en varios componentes. Se usa en componentes que empiezan con 'use client' (los que se ejecutan en el navegador).",
                "uso": "'use client';\nimport { useContador } from '@/hooks/useContador';\n\nconst { valor, setValor } = useContador(0);",
                "uso_lenguaje": "ts",
            },
            "servicio": {
                "comando": "nuevo servicio producto nombre:str precio:decimal stock:int",
                "explicacion": "Un servicio conecta la aplicación con un recurso de la API: funciones para listar, obtener, crear, modificar y eliminar. La dirección de la API sale de NEXT_PUBLIC_API_URL (.env). Generalo con los mismos campos que el recurso de la API.",
                "uso": "import { productoService } from '@/services/productoService';\n\nconst productos = await productoService.listar();\nawait productoService.crear({ nombre: 'Yerba', precio: 1500, stock: 10 });",
                "uso_lenguaje": "ts",
            },
            "crud": {
                "comando": "nuevo crud producto nombre:str precio:decimal stock:int",
                "explicacion": "Genera de una vez la interfaz completa de un recurso de la API: la lista, el detalle con eliminar y el formulario para crear y editar (con los errores de validación de la API en cada campo), cada uno en su carpeta de app/, y el enlace en el menú. Las páginas son 'use client' y hablan con el servicio.",
                "uso": "app/productos/page              /productos              listar()\napp/productos/nuevo/page        /productos/nuevo        crear()\napp/productos/[id]/page         /productos/3            obtener(3), eliminar(3)\napp/productos/[id]/editar/page  /productos/3/editar     obtener(3), actualizar(3)",
                "uso_lenguaje": "texto",
            },
        },
        "extra": [
            ("npm install", "Instala las dependencias (una vez, o cuando cambia package.json)."),
            ("npm run dev", "Levanta la aplicación en http://localhost:3000 y la actualiza sola cuando guardás un cambio."),
            ("npm run build", "Arma la versión para publicar (y revisa los tipos en TypeScript). Después: npm start."),
        ],
    },
    "next-fullstack": {
        "carpeta": "mi-app",
        "resumen": "Next.js full stack: las páginas y la API en el mismo proyecto, con base de datos (Prisma + SQLite) y validación (Zod), en TypeScript o JavaScript. La API tiene la misma forma que las de Django, FastAPI y Express: también la puede usar React Native.",
        "requisitos": ["Node.js 22.12 o más nuevo", "Python 3.10 o más nuevo (para andamio)"],
        "piezas": {
            "recurso": {
                "comando": "nuevo recurso producto nombre:str precio:decimal stock:int",
                "explicacion": "La API de un recurso en app/api/productos/: route (listar y crear) y [id]/route (ver, reemplazar, modificar y eliminar), con el modelo en prisma/schema.prisma, la validación con mensajes en español y 5 tests. Con --migrar, andamio también crea la tabla.",
                "uso": "GET    /api/productos/                  lista (un array JSON)\nPOST   /api/productos/                  crea\nGET    /api/productos/1/                ve uno\nPATCH  /api/productos/1/                modifica\nDELETE /api/productos/1/                elimina\n\nGET    /api/productos/?search=yerba     busca\nGET    /api/productos/?ordering=-precio ordena",
                "uso_lenguaje": "texto",
            },
            "crud": {
                "comando": "nuevo crud producto nombre:str precio:decimal stock:int",
                "explicacion": "Las páginas del recurso (lista, detalle con eliminar y formulario para crear y editar), conectadas a la API de este mismo proyecto. Generalo con los mismos campos que el recurso.",
                "uso": "/productos              lista           listar()\n/productos/nuevo        agregar         crear()\n/productos/3            detalle         obtener(3), eliminar(3)\n/productos/3/editar     editar          obtener(3), actualizar(3)",
                "uso_lenguaje": "texto",
            },
            "pagina": {
                "comando": "nuevo pagina Contacto",
                "explicacion": "Una página: la carpeta app/contacto es la dirección /contacto, con su enlace en el menú.",
                "uso": "import Link from 'next/link';\n\n<Link href=\"/contacto\">Escribinos</Link>",
                "uso_lenguaje": "ts",
            },
            "componente": {
                "comando": "nuevo componente Tarjeta",
                "explicacion": "Una parte reutilizable de la interfaz, con sus propios estilos.",
                "uso": "import { Tarjeta } from '@/components';\n\n<Tarjeta>Yerba</Tarjeta>",
                "uso_lenguaje": "ts",
            },
            "hook": {
                "comando": "nuevo hook contador",
                "explicacion": "Estado y lógica para reutilizar en componentes 'use client'.",
                "uso": "const { valor, setValor } = useContador(0);",
                "uso_lenguaje": "ts",
            },
            "servicio": {
                "comando": "nuevo servicio cliente nombre:str email:email",
                "explicacion": "Funciones para usar un recurso de la API de este proyecto desde las páginas (el crud ya trae el suyo).",
                "uso": "import { clienteService } from '@/services/clienteService';\n\nconst clientes = await clienteService.listar();",
                "uso_lenguaje": "ts",
            },
        },
        "extra": [
            ("npm install", "Instala las dependencias y genera el cliente de Prisma."),
            ("npx prisma migrate dev --name productos", "Crea la migración con los cambios de prisma/schema.prisma y la aplica a la base."),
            ("npm run dev", "Levanta la aplicación y la API en http://localhost:3000 y las actualiza solas cuando guardás un cambio."),
            ("npm test", "Ejecuta los tests de la API, con otra base (test.db): no toca tus datos."),
            ("npm run build", "Arma la versión para publicar (después: npm start)."),
            ("npx prisma studio", "Abre una página para ver y editar los datos de la base."),
        ],
    },
    "reflex": {
        "carpeta": "mi-app",
        "resumen": "Aplicación web hecha solo con Python, con Reflex: páginas, estado y base de datos en Python. Sirve con su propia base (crud) o usando una API hecha con andamio (crud-api).",
        "requisitos": ["Python 3.11 o más nuevo", "Internet la primera vez (Reflex descarga lo que usa para el navegador)"],
        "piezas": {
            "crud": {
                "comando": "nuevo crud producto nombre:str precio:decimal stock:int",
                "explicacion": "La tabla en la base de datos de este proyecto (un modelo de SQLModel, con su validación y los mensajes en español) y una página para listar, agregar, editar y eliminar, con su enlace en el menú. Con --migrar, andamio también crea la tabla (reflex db).",
                "uso": "/productos        el formulario arriba y la tabla abajo\n\nProductoState.cargar     lee los registros (al abrir la página)\nProductoState.guardar    valida y guarda (agregar o editar)\nProductoState.eliminar   elimina uno",
                "uso_lenguaje": "texto",
            },
            "crud-api": {
                "comando": "nuevo crud-api cliente nombre:str email:email",
                "explicacion": "La misma página, pero los datos están en una API hecha con andamio (Django, FastAPI o Express): el estado los pide con un servicio, y si la API rechaza un dato, el error aparece debajo del campo. La dirección está en API_URL (.env).",
                "uso": "API_URL=http://localhost:8000/api      (en el .env)\n\nClienteState.cargar   ->  GET  /api/clientes/\nClienteState.guardar  ->  POST /api/clientes/   o   PATCH /api/clientes/3/",
                "uso_lenguaje": "texto",
            },
            "pagina": {
                "comando": "nuevo pagina Contacto",
                "explicacion": "Una página es una función de Python que devuelve componentes. andamio la registra con su dirección (/contacto) y agrega el enlace en el menú.",
                "uso": "def contacto() -> rx.Component:\n    return plantilla(\n        rx.heading(\"Contacto\", size=\"7\"),\n        rx.text(\"Escribinos a hola@ejemplo.com\"),\n    )",
                "uso_lenguaje": "python",
            },
            "componente": {
                "comando": "nuevo componente Tarjeta",
                "explicacion": "Un componente es una función que arma una parte de la interfaz para usarla en varias páginas.",
                "uso": "from mi_app.componentes.tarjeta import tarjeta\n\ntarjeta(rx.heading(\"Yerba\"), rx.text(\"$ 1500\"))",
                "uso_lenguaje": "python",
            },
            "estado": {
                "comando": "nuevo estado contador",
                "explicacion": "Un estado guarda datos de la aplicación y las acciones que los cambian. En Reflex vive en Python: la página se actualiza sola cuando cambia.",
                "uso": "from mi_app.estados.contador import ContadorState\n\nrx.button(\"Sumar\", on_click=ContadorState.sumar)\nrx.text(ContadorState.valor)",
                "uso_lenguaje": "python",
            },
            "servicio": {
                "comando": "nuevo servicio producto nombre:str precio:decimal stock:int",
                "explicacion": "Funciones para usar un recurso de una API hecha con andamio: listar, obtener, crear, actualizar y eliminar (son async, se usan desde un estado).",
                "uso": "import mi_app.servicios.producto as producto_api\n\nproductos = await producto_api.listar()\nawait producto_api.crear({\"nombre\": \"Yerba\", \"precio\": 1500, \"stock\": 10})",
                "uso_lenguaje": "python",
            },
        },
        "extra": [
            ("python -m venv .venv", "Crea el entorno virtual del proyecto (una sola vez)."),
            (".venv\\Scripts\\activate", "Activa el entorno virtual en Windows (en Linux o Mac: source .venv/bin/activate)."),
            ("pip install -r requirements.txt", "Instala Reflex y lo que usa la base de datos."),
            ("reflex run", "Levanta la aplicación en http://localhost:3000 y la actualiza sola cuando guardás un cambio."),
            ("reflex db init", "La primera vez: crea las migraciones de la base y las aplica."),
            ("reflex db makemigrations --message productos", "Después de cambiar un modelo: crea la migración (y después reflex db migrate)."),
        ],
    },
    "react": {
        "carpeta": "mi-web",
        "resumen": "Aplicación web con React y Vite, en TypeScript o JavaScript. Genera componentes, páginas, hooks, servicios y CRUDs completos para usar tu API (Django, FastAPI o Express).",
        "requisitos": ["Node.js 20.19 o más nuevo", "Python 3.10 o más nuevo (para andamio)"],
        "piezas": {
            "componente": {
                "comando": "nuevo componente Tarjeta",
                "explicacion": "Un componente es una parte reutilizable de la interfaz: una tarjeta, un botón, un formulario. Se genera con sus propios estilos, que no afectan al resto de la página, y queda exportado para importarlo desde cualquier lado.",
                "uso": "import { Tarjeta } from './components';\n\n<Tarjeta>\n  <h3>Yerba</h3>\n  <p>$ 1500</p>\n</Tarjeta>",
                "uso_lenguaje": "ts",
            },
            "pagina": {
                "comando": "nuevo pagina Contacto",
                "explicacion": "Una página es una pantalla completa de la aplicación. Se genera en src/pages/ con sus estilos, y andamio la registra en el router: queda en la ruta /contacto y con su enlace en el menú.",
                "uso": "// Ya queda en el menú. Para enlazarla desde otra página:\nimport { Link } from 'react-router';\n\n<Link to=\"/contacto\">Escribinos</Link>",
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
                "explicacion": "Un servicio conecta la aplicación con un recurso de la API (Django, FastAPI o Express): funciones para listar, obtener, crear, modificar y eliminar. Generalo con los mismos campos que el recurso de la API.",
                "uso": "import { productoService } from './services/productoService';\n\nconst productos = await productoService.listar();\nawait productoService.crear({ nombre: 'Yerba', precio: 1500, stock: 10 });\nawait productoService.actualizar(1, { stock: 7 });",
                "uso_lenguaje": "ts",
            },
            "crud": {
                "comando": "nuevo crud producto nombre:str precio:decimal stock:int",
                "explicacion": "Genera de una vez la interfaz completa de un recurso de la API (Django, FastAPI o Express): la lista, el detalle con eliminar y el formulario para crear y editar (que muestra los errores de validación de la API en cada campo), con sus rutas y el enlace en el menú. Las páginas hablan con el servicio; el componente de detalle solo muestra los datos y avisa. Generalo con los mismos campos que el recurso de la API.",
                "uso": "/productos              lista           listar()\n/productos/nuevo        agregar         crear()\n/productos/3            detalle         obtener(3), eliminar(3)\n/productos/3/editar     editar          obtener(3), actualizar(3)",
                "uso_lenguaje": "texto",
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
                "explicacion": "Conecta la app con un recurso de la API (Django, FastAPI o Express). http explica qué dirección usar en el emulador (10.0.2.2), en el navegador (localhost) o en un celular real (la IP de tu PC).",
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
    "next": {
        "public/.gitkeep": "Carpeta para archivos que se sirven tal cual: imágenes, íconos, fuentes.",
        "hooks/.gitkeep": "Carpeta para los hooks: acá los crea python -m andamio nuevo hook.",
        "services/.gitkeep": "Carpeta para los servicios: acá los crea python -m andamio nuevo servicio.",
    },
    "reflex": {
        "assets/.gitkeep": "Carpeta para imágenes y otros archivos que se sirven tal cual (por ejemplo, /logo.png).",
    },
    "react-native": {
        "hooks/.gitkeep": "Carpeta para los hooks: acá los crea python -m andamio nuevo hook.",
        "services/.gitkeep": "Carpeta para los servicios: acá los crea python -m andamio nuevo servicio.",
    },
}

# --- El camino de cada guía ------------------------------------------------------------

# Las piezas en el orden en que conviene aprenderlas. "tema:x" intercala una lección de un
# concepto que no es una pieza (por ejemplo, el router), definida en TEMAS.
CAMINO = {
    "python": ["entidad", "tema:menu"],
    "django": ["recurso", "tema:rutas"],
    "fastapi": ["recurso", "tema:rutas"],
    "express": ["recurso", "tema:rutas"],
    "react": ["componente", "pagina", "tema:router", "hook", "servicio", "crud"],
    "react-native": ["pantalla", "tema:router", "componente", "hook", "servicio"],
    "next": ["componente", "pagina", "tema:router", "hook", "servicio", "crud"],
    "next-fullstack": ["recurso", "crud", "componente", "pagina", "tema:router", "hook", "servicio"],
    "reflex": ["pagina", "tema:router", "componente", "estado", "crud", "servicio", "crud-api"],
}

# Lecciones de conceptos. "archivos" son archivos del proyecto completo de la guía (se
# muestran tal cual quedan); {ext} y {extx} cambian según el lenguaje.
_ROUTER_NEXT = {
    "titulo": "Las rutas: cada carpeta es una dirección",
    "texto": [
        "En Next.js no se escriben rutas: la carpeta de app/ es la dirección. app/contacto/page es /contacto, y una carpeta entre corchetes es una parte variable: app/productos/[id]/page es /productos/3.",
        "El menú está en app/layout, que envuelve a todas las páginas: andamio agrega un <Link> por cada página que generes.",
        "Para ir a otra página: <Link href=\"/contacto\"> o, desde el código, useRouter().push('/contacto'). Para leer la parte variable: useParams().",
    ],
    "archivos": ["app/layout.{extx}", "app/productos/[id]/page.{extx}"],
}
TEMAS = {
    "python": {
        "menu": {
            "titulo": "El menú principal",
            "texto": [
                "main.py muestra el menú principal y llama al menú de cada entidad. El diccionario MENUS tiene una opción por entidad: andamio la agrega cuando generás una.",
                "Para sumar una opción propia, agregá una línea a MENUS con el texto y la función que se ejecuta.",
            ],
            "archivos": ["main.py"],
        }
    },
    "django": {
        "rutas": {
            "titulo": "Las rutas de la API",
            "texto": [
                "Cada recurso tiene su urls.py: un router de Django REST Framework arma /api/productos/ (listar y crear) y /api/productos/3/ (ver, modificar y eliminar).",
                "config/urls.py junta todas las rutas: andamio agrega una línea por cada recurso. En /api/docs/ las ves todas, con Swagger.",
            ],
            "archivos": ["config/urls.py", "productos/urls.py"],
        }
    },
    "fastapi": {
        "rutas": {
            "titulo": "Las rutas de la API",
            "texto": [
                "Cada recurso tiene su router.py: un APIRouter con prefix=\"/api/productos\" y una función por operación (@router.get, @router.post...).",
                "app/main.py incluye cada router con app.include_router: andamio agrega la línea. En /docs las ves todas, con Swagger.",
            ],
            "archivos": ["app/main.py"],
        }
    },
    "express": {
        "rutas": {
            "titulo": "Las rutas de la API",
            "texto": [
                "Cada recurso tiene su router (src/productos/router): una función por operación (router.get, router.post...).",
                "src/app los monta con app.use('/api/productos', productosRouter): andamio agrega la línea, y también la suma a la documentación de /docs.",
            ],
            "archivos": ["src/app.{ext}"],
        }
    },
    "react": {
        "router": {
            "titulo": "El router: rutas y menú",
            "texto": [
                "Una aplicación de React es una sola página: el router (react-router) decide qué componente mostrar según la dirección. andamio ya lo dejó configurado en src/App.",
                "Cada <Route path=\"/contacto\" element={<ContactoPage />} /> asocia una dirección con una página, y <Link to=\"/contacto\"> navega sin recargar. pagina y crud agregan su ruta y su enlace solos.",
                "Adentro de una página: useNavigate() para ir a otra dirección desde el código y useParams() para leer la parte variable de la ruta (el :id de /productos/:id).",
            ],
            "archivos": ["src/App.{extx}", "src/pages/productos/ProductoDetallePage.{extx}"],
        }
    },
    "react-native": {
        "router": {
            "titulo": "Las rutas: Expo Router",
            "texto": [
                "Con Expo Router cada archivo de app/ es una pantalla y su ruta: app/productos/detalle-producto es /productos/detalle-producto. app/index es la pantalla de inicio.",
                "app/_layout define cómo se muestran: en un Stack, una arriba de la otra, con el botón para volver.",
                "Para ir a otra pantalla: <Link href=\"/productos/detalle-producto\"> o router.push(...). Para leer lo que llega en la ruta: useLocalSearchParams().",
            ],
            "archivos": ["app/_layout.{extx}"],
        }
    },
    "next": {"router": _ROUTER_NEXT},
    "next-fullstack": {"router": _ROUTER_NEXT},
    "reflex": {
        "router": {
            "titulo": "Las rutas y el menú",
            "texto": [
                "Cada página es una función de Python. Se registra con app.add_page(funcion, route=\"/contacto\") en mi_app/mi_app.py: andamio agrega la línea, y también el enlace en la lista ENLACES de plantilla.py.",
                "Para ir a otra página: rx.link(\"Contacto\", href=\"/contacto\"), o rx.redirect(\"/contacto\") desde una acción del estado.",
            ],
            "archivos": ["mi_app/mi_app.py", "mi_app/plantilla.py"],
        }
    },
}

# Combinaciones: cómo usar varias piezas juntas, con código real (sitio/ejemplos/). Cada
# una se arma sobre la anterior. "archivos" son (ruta en el proyecto, ejemplo); {v} es la
# variante y {ext}/{extx} sus extensiones. tests/integracion/test_combinaciones.py aplica
# cada combinación a un proyecto generado y lo compila.
_CAMPOS_PRODUCTO = "nombre:str precio:decimal stock:int"

_COMBINACIONES_WEB = [
    {
        "id": "servicio-en-pagina",
        "titulo": "Una página que muestra datos de la API",
        "usa": ["pagina", "servicio"],
        "texto": "Una página nueva que, al abrirse, pide los productos a la API con el servicio y los muestra en una lista.",
        "pasos": [("", "nuevo pagina Catalogo"), ("", f"nuevo servicio producto {_CAMPOS_PRODUCTO}")],
        "claves": [
            "useState guarda los datos de la página: cuando cambian (setProductos), la página se vuelve a dibujar.",
            "useEffect(..., []) se ejecuta una sola vez, al abrir la página: ahí se piden los datos.",
            "productoService.listar() devuelve una promesa: .then recibe la lista y .catch el error.",
        ],
    },
    {
        "id": "componente-con-datos",
        "titulo": "Mostrar cada producto con un componente",
        "usa": ["componente"],
        "texto": "La misma página, pero cada producto se muestra con un componente Tarjeta. El componente no sabe de la API: recibe lo que tiene que mostrar.",
        "pasos": [("", "nuevo componente Tarjeta")],
        "claves": [
            "Lo que va entre <Tarjeta> y </Tarjeta> le llega al componente como children.",
            "key={producto.id} le dice a React cuál tarjeta es cuál cuando la lista cambia.",
            "Si mañana cambiás cómo se ve una tarjeta, se cambia en un solo lugar.",
        ],
    },
    {
        "id": "hook-propio",
        "titulo": "Llevar la lógica a un hook",
        "usa": ["hook", "servicio"],
        "texto": "Pedir los datos (con su estado de cargando y su error) se lleva a un hook propio: useProductos. La página queda más corta y otras páginas pueden usar el mismo hook.",
        "pasos": [("", "nuevo hook productos")],
        "claves": [
            "Un hook es una función que empieza con use y puede usar useState y useEffect.",
            "Devuelve lo que la página necesita: { productos, cargando, error }.",
            "andamio genera el esqueleto del hook; acá se reemplaza por el que pide los productos.",
        ],
    },
]

COMBINACIONES = {
    "react": [
        {**_COMBINACIONES_WEB[0], "archivos": [("src/pages/CatalogoPage/CatalogoPage.{extx}", "react/{v}/1-CatalogoPage.{extx}")]},
        {**_COMBINACIONES_WEB[1], "archivos": [("src/pages/CatalogoPage/CatalogoPage.{extx}", "react/{v}/2-CatalogoPage.{extx}")]},
        {
            **_COMBINACIONES_WEB[2],
            "archivos": [
                ("src/hooks/useProductos.{ext}", "react/{v}/3-useProductos.{ext}"),
                ("src/pages/CatalogoPage/CatalogoPage.{extx}", "react/{v}/3-CatalogoPage.{extx}"),
            ],
        },
        {
            "id": "enlazar-con-el-crud",
            "titulo": "Enlazar con otra página (router)",
            "usa": ["crud", "pagina"],
            "texto": "Cada tarjeta del catálogo lleva al detalle del producto, que es una página del crud. El crud usa el servicio que ya tenías.",
            "pasos": [("", f"nuevo crud producto {_CAMPOS_PRODUCTO}")],
            "archivos": [("src/pages/CatalogoPage/CatalogoPage.{extx}", "react/{v}/4-CatalogoPage.{extx}")],
            "claves": [
                "<Link to={`/productos/${producto.id}`}> arma la dirección de cada producto: /productos/3.",
                "Esa ruta la registró el crud en src/App; su página lee el 3 con useParams().",
                "El crud no pisó tu servicio: usa el que ya existía, porque tiene los mismos campos.",
            ],
        },
    ],
    "next": [
        {**_COMBINACIONES_WEB[0], "archivos": [("app/catalogo/page.{extx}", "next/{v}/1-page.{extx}")]},
        {**_COMBINACIONES_WEB[1], "archivos": [("app/catalogo/page.{extx}", "next/{v}/2-page.{extx}")]},
        {
            **_COMBINACIONES_WEB[2],
            "archivos": [("hooks/useProductos.{ext}", "next/{v}/3-useProductos.{ext}"), ("app/catalogo/page.{extx}", "next/{v}/3-page.{extx}")],
        },
        {
            "id": "enlazar-con-el-crud",
            "titulo": "Enlazar con otra página",
            "usa": ["crud", "pagina"],
            "texto": "Cada tarjeta del catálogo lleva al detalle del producto, que es una página del crud (la carpeta app/productos/[id]).",
            "pasos": [("", f"nuevo crud producto {_CAMPOS_PRODUCTO}")],
            "archivos": [("app/catalogo/page.{extx}", "next/{v}/4-page.{extx}")],
            "claves": [
                "<Link href={`/productos/${producto.id}`}> arma la dirección de cada producto: /productos/3.",
                "No hay que registrar la ruta: la carpeta app/productos/[id] que generó el crud ya es esa dirección.",
                "'use client' va en la primera línea porque la página usa un hook: se ejecuta en el navegador.",
            ],
        },
    ],
    "react-native": [
        {
            **_COMBINACIONES_WEB[0],
            "titulo": "Una pantalla que muestra datos de la API",
            "usa": ["servicio"],
            "texto": "La pantalla de inicio pide los productos a la API con el servicio y los muestra en una lista (FlatList).",
            "pasos": [("", f"nuevo servicio producto {_CAMPOS_PRODUCTO}")],
            "archivos": [("app/index.{extx}", "react-native/{v}/1-index.{extx}")],
            "claves": [
                "useState guarda la lista: cuando cambia (setProductos), la pantalla se vuelve a dibujar.",
                "useEffect(..., []) se ejecuta una sola vez, al abrir la pantalla: ahí se piden los datos.",
                "FlatList dibuja solo las filas que se ven: sirve para listas largas.",
            ],
        },
        {**_COMBINACIONES_WEB[1], "archivos": [("app/index.{extx}", "react-native/{v}/2-index.{extx}")]},
        {
            **_COMBINACIONES_WEB[2],
            "archivos": [("hooks/useProductos.{ext}", "react-native/{v}/3-useProductos.{ext}"), ("app/index.{extx}", "react-native/{v}/3-index.{extx}")],
        },
        {
            "id": "abrir-otra-pantalla",
            "titulo": "Abrir otra pantalla con un dato (router)",
            "usa": ["pantalla"],
            "texto": "Al tocar una tarjeta se abre la pantalla de detalle, que recibe el id del producto en la ruta y lo pide a la API.",
            "pasos": [("", "nuevo pantalla detalle-producto --carpeta productos")],
            "archivos": [
                ("app/index.{extx}", "react-native/{v}/4-index.{extx}"),
                ("app/productos/detalle-producto.{extx}", "react-native/{v}/4-detalle-producto.{extx}"),
            ],
            "claves": [
                "<Link href={{ pathname: '/productos/detalle-producto', params: { id: item.id } }}> abre la pantalla con el id.",
                "En el detalle, useLocalSearchParams() lee ese id, y productoService.obtener(id) pide el producto.",
                "asChild hace que el Link use el Pressable de adentro: toda la tarjeta se puede tocar.",
            ],
        },
    ],
    "next-fullstack": [
        {
            **_COMBINACIONES_WEB[0],
            "titulo": "Una página que usa la API de este proyecto",
            "usa": ["recurso", "pagina", "servicio"],
            "texto": "El recurso crea la API en app/api/productos/; una página nueva la usa con el servicio, igual que si la API estuviera en otro lado.",
            "pasos": [
                ("", f"nuevo recurso producto {_CAMPOS_PRODUCTO} --migrar"),
                ("", "nuevo pagina Catalogo"),
                ("", f"nuevo servicio producto {_CAMPOS_PRODUCTO}"),
            ],
            "archivos": [("app/catalogo/page.{extx}", "next/{v}/1-page.{extx}")],
        },
        {**_COMBINACIONES_WEB[1], "archivos": [("app/catalogo/page.{extx}", "next/{v}/2-page.{extx}")]},
        {
            **_COMBINACIONES_WEB[2],
            "archivos": [("hooks/useProductos.{ext}", "next/{v}/3-useProductos.{ext}"), ("app/catalogo/page.{extx}", "next/{v}/3-page.{extx}")],
        },
        {
            "id": "desde-react-native",
            "titulo": "Usar esta API desde React Native",
            "usa": ["recurso"],
            "texto": "La API de este proyecto tiene la misma forma que las de Django, FastAPI y Express: una app de React Native la usa con su servicio.",
            "pasos": [
                ("En la app de React Native", f"nuevo servicio producto {_CAMPOS_PRODUCTO}"),
                ("En el .env de la app", "EXPO_PUBLIC_API_URL=http://IP-DE-TU-PC:3000/api"),
                ("En este proyecto", "npm run dev"),
            ],
            "claves": [
                "En un celular, localhost es el celular: usá la IP de tu PC (en Windows, ipconfig).",
                "Next.js ya escucha en la red con npm run dev.",
                "Para Expo en el navegador, agregá su dirección a CORS_ALLOWED_ORIGINS en el .env de este proyecto.",
            ],
        },
    ],
    "reflex": [
        {
            "id": "componente-en-pagina",
            "titulo": "Usar un componente en una página",
            "usa": ["pagina", "componente"],
            "texto": "Una página nueva que muestra tarjetas con el componente tarjeta.",
            "pasos": [("", "nuevo pagina Catalogo"), ("", "nuevo componente Tarjeta")],
            "archivos": [("mi_app/paginas/catalogo.py", "reflex/1-catalogo.py")],
            "claves": [
                "Un componente es una función: tarjeta(...) recibe lo que va adentro y devuelve un componente.",
                "rx.hstack los pone uno al lado del otro; spacing es el espacio entre ellos.",
            ],
        },
        {
            "id": "estado-en-pagina",
            "titulo": "Una página con su estado",
            "usa": ["estado"],
            "texto": "La misma página con un botón que suma \"me gusta\": el valor vive en un estado y la página se actualiza sola.",
            "pasos": [("", "nuevo estado contador")],
            "archivos": [("mi_app/paginas/catalogo.py", "reflex/2-catalogo.py")],
            "claves": [
                "on_click=ContadorState.sumar ejecuta esa acción en Python cuando tocás el botón.",
                "rx.text(ContadorState.valor) muestra el valor y cambia solo cuando el estado cambia.",
            ],
        },
        {
            "id": "servicio-en-pagina",
            "titulo": "Una página que muestra datos de una API",
            "usa": ["servicio", "componente"],
            "texto": "La página pide los productos a una API hecha con andamio (Django, FastAPI o Express) y muestra una tarjeta por cada uno.",
            "pasos": [("", f"nuevo servicio producto {_CAMPOS_PRODUCTO}"), ("En el .env", "API_URL=http://localhost:8000/api")],
            "archivos": [("mi_app/paginas/catalogo.py", "reflex/3-catalogo.py")],
            "claves": [
                "CatalogoState.cargar es async: espera la respuesta de la API (await) sin trabar la página.",
                "on_mount=CatalogoState.cargar pide los datos cuando la página se abre.",
                "rx.foreach arma una tarjeta por producto: la lista vive en el estado, no en el navegador.",
            ],
        },
    ],
    "python": [
        {
            "id": "entidad-en-tu-codigo",
            "titulo": "Usar una entidad desde tu propio programa",
            "usa": ["entidad"],
            "texto": "Las funciones de una entidad (crear, listar, obtener, actualizar y eliminar) se pueden usar desde cualquier archivo: por ejemplo, un reporte.",
            "pasos": [("", "nuevo entidad producto nombre:str precio:float stock:int")],
            "archivos": [("reporte.py", "python/1-reporte.py")],
            "claves": [
                "db.inicializar() crea las tablas si no existen (main.py lo hace al arrancar).",
                "producto.listar() devuelve filas: se leen por nombre, como fila[\"precio\"].",
                "Se ejecuta con python reporte.py, desde la carpeta del proyecto.",
            ],
        }
    ],
}

# Las APIs se combinan con los frontends: son pasos en los dos proyectos.
for _api, _marcha in (
    ("django", "python manage.py runserver"),
    ("fastapi", "python -m uvicorn app.main:app --reload"),
    ("express", "npm run dev"),
):
    _migrar = " --migrar" if _api in ("django", "express") else ""
    COMBINACIONES[_api] = [
        {
            "id": "desde-una-web",
            "titulo": "Usar el recurso desde React o Next.js",
            "usa": ["recurso"],
            "texto": "La web pide y guarda los datos en esta API. Generá el recurso acá y el crud en la web, con los mismos campos.",
            "pasos": [
                ("En la API", f"nuevo recurso producto {_CAMPOS_PRODUCTO}{_migrar}"),
                ("En la API", _marcha),
                ("En la web (React o Next.js)", f"nuevo crud producto {_CAMPOS_PRODUCTO}"),
                ("En la web", "npm run dev"),
            ],
            "claves": [
                "Los campos tienen que ser los mismos en los dos lados: si no, la API responde 400 y dice cuál falta.",
                "La web ya apunta a http://localhost:8000/api (VITE_API_URL o NEXT_PUBLIC_API_URL en su .env).",
                "La API ya acepta pedidos de React (puerto 5173) y Next.js (3000): CORS_ALLOWED_ORIGINS en el .env.",
            ],
        },
        {
            "id": "desde-el-celular",
            "titulo": "Usarlo desde el celular (React Native)",
            "usa": ["recurso"],
            "texto": "La app de React Native usa la misma API con su servicio.",
            "pasos": [
                ("En la app", f"nuevo servicio producto {_CAMPOS_PRODUCTO}"),
                ("En el .env de la app", "EXPO_PUBLIC_API_URL=http://IP-DE-TU-PC:8000/api"),
                ("En la API", {"django": "python manage.py runserver 0.0.0.0:8000", "fastapi": "python -m uvicorn app.main:app --reload --host 0.0.0.0", "express": "npm run dev"}[_api]),
            ],
            "claves": [
                "En el emulador de Android tu PC es 10.0.2.2 (ya viene en el .env de la app).",
                "En un celular real, poné la IP de tu PC (en Windows: ipconfig) y que la API escuche en la red.",
            ]
            + (["En Django, agregá también esa IP a ALLOWED_HOSTS en el .env."] if _api == "django" else []),
        },
        {
            "id": "buscar-ordenar-filtrar",
            "titulo": "Buscar, ordenar y filtrar",
            "usa": ["recurso"],
            "texto": "La lista acepta parámetros en la dirección. Probalos en el navegador o desde la web.",
            "pasos": [
                ("Buscar en los campos de texto", "http://localhost:8000/api/productos/?search=yerba"),
                ("Ordenar (con - es de mayor a menor)", "http://localhost:8000/api/productos/?ordering=-precio"),
                ("Filtrar por igualdad", "http://localhost:8000/api/productos/?stock=10"),
            ],
            "claves": ["Se pueden combinar: ?search=mate&ordering=precio.", "Funciona igual en las tres APIs de andamio."],
        },
    ]


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
    "fastapi": [
        ("requirements.txt", "Librerías del proyecto con sus versiones. Se instalan con pip install -r requirements.txt."),
        ("app/main.py", "La aplicación: CORS, errores en español y una línea por cada recurso (andamio las agrega solo). /api/ lleva a la documentación."),
        ("app/config.py", "Configuración leída del .env: base de datos, páginas que pueden usar la API (CORS) y zona horaria."),
        ("app/db.py", "Conexión a la base de datos (SQLite por defecto): crea las tablas al arrancar y abre una sesión por pedido."),
        ("app/tipos.py", "Tipos que usan todos los recursos: decimales que salen como número y fechas con hora en hora local, igual que Django."),
        ("app/errores.py", "Convierte los errores de validación al formato de Django REST: 400 con {campo: [mensaje]} en español."),
        ("app/*/modelo.py", "El modelo: la tabla con sus campos y las formas de los datos para crear, modificar y leer, con sus validaciones."),
        ("app/*/router.py", "Las rutas del recurso: listar (con búsqueda, orden y filtros), crear, ver, reemplazar, modificar y eliminar."),
        ("*/__init__.py", "Convierte la carpeta en un paquete de Python, para poder hacer import desde ella."),
        ("tests/conftest.py", "Prepara los tests: un cliente de la API con una base de datos en memoria (no toca tus datos)."),
        ("tests/test_*.py", "5 tests de la API: listar, crear, ver, modificar y eliminar. Se ejecutan con python -m pytest."),
    ],
    "express": [
        ("package.json", "Dependencias (Express, Prisma, Zod) con versiones fijas, y los comandos npm run dev y npm test."),
        ("tsconfig.json", "Configuración de TypeScript (modo estricto). npm run tipos revisa los tipos."),
        ("prisma.config.*", "Configuración de Prisma: dónde están el esquema, las migraciones y la base de datos (DATABASE_URL del .env)."),
        ("prisma/schema.prisma", "Las tablas de la base de datos: un model por tabla (andamio agrega uno por recurso). Después de cambiarlo: npx prisma migrate dev."),
        ("src/servidor.*", "Arranca la API en el puerto 8000 (npm run dev)."),
        ("src/app.*", "La aplicación: CORS, una línea por recurso con sus rutas, la documentación en /docs y el manejo de errores."),
        ("src/config.*", "Configuración leída del .env: puerto, base de datos, páginas que pueden usar la API (CORS) y zona horaria."),
        ("src/db.*", "Conexión a la base de datos con Prisma: prisma.producto.findMany(), create(), update(), delete()."),
        ("src/docs.*", "Arma la documentación de Swagger (/docs) con los esquemas de cada recurso. Funciona sin internet."),
        ("src/errores.*", "Errores con el formato de Django REST: 400 con {campo: [mensaje]} en español y 404 con {detail}."),
        ("src/fechas.*", "Cómo salen las fechas en el JSON: \"2026-11-19\", y las fechas con hora en hora local con su zona, igual que Django."),
        ("src/validacion.*", "Funciones para validar los datos con Zod (texto, entero, decimal, fecha...), con los mensajes en español de Django."),
        ("src/*/esquema.*", "Qué datos acepta el recurso (validación con Zod) y cómo se ve cada registro en el JSON."),
        ("src/*/router.*", "Las rutas del recurso: listar (con búsqueda, orden y filtros), crear, ver, reemplazar, modificar y eliminar."),
        ("tests/api.*", "Ayuda para los tests: arranca la API con otra base de datos (test.db), para no tocar tus datos."),
        ("tests/*.test.*", "5 tests de la API: listar, crear, ver, modificar y eliminar. Se ejecutan con npm test."),
    ],
    "next": [
        ("package.json", "Dependencias (Next.js y React) con versiones fijas, y los comandos npm run dev, build y start."),
        ("tsconfig.json", "Configuración de TypeScript, con el atajo @/ para importar desde la raíz (import { Tarjeta } from '@/components')."),
        ("jsconfig.json", "Configura el atajo @/ para importar desde la raíz (import { Tarjeta } from '@/components')."),
        ("next.config.*", "Configuración de Next.js."),
        ("app/layout.module.css", "Estilos del layout: el menú y el contenedor de las páginas."),
        ("app/layout.*", "Layout principal: envuelve a todas las páginas y tiene el menú. andamio agrega un enlace por cada página."),
        ("app/page.module.css", "Estilos de la página de inicio."),
        ("app/page.*", "La página de inicio (la dirección /)."),
        ("app/globals.css", "Estilos globales de toda la aplicación."),
        ("app/*/page.module.css", "Estilos propios de la página."),
        ("app/*/*.module.css", "Estilos de las páginas del recurso (lista, detalle y formulario)."),
        ("app/*/*Formulario.*", "El formulario para crear y editar: usa crear() o actualizar() y muestra los errores de validación de la API. Lo usan las páginas nuevo y editar."),
        ("app/*/nuevo/page.*", "Agregar (la dirección /…/nuevo): muestra el formulario vacío."),
        ("app/*/[[]id]/editar/page.*", "Editar (la dirección /…/3/editar): muestra el formulario con los datos actuales."),
        ("app/*/[[]id]/page.*", "El detalle (la dirección /…/3): pide el registro con obtener(id) y lo elimina con eliminar(id). [id] es la parte variable."),
        ("app/*/page.*", "Una página: la carpeta es la dirección. Si es la de un recurso, la lista: pide los registros con listar()."),
        ("components/index.*", "Exporta todos los componentes desde un lugar: import { Tarjeta } from '@/components'."),
        ("components/*/index.*", "Permite importar el componente por el nombre de su carpeta."),
        ("components/*Detalle/*Detalle.?sx", "Muestra un registro con los botones Editar y Eliminar. No llama a la API: recibe los datos y avisa con onEditar y onEliminar."),
        ("components/*.module.css", "Estilos propios del componente: no afectan al resto."),
        ("components/*", "El componente: una función que recibe props y devuelve lo que se ve."),
        ("hooks/useConsulta.*", "Hook genérico para pedir datos a la API: guarda el resultado, si está cargando y el error. Lo usan las páginas del CRUD."),
        ("hooks/use*", "Un hook: estado y lógica para reutilizar en componentes 'use client'."),
        ("services/http.*", "Funciones para pedir datos a la API (GET, POST, PATCH, DELETE) con manejo de errores. Usa NEXT_PUBLIC_API_URL del .env."),
        ("services/*Service.*", "Funciones para un recurso de la API: listar, obtener, crear, actualizar y eliminar, con los tipos de cada campo."),
    ],
    "next-fullstack": [
        ("package.json", "Dependencias (Next.js, React, Prisma, Zod) con versiones fijas, y los comandos npm run dev, build y test."),
        ("prisma.config.*", "Configuración de Prisma: dónde están el esquema, las migraciones y la base de datos (DATABASE_URL del .env)."),
        ("prisma/schema.prisma", "Las tablas de la base de datos: un model por tabla (andamio agrega uno por recurso). Después de cambiarlo: npx prisma migrate dev."),
        ("proxy.*", "Permite que otras páginas (React con Vite, Expo web) usen la API de este proyecto (CORS). Se configura con CORS_ALLOWED_ORIGINS."),
        ("lib/db.*", "Conexión a la base de datos con Prisma: prisma.producto.findMany(), create(), update(), delete()."),
        ("lib/errores.*", "Errores con el formato de Django REST (400 {campo: [mensaje]}, 404 {detail}) y responder(), que los convierte en la respuesta de cada ruta."),
        ("lib/fechas.*", "Cómo salen y se leen las fechas: \"2026-11-19\", y las fechas con hora en hora local con su zona, igual que Django."),
        ("lib/validacion.*", "Funciones para validar los datos con Zod (texto, entero, decimal, fecha...), con los mensajes en español de Django."),
        ("app/api/*/[[]id]/route.*", "La API de un registro: GET (ver), PUT (reemplazar), PATCH (modificar) y DELETE (eliminar) en /api/productos/3/."),
        ("app/api/*/route.*", "La API del recurso: GET (listar, con búsqueda, orden y filtros) y POST (crear) en /api/productos/."),
        ("app/api/*/esquema.*", "Qué datos acepta el recurso (validación con Zod) y cómo se ve cada registro en el JSON."),
        ("tests/api.*", "Ayuda para los tests: llama a las funciones de app/api/ sin levantar el servidor, con otra base (test.db)."),
        ("tests/*.test.*", "5 tests de la API: listar, crear, ver, modificar y eliminar. Se ejecutan con npm test."),
    ],
    "reflex": [
        ("rxconfig.py", "Configuración de Reflex: el nombre de la app, la base de datos, los puertos y que no envíe datos de uso."),
        ("requirements.txt", "Librerías del proyecto con sus versiones. Se instalan con pip install -r requirements.txt."),
        ("*/validacion.py", "Validación de los formularios: los errores de Pydantic en español (como Django) y las fechas con hora en hora local."),
        ("*/plantilla.py", "La plantilla de todas las páginas: el menú (lista ENLACES, andamio agrega uno por página) y el contenido."),
        ("*/paginas/inicio.py", "La página de inicio (la dirección /)."),
        ("*/paginas/*.py", "Una página: una función que devuelve componentes. Si es la de un recurso, también su estado (los datos y las acciones)."),
        ("*/modelos/*.py", "El modelo: la tabla de la base de datos (SQLModel) y los datos que acepta el formulario, con su validación."),
        ("*/componentes/*.py", "Un componente: una función que arma una parte de la interfaz para reutilizarla."),
        ("*/estados/*.py", "Un estado: datos de la aplicación y las acciones (eventos) que los cambian."),
        ("*/servicios/http.py", "Pedidos a la API (con httpx), con su dirección (API_URL del .env) y el manejo de errores."),
        ("*/servicios/*.py", "Funciones para un recurso de la API: listar, obtener, crear, actualizar y eliminar."),
        ("*/__init__.py", "Convierte la carpeta en un paquete de Python, para poder hacer import desde ella."),
        ("*/*.py", "La aplicación: registra cada página con su dirección (andamio agrega las líneas)."),
    ],
    "react": [
        ("package.json", "Dependencias (React, Vite) con versiones fijas, y los comandos npm run dev y npm run build."),
        ("index.html", 'La página que carga el navegador: React se dibuja dentro de <div id="root">.'),
        ("vite.config.*", "Configuración de Vite: el servidor de desarrollo y el empaquetador."),
        ("tsconfig*.json", "Configuración de TypeScript (modo estricto)."),
        ("src/main.*", "Punto de entrada: monta el componente App en la página."),
        ("src/App.module.css", "Estilos de App. Las clases de un .module.css solo afectan a ese componente."),
        ("src/App.*", "Componente principal: el menú y las rutas (qué página se ve en cada dirección). andamio agrega acá las páginas que generes."),
        ("src/index.css", "Estilos globales de toda la aplicación."),
        ("src/components/index.*", "Exporta todos los componentes desde un lugar: import { Tarjeta } from './components'."),
        ("src/components/*/index.*", "Permite importar el componente por el nombre de su carpeta."),
        ("src/components/*Detalle/*Detalle.?sx", "Muestra un registro con los botones Editar y Eliminar. No llama a la API: recibe los datos y avisa con onEditar y onEliminar."),
        ("src/components/*.module.css", "Estilos propios del componente (clase .root): no afectan al resto."),
        ("src/components/*", "El componente: una función que recibe props y devuelve lo que se ve."),
        ("src/pages/*/index.*", "Permite importar las páginas de la carpeta por su nombre."),
        ("src/pages/InicioPage/InicioPage.?sx", "La página de inicio (la ruta /)."),
        ("src/pages/*/*ListaPage.*", "La lista: pide los registros a la API con listar() y enlaza al detalle de cada uno."),
        ("src/pages/*/*DetallePage.*", "El detalle (ruta /…/:id): pide el registro con obtener(id) y lo elimina con eliminar(id)."),
        ("src/pages/*/*FormPage.*", "El formulario para crear y editar: usa crear() o actualizar() y muestra los errores de validación de la API."),
        ("src/pages/*.module.css", "Estilos propios de la página."),
        ("src/pages/*", "Una página completa de la aplicación."),
        ("src/hooks/useConsulta.*", "Hook genérico para pedir datos a la API: guarda el resultado, si está cargando y el error. Lo usan las páginas del CRUD."),
        ("src/hooks/use*", "Un hook: estado y lógica para reutilizar en varios componentes."),
        ("src/services/http.*", "Funciones para pedir datos a la API (GET, POST, PATCH, DELETE) con manejo de errores. Usa VITE_API_URL del .env."),
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
        ("services/http.*", "Funciones para pedir datos a la API. Explica qué dirección usar en el emulador, el navegador o un celular."),
        ("services/*Service.*", "Funciones para un recurso de la API: listar, obtener, crear, actualizar y eliminar, con los tipos de cada campo."),
    ],
}

LENGUAJES = {".py": "python", ".ts": "ts", ".tsx": "ts", ".js": "ts", ".jsx": "ts", ".json": "json", ".sql": "sql", ".css": "css", ".html": "html", ".md": "md"}


def descripcion(clave: str, ruta: str) -> str | None:
    # Un stack que extiende a otro (next-fullstack -> next) usa también sus explicaciones.
    stack = stacks.por_clave(clave)
    claves = [clave, stack.extiende] if stack and stack.extiende else [clave]
    for k in claves:
        if ruta in CARPETAS.get(k, {}):
            return CARPETAS[k][ruta]
    for patron, texto in [e for k in claves for e in DESCRIPCIONES[k]] + _COMUNES:
        if fnmatch.fnmatchcase(ruta, patron):
            return texto
    return None


# --- Ejecución ---------------------------------------------------------------------------


def _limpiar(texto: str) -> str:
    # La página muestra la terminal de un alumno en Windows, aunque se genere en Linux.
    texto = texto.replace("source .venv/bin/activate", ".venv\\Scripts\\activate")
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
        "camino": camino(stack.clave, variante, archivos),
        "combinaciones": combinaciones(stack.clave, variante),
    }


EJEMPLOS = RAIZ / "sitio" / "ejemplos"


def extensiones(variante: str) -> dict[str, str]:
    """Las extensiones de los archivos de código según el lenguaje: ts/tsx, js/jsx (o py)."""
    return {"ts": {"ext": "ts", "extx": "tsx"}, "js": {"ext": "js", "extx": "jsx"}}.get(variante, {"ext": "py", "extx": "py"})


def camino(clave: str, variante: str, archivos: list[dict]) -> list[dict]:
    """Las lecciones de la guía en orden: piezas y temas, con los archivos reales de cada tema."""
    rutas = {a["ruta"] for a in archivos}
    lecciones = []
    for item in CAMINO[clave]:
        if not item.startswith("tema:"):
            lecciones.append({"tipo": "pieza", "clave": item})
            continue
        tema = TEMAS[clave][item.removeprefix("tema:")]
        mostrados = [ruta.format(**extensiones(variante)) for ruta in tema["archivos"]]
        faltan = [ruta for ruta in mostrados if ruta not in rutas]
        if faltan:
            raise SystemExit(f"{clave}/{variante}: el tema {item} muestra archivos que el proyecto no tiene: {faltan}")
        lecciones.append({"tipo": "tema", "id": item.removeprefix("tema:"), "titulo": tema["titulo"], "texto": tema["texto"], "archivos": mostrados})
    return lecciones


def archivos_combinacion(combinacion: dict, variante: str) -> list[tuple[str, Path]]:
    """(ruta en el proyecto, archivo de ejemplo) de una combinación, para esa variante."""
    valores = {**extensiones(variante), "v": variante}
    return [(ruta.format(**valores), EJEMPLOS / ejemplo.format(**valores)) for ruta, ejemplo in combinacion.get("archivos", [])]


def combinaciones(clave: str, variante: str) -> list[dict]:
    resultado = []
    for combinacion in COMBINACIONES.get(clave, []):
        archivos = []
        for ruta, ejemplo in archivos_combinacion(combinacion, variante):
            if not ejemplo.is_file():
                raise SystemExit(f"Falta el ejemplo {ejemplo.relative_to(RAIZ)} ({clave}, {combinacion['id']})")
            lenguaje = LENGUAJES.get(Path(ruta).suffix, "texto")
            archivos.append({"ruta": ruta, "lenguaje": lenguaje, "contenido": ejemplo.read_text(encoding="utf-8")})
        pasos = [
            {"lugar": lugar, "comando": f"{PROGRAMA} {comando}" if comando.startswith("nuevo ") else comando}
            for lugar, comando in combinacion["pasos"]
        ]
        resultado.append(
            {
                "id": combinacion["id"],
                "titulo": combinacion["titulo"],
                "usa": combinacion["usa"],
                "texto": combinacion["texto"],
                "pasos": pasos,
                "archivos": archivos,
                "claves": combinacion["claves"],
            }
        )
    return resultado


def _que_se_modifico(salida: str, ruta: str) -> str:
    """Lo que andamio dice que cambió: "  ~ main.py  (import del menú, opción en MENUS)"."""
    limpia = re.sub(r"\x1b\[[\d;]*m", "", salida).replace("\\", "/")
    encontrado = re.search(rf"~ {re.escape(ruta)}\s+\((.*)\)", limpia)
    return encontrado.group(1) if encontrado else ""


def demo_tecnologia(base: Path, stack) -> dict:
    """Cada tecnología en su propia carpeta: Django y FastAPI usan el mismo nombre (mi-api)."""
    global _base_actual
    base = base / stack.clave
    base.mkdir()
    _base_actual = str(base.resolve())
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
    proyecto = base / "python" / TECNOLOGIAS["python"]["carpeta"]
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
            return {"version": andamio.__version__, "menu": sesion, "tecnologias": tecnologias}
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
