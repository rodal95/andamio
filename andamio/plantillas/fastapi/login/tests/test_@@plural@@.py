"""Tests del login con JWT. Ejecutalos con: python -m pytest"""

from app.@@plural@@.modelo import Usuario
from app.@@plural@@.seguridad import hash_de, puede_ingresar

USUARIO = {"username": "ana", "email": "ana@ejemplo.com", "password": "una-clave-larga-123"}


def registrar(cliente):
    respuesta = cliente.post("/api/registro/", json=USUARIO)
    assert respuesta.status_code == 201, respuesta.json()
    return respuesta.json()


def tokens(cliente, password=USUARIO["password"]):
    return cliente.post("/api/token/", json={"username": "ana", "password": password})


def test_registro(cliente):
    usuario = registrar(cliente)
    assert usuario["username"] == "ana"
    assert "password" not in usuario and "password_hash" not in usuario


def test_registro_rechaza_una_clave_debil_y_un_usuario_repetido(cliente):
    respuesta = cliente.post("/api/registro/", json={**USUARIO, "password": "123"})
    assert respuesta.status_code == 400
    assert "password" in respuesta.json()
    registrar(cliente)
    respuesta = cliente.post("/api/registro/", json=USUARIO)
    assert respuesta.status_code == 400
    assert "username" in respuesta.json()


def test_login_devuelve_los_tokens(cliente):
    registrar(cliente)
    respuesta = tokens(cliente)
    assert respuesta.status_code == 200
    assert {"access", "refresh"} <= set(respuesta.json())


def test_login_con_clave_incorrecta(cliente):
    registrar(cliente)
    assert tokens(cliente, "otra").status_code == 401


def test_un_usuario_que_no_existe_o_desactivado_no_ingresa(cliente):
    # guía: Las dos respuestas son iguales (y tardan lo mismo): no dan pistas de qué usuarios existen.
    assert tokens(cliente).status_code == 401
    desactivado = Usuario(username="ana", password_hash=hash_de("una-clave-larga-123"), activo=False)
    assert not puede_ingresar(desactivado, "una-clave-larga-123")


def test_yo_con_y_sin_token(cliente):
    registrar(cliente)
    assert cliente.get("/api/yo/").status_code == 401
    acceso = tokens(cliente).json()["access"]
    respuesta = cliente.get("/api/yo/", headers={"Authorization": f"Bearer {acceso}"})
    assert respuesta.status_code == 200
    assert respuesta.json()["username"] == "ana"
    assert cliente.get("/api/yo/", headers={"Authorization": "Bearer no-es-un-token"}).status_code == 401


def test_renovar_el_token(cliente):
    registrar(cliente)
    refresco = tokens(cliente).json()["refresh"]
    respuesta = cliente.post("/api/token/refresh/", json={"refresh": refresco})
    assert respuesta.status_code == 200
    assert "access" in respuesta.json()
    # El de acceso no sirve para renovar.
    acceso = tokens(cliente).json()["access"]
    assert cliente.post("/api/token/refresh/", json={"refresh": acceso}).status_code == 401
