"""Conexión a la base de datos SQLite."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

CARPETA = Path(__file__).parent

# Archivo de la base de datos. Se crea solo la primera vez que se usa.
RUTA_DB = CARPETA / "datos.db"

# Script con las tablas. andamio agrega una tabla por cada entidad que generes.
RUTA_SCHEMA = CARPETA / "sql" / "schema.sql"


@contextmanager
def get_conexion():
    """Abre una conexión y se ocupa de confirmar los cambios y cerrarla.

    Uso:
        with get_conexion() as conexion:
            conexion.execute("INSERT INTO productos (nombre) VALUES (?)", ("Mate",))

    - Si todo sale bien, guarda los cambios (commit).
    - Si hay un error, los descarta (rollback) y deja pasar el error.
    - En cualquier caso, cierra la conexión.

    Ojo: "with sqlite3.connect(...)" hace commit/rollback pero NO cierra la conexión.
    Por eso usamos esta función.
    """
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row  # permite leer las columnas por nombre: fila["nombre"]
    conexion.execute("PRAGMA foreign_keys = ON")  # SQLite no controla las claves foráneas si no se lo pedís
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar():
    """Crea las tablas que todavía no existen, ejecutando sql/schema.sql."""
    with get_conexion() as conexion:
        conexion.executescript(RUTA_SCHEMA.read_text(encoding="utf-8"))
