"""Menú de consola para @@titulo@@."""

from entidades import @@nombre@@
@@imports_relaciones@@
from menus.entrada import confirmar, mostrar_filas, pedir


def mostrar_menu():
    """Muestra el menú hasta que se elija "Volver"."""
    while True:
        print()
        print("--- @@titulo@@ ---")
        print("1. Listar")
        print("2. Agregar")
        print("3. Modificar")
        print("4. Eliminar")
        # --- andamio:opciones (no borrar esta línea) ---
        print("0. Volver")
        opcion = input("Elegí una opción: ").strip()
        if opcion == "1":
            listar()
        elif opcion == "2":
            agregar()
        elif opcion == "3":
            modificar()
        elif opcion == "4":
            eliminar()
        # --- andamio:acciones (no borrar esta línea) ---
        elif opcion == "0":
            return
        else:
            print("Opción inválida.")


def listar():
    mostrar_filas(@@nombre@@.listar())


def agregar():
    @@pedir_campos@@
    nuevo_id = @@nombre@@.crear(@@parametros@@)
    print(f"Se guardó con el id {nuevo_id}.")


def modificar():
    id_@@nombre@@ = pedir("Id a modificar", int)
    actual = @@nombre@@.obtener(id_@@nombre@@)
    if actual is None:
        print("No existe un registro con ese id.")
        return
    print("Escribí el valor nuevo, o apretá Enter para dejar el que está entre corchetes.")
    @@pedir_campos_actual@@
    @@nombre@@.actualizar(id_@@nombre@@, @@parametros@@)
    print("Cambios guardados.")


def eliminar():
    id_@@nombre@@ = pedir("Id a eliminar", int)
    if @@nombre@@.obtener(id_@@nombre@@) is None:
        print("No existe un registro con ese id.")
        return
    if confirmar("¿Seguro que querés eliminarlo?"):
        @@nombre@@.eliminar(id_@@nombre@@)
        print("Eliminado.")
@@funciones_relaciones@@
