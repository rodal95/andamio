# guía: Guardar, listar, modificar y eliminar @@plural@@ en SQLite (la tabla está en sql/schema.sql).
# guía: Lo usa menus/menu_@@nombre@@.py. Las consultas usan ? para que los datos no se mezclen con el SQL.
"""Funciones para la tabla @@plural@@: crear, listar, obtener, actualizar y eliminar.

Todas las consultas usan signos "?" para los valores, en lugar de armar el SQL
pegando textos. Así SQLite se encarga de las comillas y se evita la inyección SQL.
"""

from db import get_conexion


def crear(@@parametros@@):
    # TODO(logica): validaciones antes de guardar (ej.: que el precio sea mayor que cero).
    """Guarda un registro nuevo y devuelve su id."""
    with get_conexion() as conexion:
        cursor = conexion.execute(
            "INSERT INTO @@plural@@ (@@columnas@@) VALUES (@@signos@@)",
            @@valores@@,
        )
        return cursor.lastrowid


def listar():
    """Devuelve todos los registros como una lista de diccionarios."""
    with get_conexion() as conexion:
        filas = conexion.execute("SELECT * FROM @@plural@@ ORDER BY id").fetchall()
        return [dict(fila) for fila in filas]


def obtener(id_@@nombre@@):
    """Devuelve el registro con ese id (como diccionario), o None si no existe."""
    with get_conexion() as conexion:
        fila = conexion.execute("SELECT * FROM @@plural@@ WHERE id = ?", (id_@@nombre@@,)).fetchone()
        return dict(fila) if fila else None


def actualizar(id_@@nombre@@, @@parametros@@):
    """Modifica un registro. Devuelve True si existía y False si no."""
    with get_conexion() as conexion:
        cursor = conexion.execute(
            "UPDATE @@plural@@ SET @@asignaciones@@ WHERE id = ?",
            (@@parametros@@, id_@@nombre@@),
        )
        return cursor.rowcount > 0


def eliminar(id_@@nombre@@):
    """Borra un registro. Devuelve True si existía y False si no."""
    with get_conexion() as conexion:
        cursor = conexion.execute("DELETE FROM @@plural@@ WHERE id = ?", (id_@@nombre@@,))
        return cursor.rowcount > 0
