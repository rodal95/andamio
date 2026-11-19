"""@@proyectoTitulo@@: aplicación de consola con Python y SQLite.

Para ejecutarla:  python main.py
"""

import db

# Cada entidad tiene su propio menú. andamio agrega los import solo.
# --- andamio:imports (no borrar esta línea) ---

# Opciones del menú principal: el texto que se muestra y la función que abre el submenú.
MENUS = {
    # --- andamio:menus (no borrar esta línea) ---
}


def main():
    db.inicializar()  # crea las tablas que falten
    while True:
        print()
        print("=== @@proyectoTitulo@@ ===")
        opciones = list(MENUS.items())
        if not opciones:
            print("Todavía no hay entidades. Generá una con:")
            print("    python -m andamio nuevo entidad producto nombre:str precio:float")
        for numero, (titulo, _) in enumerate(opciones, start=1):
            print(f"{numero}. {titulo}")
        print("0. Salir")

        eleccion = input("Elegí una opción: ").strip()
        if eleccion == "0":
            print("¡Hasta luego!")
            break
        if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
            _, abrir_menu = opciones[int(eleccion) - 1]
            abrir_menu()
        else:
            print("Opción inválida.")


# Este bloque se ejecuta solo cuando corrés "python main.py",
# no cuando otro archivo hace "import main".
if __name__ == "__main__":
    main()
