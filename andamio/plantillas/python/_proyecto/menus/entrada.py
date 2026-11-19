"""Funciones para pedir datos por teclado y mostrar resultados."""

NOMBRES_DE_TIPO = {
    str: "un texto",
    int: "un número entero (sin decimales)",
    float: "un número (podés usar decimales)",
}


def pedir(texto, tipo=str, actual=None):
    """Pide un dato y lo convierte al tipo indicado: str, int o float.

    Si el dato no es válido, explica por qué y lo vuelve a pedir.
    Si se pasa `actual`, apretar Enter conserva ese valor (sirve para modificar).

    Ejemplos:
        nombre = pedir("Nombre")
        precio = pedir("Precio", float)
        stock = pedir("Stock", int, actual=10)
    """
    while True:
        sufijo = f" [{actual}]" if actual is not None else ""
        respuesta = input(f"{texto}{sufijo}: ").strip()
        if respuesta == "":
            if actual is not None:
                return actual
            print("  Este dato es obligatorio.")
            continue
        if tipo is float:
            respuesta = respuesta.replace(",", ".")  # acepta 10,5 además de 10.5
        try:
            return tipo(respuesta)
        except ValueError:
            print(f"  Tiene que ser {NOMBRES_DE_TIPO[tipo]}.")


def confirmar(texto):
    """Pregunta sí o no. Devuelve True si la respuesta es "s"."""
    return input(f"{texto} (s/n): ").strip().lower() in ("s", "si", "sí")


def mostrar_filas(filas):
    """Muestra una lista de registros (diccionarios) como una tabla."""
    if not filas:
        print("  (no hay registros)")
        return
    columnas = list(filas[0].keys())
    anchos = {c: max(len(c), *(len(str(f[c])) for f in filas)) for c in columnas}
    print("  " + " | ".join(c.ljust(anchos[c]) for c in columnas))
    print("  " + "-+-".join("-" * anchos[c] for c in columnas))
    for fila in filas:
        print("  " + " | ".join(str(fila[c]).ljust(anchos[c]) for c in columnas))
