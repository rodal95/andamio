"""Tests de la API de @@titulo@@. Ejecutalos con: python -m pytest"""

@@imports_test@@
@@imports_login_test@@
URL = "/api/@@plural@@/"

DATOS = {
    @@datos_prueba@@
}

DATOS_MODIFICADOS = {
    @@datos_modificados@@
}


def crear(cliente):
    respuesta = cliente.post(URL, json=DATOS)
    assert respuesta.status_code == 201, respuesta.json()
    return respuesta.json()


def test_listar(cliente):
    crear(cliente)
    respuesta = cliente.get(URL)
    assert respuesta.status_code == 200
    # Sin paginación, la respuesta es directamente una lista.
    assert len(respuesta.json()) == 1


def test_crear(cliente):
    creado = crear(cliente)
    assert creado["id"] == 1


def test_obtener(cliente):
    creado = crear(cliente)
    respuesta = cliente.get(f"{URL}{creado['id']}/")
    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == creado["id"]


def test_actualizar(cliente):
    creado = crear(cliente)
    respuesta = cliente.put(f"{URL}{creado['id']}/", json=DATOS_MODIFICADOS)
    assert respuesta.status_code == 200, respuesta.json()
    @@verificacion@@


def test_eliminar(cliente):
    creado = crear(cliente)
    assert cliente.delete(f"{URL}{creado['id']}/").status_code == 204
    assert cliente.get(f"{URL}{creado['id']}/").status_code == 404
@@tests_login@@
