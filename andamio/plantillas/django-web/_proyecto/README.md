# @@proyectoTitulo@@

Sitio web con Django y plantillas HTML (todo en un solo proyecto: las páginas se
arman en el servidor). Trae login, registro y panel de administración.

## Primera vez

En Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Linux o Mac, activá el entorno con `source .venv/bin/activate`.
Abrí http://127.0.0.1:8000

## Agregar una sección (crud)

```
python -m andamio nuevo crud producto nombre:str precio:decimal stock:int --migrar
```

Crea la app `productos` con su modelo, formulario, vistas (lista, detalle, crear,
editar y eliminar), plantillas, rutas, admin y tests, y el enlace en el menú.
Con `--protegido`, crear, editar y eliminar piden iniciar sesión.

## Agregar una página

```
python -m andamio nuevo pagina Contacto
```

Crea `templates/paginas/contacto.html` en `/contacto/`, con su enlace en el menú.

## Tests

```
python manage.py test
```
