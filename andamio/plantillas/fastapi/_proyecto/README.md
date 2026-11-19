# @@proyectoTitulo@@

API REST con FastAPI y SQLModel.

## Primera vez

En Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

En Linux o Mac, activá el entorno con `source .venv/bin/activate`.

La documentación interactiva de la API queda en http://127.0.0.1:8000/docs

## Agregar un recurso

```
python -m andamio nuevo recurso producto nombre:str precio:decimal stock:int
```

El recurso queda en `/api/productos/`, con la misma forma que la API de Django:
los servicios y el CRUD de React y React Native funcionan igual. Tipos de campo:
`str`, `text`, `int`, `decimal`, `float`, `bool`, `date`, `datetime`, `email`.

**Ojo:** las tablas se crean al arrancar, pero si después cambiás un modelo (por
ejemplo, le agregás un campo), la tabla no se modifica sola. Mientras desarrollás,
borrá `datos.db` y volvé a arrancar (se pierden los datos de prueba).

## Tests

```
python -m pytest
```

## Estructura

```
app/main.py        la aplicación: CORS, errores y los routers de cada recurso
app/config.py      configuración leída del .env (base de datos, CORS, zona horaria)
app/db.py          conexión a la base de datos
app/tipos.py       tipos que usan todos los recursos
app/errores.py     errores de validación en español (formato de Django REST)
app/<recurso>/     modelo.py (tabla y esquemas) y router.py (las rutas de la API)
tests/             tests de cada recurso
```
