# @@proyectoTitulo@@

Aplicación web hecha solo con Python, con Reflex: las páginas, su estado y la base de
datos (SQLite) se escriben en Python. Reflex arma la parte del navegador por vos.

## Primera vez

Necesitás Python 3.11 o más nuevo (`python --version`). La primera vez que se ejecuta,
Reflex descarga lo que necesita para el navegador, así que hace falta internet.

En Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
reflex run
```

En Linux o Mac, activá el entorno con `source .venv/bin/activate`.

Abrí http://localhost:3000

## Generar piezas

```
python -m andamio nuevo pagina Contacto
python -m andamio nuevo componente Tarjeta
python -m andamio nuevo estado contador
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int --migrar
python -m andamio nuevo crud-api producto nombre:str precio:decimal stock:int
python -m andamio nuevo servicio producto nombre:str precio:decimal stock:int
```

- `crud`: la tabla en la base de datos de este proyecto (`modelos/`) y una página para
  listar, agregar, editar y eliminar. `--migrar` crea la tabla; sin esa opción, la primera
  vez `reflex db init` y después `reflex db makemigrations` y `reflex db migrate`.
- `crud-api`: la misma página, pero los datos están en una API hecha con andamio (Django,
  FastAPI o Express) y se piden con un servicio. La dirección está en `API_URL` (`.env`).
- `servicio`: solo las funciones para usar un recurso de esa API.

## Estructura

```
rxconfig.py                   configuración: nombre, base de datos, puertos
@@proyecto_snake@@/@@proyecto_snake@@.py        la aplicación: registra cada página con su dirección
@@proyecto_snake@@/plantilla.py         el menú y lo que rodea a todas las páginas
@@proyecto_snake@@/paginas/             las páginas (una función por página)
@@proyecto_snake@@/componentes/         componentes reutilizables
@@proyecto_snake@@/estados/             estados (datos y acciones que comparten las páginas)
@@proyecto_snake@@/modelos/             las tablas de la base de datos (SQLModel)
@@proyecto_snake@@/servicios/           funciones para usar una API externa
alembic/                      las migraciones de la base (las crea reflex db init)
```
