# @@proyectoTitulo@@

API REST con Django y Django REST Framework.

## Primera vez

En Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

En Linux o Mac, activá el entorno con `source .venv/bin/activate`.

La documentación de la API queda en http://127.0.0.1:8000/api/docs/

## Agregar un recurso

```
andamio nuevo recurso producto nombre:str precio:decimal stock:int
python manage.py makemigrations productos
python manage.py migrate
```

El recurso queda en `/api/productos/`. Tipos de campo: `str`, `text`, `int`,
`decimal`, `float`, `bool`, `date`, `datetime`, `email`.

## Tests

```
python manage.py test
```
