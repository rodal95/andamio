"""El mismo recurso funciona de punta a punta: API (Django y FastAPI) <-> servicios de React y React Native.

Levanta la API generada (una vez con Django y otra con FastAPI) y ejecuta contra ella
los servicios generados (empaquetados con Vite y ejecutados con Node).
Necesita las dependencias de la API y Node: --lento.
"""

import shutil

import pytest

from andamio.cli import main

from .apis import BACKENDS, api_en_marcha
from .node import NPX, ejecutar, npm_install, requiere_node

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


@pytest.fixture(params=BACKENDS)
def api(request, en_carpeta, monkeypatch):
    recursos = [["producto", *CAMPOS], ["cliente", "nombre", "email:email"]]
    with api_en_marcha(request.param, en_carpeta, monkeypatch, recursos) as url:
        yield url


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
@requiere_node
def test_servicios_de_react_y_react_native_contra_la_api(api, en_carpeta, monkeypatch):
    monkeypatch.chdir(en_carpeta)
    proyectos = {
        "web": ["react", "web"],
        "movil": ["react-native", "movil"],
        "web-js": ["react", "web-js", "--js"],
        "movil-js": ["react-native", "movil-js", "--js"],
    }
    for carpeta, argumentos in proyectos.items():
        monkeypatch.chdir(en_carpeta)
        assert main(["crear", *argumentos]) == 0
        monkeypatch.chdir(en_carpeta / carpeta)
        assert main(["nuevo", "servicio", "producto", *CAMPOS]) == 0
        assert main(["nuevo", "servicio", "cliente", "nombre", "email:email"]) == 0
    web = en_carpeta / "web"
    npm_install(web)
    # Los demás servicios se empaquetan con el Vite del proyecto web
    # (así no hace falta instalar Expo ni los otros proyectos para esta prueba).
    shutil.copytree(en_carpeta / "movil" / "services", web / "scripts" / "rn")
    shutil.copytree(en_carpeta / "web-js" / "src" / "services", web / "scripts" / "web-js")
    shutil.copytree(en_carpeta / "movil-js" / "services", web / "scripts" / "rn-js")
    _ejecutar_script(web, "../src/services", api, "react")
    _ejecutar_script(web, "./rn", api, "react-native")
    _ejecutar_script(web, "./web-js", api, "react-js")
    _ejecutar_script(web, "./rn-js", api, "react-native-js")
