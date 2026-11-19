"""Reporte de productos: usa las funciones de la entidad desde tu propio programa.

Ejecutalo con: python reporte.py
"""

import db
from entidades import producto

db.inicializar()  # crea las tablas si todavía no existen

producto.crear("Yerba mate", 4850.5, 24)

total = 0
for fila in producto.listar():
    print(f"{fila['nombre']}: $ {fila['precio']} ({fila['stock']} en stock)")
    total += fila["precio"] * fila["stock"]

print(f"Valor del stock: $ {total:.2f}")
