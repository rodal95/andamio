# Reglas para no romper nada

andamio valida casi todo antes de escribir (y si algo falla, no toca ningún archivo),
pero hay cosas que dependen de cómo lo usás. Esta es la línea a seguir.

## 1. Primero el proyecto, después las piezas, siempre desde adentro

```
python -m andamio crear django mi-api      (una vez, desde la carpeta donde guardás tus proyectos)
cd mi-api
python -m andamio nuevo recurso producto nombre:str precio:decimal
```

- `nuevo` busca el proyecto desde la carpeta actual hacia arriba: funciona en
  cualquier subcarpeta, pero no afuera. Si dice **"No encontré un proyecto"**, hacé `cd`.
- No crees un proyecto adentro de otro (andamio te avisa si lo hacés).
- `python -m andamio info` te dice qué proyecto detectó y qué piezas acepta.

## 2. Nombres en singular; campos `nombre:tipo`

- `producto`, no `productos`: andamio arma el plural solo (`productos`, `/api/productos/`).
  Si el plural automático está mal, indicalo: `--plural paises`.
- Escribilo como quieras (`Línea Venta`, `linea-venta`): andamio lo adapta a cada
  lenguaje (`LineaVenta`, `linea_venta`, `lineas-venta`).
- Campos: `nombre:tipo`. Sin tipo es `str`. Tipos: `str`, `text`, `int`, `decimal`,
  `float`, `bool`, `date`, `datetime`, `email`.
- No uses `id`, `creado` ni `actualizado` (se crean solos), ni palabras reservadas
  (`class`, `type`, `objects`...): andamio te explica por qué.

## 3. Los mismos campos en la API y en la interfaz

Es la regla más importante cuando combinás proyectos. El recurso de la API y el
servicio (o el `crud`) de la interfaz se generan con **exactamente los mismos campos**:

```
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int   (en la API)
python -m andamio nuevo crud    producto nombre:str precio:decimal stock:int   (en la web)
```

Copiá y pegá la lista de campos. Si no coinciden, la API responde **400** y dice qué
campo falta o sobra.

## 4. No borres las líneas `andamio:...`

Los archivos que andamio modifica tienen líneas como:

```python
# --- andamio:apps (no borrar esta línea) ---
```

Ahí agrega las apps, rutas, enlaces del menú, imports... Si la borrás, no es grave:
la pieza se genera igual y andamio te muestra qué pegar y en qué archivo. Pero es más
cómodo dejarlas. Podés escribir tu código arriba o abajo de ellas.

## 5. andamio nunca sobrescribe

Si un archivo ya existe, avisa y no toca nada. Para regenerar una pieza, borrá
primero sus archivos (y su línea en `settings.py`, `urls.py`, el menú o el router).
Antes de generar algo grande, probá con `--simular`: muestra qué crearía y qué
modificaría, sin escribir.

## 6. Después de un modelo nuevo, la migración

| Tecnología | Qué hacer después de `nuevo recurso` / `nuevo crud` |
|---|---|
| Django y Django con plantillas | `python manage.py makemigrations <app>` y `python manage.py migrate` (o `--migrar`) |
| Express y Next.js full stack | `npx prisma migrate dev --name <cambio>` (o `--migrar`) |
| Reflex (`crud`) | `reflex db makemigrations` y `reflex db migrate` (o `--migrar`) |
| FastAPI | nada: la tabla se crea al arrancar (si cambiás un modelo, borrá `datos.db`) |

Si agregás un campo **a mano** a un modelo de Django, también va en la lista `fields`
del serializer (API) o del formulario (`forms.py`, en el sitio con plantillas).

## 7. Puertos y direcciones

| Qué | Dirección |
|---|---|
| Las APIs (Django, FastAPI, Express) | http://localhost:8000/api |
| React, Vue y la web HTML | http://localhost:5173 |
| Next.js y Reflex | http://localhost:3000 |
| Django con plantillas | http://127.0.0.1:8000 |

Las APIs ya aceptan pedidos (CORS) de los puertos 5173, 3000 y 8081 (Expo web).
Si cambiás un puerto, agregalo a `CORS_ALLOWED_ORIGINS` en el `.env` de la API.
No levantes Django con plantillas y una API en el puerto 8000 al mismo tiempo
(`python manage.py runserver 8001` usa otro).

## 8. Cada cosa en su lugar

- La web HTML se sirve con `python -m http.server 5173`: abrir el `.html` con doble
  clic no permite los `import` de JavaScript.
- El `.env` no se sube a git (tiene la clave secreta); `.env.example` sí. Si cambiás
  el `.env` de React, Vue o Next.js, reiniciá `npm run dev`.
- Python: activá el entorno virtual (`.venv\Scripts\activate` en Windows) antes de
  `pip install` y `manage.py`. Node: `npm install` una vez por proyecto.

## 9. Login y recursos protegidos

- `--protegido` pide login para crear, modificar y eliminar (leer sigue libre).
- En la API de Django, generá `nuevo login` **antes** de usar recursos protegidos
  desde una web: es lo que da los tokens. Después, `pip install -r requirements.txt`.
- La interfaz tiene que mandar el token (`Authorization: Bearer <token>`). La web
  HTML, React, Vue y Next.js ya lo hacen solos si lo guardaste: `localStorage` con la
  clave `token` (en React, Vue y Next.js, con `guardarToken()` de `services/http`).
  Ver [combinaciones](combinaciones.md#login-con-jwt-desde-react-vue-o-nextjs).
  React Native todavía no.

## 10. Para cambiar el código que se genera

```
python -m andamio plantillas exportar
```

Copia las plantillas a `.andamio/plantillas/` de tu proyecto: si las editás, andamio
usa tu versión (cada carpeta tiene un `LEEME.md` con los marcadores `@@...@@`).
