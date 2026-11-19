# @@proyectoTitulo@@

Aplicación de consola con Python y SQLite.

## Ejecutar

```
python main.py
```

## Agregar una entidad

```
python -m andamio nuevo entidad producto nombre:str precio:float stock:int
```

Tipos de campo: `str` (texto), `int` (número entero), `float` (número con decimales).

## Estructura

```
main.py            menú principal (diccionario MENUS)
db.py              conexión a la base (get_conexion)
sql/schema.sql     tablas
entidades/         funciones crear, listar, obtener, actualizar y eliminar de cada tabla
menus/             menú de cada entidad y funciones para pedir datos (entrada.py)
```
