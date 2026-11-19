"""El mismo recurso funciona de punta a punta: Django <-> servicios de React y React Native.

Levanta la API generada en Django y ejecuta contra ella los servicios generados
(empaquetados con Vite y ejecutados con Node). Necesita Django y Node: --lento.
"""

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

from andamio.cli import main

from .node import NPX, ejecutar, npm_install, requiere_node
from .test_django import requiere_django

CAMPOS = ["nombre:str", "descripcion:text", "precio:decimal", "stock:int", "peso:float", "activo:bool", "vence:date", "publicado:datetime", "contacto:email"]

SCRIPT = """\
import { ErrorApi } from '@@BASE@@/http';
import { clienteService } from '@@BASE@@/clienteService';
import { productoService } from '@@BASE@@/productoService';

function verificar(condicion: boolean, mensaje: string) {
  if (!condicion) throw new Error(`FALLÓ: ${mensaje}`);
  console.log(`ok - ${mensaje}`);
}

const nuevo = await productoService.crear({
  nombre: 'Yerba', descripcion: '1 kg', precio: 1500.5, stock: 10, peso: 1, activo: true,
  vence: '2026-12-01', publicado: '2026-11-19T10:00:00Z', contacto: 'ventas@ejemplo.com',
});
verificar(typeof nuevo.id === 'number', 'crear devuelve el id');
verificar(nuevo.precio === 1500.5, 'el decimal llega como número');
const lista = await productoService.listar();
verificar(Array.isArray(lista) && lista.length === 1, 'listar devuelve un array');
verificar((await productoService.obtener(nuevo.id)).nombre === 'Yerba', 'obtener');
const modificado = await productoService.actualizar(nuevo.id, { stock: 7 });
verificar(modificado.stock === 7 && modificado.nombre === 'Yerba', 'actualizar (PATCH)');
await productoService.eliminar(nuevo.id);
verificar((await productoService.listar()).length === 0, 'eliminar');
try {
  await clienteService.crear({ nombre: '', email: 'no-es-mail' });
  verificar(false, 'la validación tendría que fallar');
} catch (error) {
  verificar(error instanceof ErrorApi && error.estado === 400, 'error de validación -> ErrorApi 400');
}
"""


def _puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def api_django(en_carpeta, monkeypatch):
    main(["crear", "django", "api"])
    raiz = en_carpeta / "api"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "recurso", "producto", *CAMPOS, "--migrar"]) == 0
    assert main(["nuevo", "recurso", "cliente", "nombre", "email:email", "--migrar"]) == 0
    puerto = _puerto_libre()
    servidor = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{puerto}", "--noreload"],
        cwd=raiz,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{puerto}/api"
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(f"{url}/clientes/", timeout=2)
                break
            except OSError:
                time.sleep(0.5)
        else:
            pytest.fail("El servidor de Django no arrancó")
        yield url
    finally:
        servidor.terminate()
        servidor.wait(timeout=30)


def _ejecutar_script(proyecto_web, base, url, nombre):
    script = proyecto_web / "scripts" / f"{nombre}.ts"
    script.parent.mkdir(exist_ok=True)
    script.write_text(SCRIPT.replace("@@BASE@@", base), encoding="utf-8")
    salida = proyecto_web / "scripts" / f"salida-{nombre}"
    entorno = {"VITE_API_URL": url, "EXPO_PUBLIC_API_URL": url, "NO_PROXY": "127.0.0.1,localhost"}
    ejecutar([NPX, "vite", "build", "--ssr", str(script), "--outDir", str(salida), "--logLevel", "error"], proyecto_web, env=entorno)
    resultado = ejecutar(["node", str(salida / f"{nombre}.js")], proyecto_web, env=entorno)
    assert resultado.stdout.count("ok - ") == 7, resultado.stdout


@pytest.mark.lento
@pytest.mark.django
@requiere_django
@requiere_node
def test_servicios_de_react_y_react_native_contra_django(api_django, en_carpeta, monkeypatch):
    monkeypatch.chdir(en_carpeta)
    main(["crear", "react", "web"])
    main(["crear", "react-native", "movil"])
    for carpeta in ("web", "movil"):
        monkeypatch.chdir(en_carpeta / carpeta)
        assert main(["nuevo", "servicio", "producto", *CAMPOS]) == 0
        assert main(["nuevo", "servicio", "cliente", "nombre", "email:email"]) == 0
    web = en_carpeta / "web"
    npm_install(web)
    # Los servicios de React Native se empaquetan con el Vite del proyecto web
    # (así no hace falta instalar Expo para esta prueba).
    shutil.copytree(en_carpeta / "movil" / "services", web / "scripts" / "rn")
    _ejecutar_script(web, "../src/services", api_django, "react")
    _ejecutar_script(web, "./rn", api_django, "react-native")
