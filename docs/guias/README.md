# Guías de andamio

Estas guías explican qué podés hacer con cada tecnología, con qué comando, cómo se
combinan las piezas y qué conviene respetar para que todo funcione a la primera.
La [página de andamio](https://rodal95.github.io/andamio/) tiene además una guía
interactiva por tecnología, con la salida real de cada comando y todos los archivos
generados.

| Guía | Para qué |
|---|---|
| [Todos los comandos](comandos.md) | Referencia por tecnología: cómo crear el proyecto, cada pieza con su comando, qué genera y un ejemplo de uso. |
| [Cómo combinar](combinaciones.md) | Qué frontend va con qué API, una página que muestra datos de un servicio, y el recorrido completo API + web. |
| [Reglas para no romper nada](reglas.md) | La línea a seguir para evitar los errores más comunes. |
| [API REST con Django + login JWT](django-api-jwt.md) | Paso a paso: CRUD completo (modelo, serializer, admin, urls, configuración) y login con SimpleJWT. |
| [Sitio con Django y plantillas](django-plantillas.md) | La otra forma de usar Django: un solo proyecto (monolito) con vistas y plantillas HTML. |
| [Estilos](estilos.md) | `tema` (colores y modo oscuro de todo el proyecto), `ui` (partes listas: tarjetas, modal, navbar...) y `estilo` (el CSS de tu componente o página). |

## ¿Qué tecnología elijo?

```
¿Necesitás una base de datos y una API que usen otras apps?
   └─ sí → una API: django (con login JWT), fastapi o express
            y después una interfaz que la use: web, react, vue, next o react-native

¿Querés todo en un solo proyecto?
   ├─ en Python, con páginas HTML armadas en el servidor → django-web
   ├─ en Python, con una interfaz moderna sin escribir JavaScript → reflex
   └─ en JavaScript/TypeScript → next-fullstack

¿Estás empezando?
   ├─ con Python y SQL, en la consola → python
   └─ con la web, sin instalar Node → web (HTML + CSS + JavaScript)
```

| Tipo (`crear`) | Qué es | Piezas (`nuevo`) |
|---|---|---|
| `python` | Programa de consola con SQLite | `entidad` |
| `django` | API REST con Django REST Framework | `recurso`, `login` |
| `django-web` | Sitio con Django y plantillas (monolito) | `crud`, `pagina`, `tema`, `ui`, `estilo` |
| `fastapi` | API REST con FastAPI + SQLModel | `recurso` |
| `express` | API REST con Express + Prisma (TS o JS) | `recurso` |
| `web` | Página con HTML, CSS y JavaScript, sin instalar nada | `pagina`, `componente`, `servicio`, `crud`, `tema`, `ui`, `estilo` |
| `react` | React + Vite (TS o JS) | `componente`, `pagina`, `hook`, `servicio`, `crud`, `tema`, `ui`, `estilo` |
| `vue` | Vue 3 + Vite + Vue Router | `componente`, `pagina`, `composable`, `servicio`, `crud`, `tema`, `ui`, `estilo` |
| `react-native` | App de celular con Expo (TS o JS) | `pantalla`, `componente`, `hook`, `servicio`, `tema` |
| `next` | Next.js que usa una API (TS o JS) | `componente`, `pagina`, `hook`, `servicio`, `crud`, `tema`, `ui`, `estilo` |
| `next-fullstack` | Next.js con su propia API y base | `recurso`, `crud`, `pagina`, `componente`, `hook`, `servicio`, `tema`, `ui`, `estilo` |
| `reflex` | Web hecha solo con Python | `crud`, `crud-api`, `pagina`, `componente`, `estado`, `servicio`, `tema` |

## Los tres comandos que vas a usar siempre

```
python -m andamio crear <tipo> <nombre>          crea el proyecto (una vez)
python -m andamio nuevo <pieza> <nombre> [campos] agrega una pieza (todas las veces que quieras)
python -m andamio comandos                        el árbol de todos los comandos, con la forma general de cada pieza
python -m andamio info                            qué piezas y tipos de campo hay en este proyecto
```

Los nombres y los campos son tuyos: en las guías los ejemplos usan `producto`,
`Contacto` o `Tarjeta`, pero cada pieza se genera con el nombre y los campos que
necesites (`nuevo crud cliente nombre:str email:email`, `nuevo pagina SobreNosotros`).

Y si no te acordás de nada: `python -m andamio` abre un menú que te pregunta todo.
