"""Variantes JavaScript de React y React Native, y detección de la variante."""

import json

import pytest

from andamio.cli import main

from .node import NPX, NPM, ejecutar, npm_install, requiere_node


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def web_js(en_carpeta, monkeypatch):
    assert main(["crear", "react", "mi-web", "--js"]) == 0
    raiz = en_carpeta / "mi-web"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def movil_js(en_carpeta, monkeypatch):
    assert main(["crear", "react-native", "mi-app", "--variante", "js"]) == 0
    raiz = en_carpeta / "mi-app"
    monkeypatch.chdir(raiz)
    return raiz


def test_react_js_proyecto(web_js, capsys):
    for archivo in ["vite.config.js", "src/main.jsx", "src/App.jsx", "src/components/index.js", "index.html"]:
        assert (web_js / archivo).is_file(), archivo
    assert not (web_js / "tsconfig.json").exists()
    paquete = json.loads(leer(web_js / "package.json"))
    assert "typescript" not in paquete["devDependencies"]
    assert paquete["scripts"]["build"] == "vite build"
    assert "/src/main.jsx" in leer(web_js / "index.html")
    capsys.readouterr()
    main(["info"])
    assert "Proyecto React + Vite (JavaScript)" in capsys.readouterr().out


def test_react_js_piezas(web_js, capsys):
    assert main(["nuevo", "componente", "Tarjeta"]) == 0
    assert main(["nuevo", "pagina", "Productos"]) == 0
    assert main(["nuevo", "hook", "contador"]) == 0
    assert main(["nuevo", "servicio", "producto", "nombre:str", "precio:decimal", "vence:date"]) == 0
    assert (web_js / "src/components/Tarjeta/Tarjeta.jsx").is_file()
    assert (web_js / "src/components/Tarjeta/index.js").is_file()
    assert "export { Tarjeta } from './Tarjeta';" in leer(web_js / "src/components/index.js")
    assert not (web_js / "src/components/index.ts").exists()
    assert (web_js / "src/pages/ProductosPage/ProductosPage.jsx").is_file()
    assert (web_js / "src/hooks/useContador.js").is_file()
    servicio = leer(web_js / "src/services/productoService.js")
    assert " * @typedef {Object} Producto" in servicio
    assert " * @property {number} precio número con 2 decimales" in servicio
    assert ' * @property {string} vence fecha: "2025-03-15"' in servicio
    assert "const RUTA = '/productos/';" in servicio
    assert (web_js / "src/services/http.js").is_file()
    # La pieza repetida se detecta también con la extensión de la variante.
    capsys.readouterr()
    assert main(["nuevo", "hook", "contador"]) == 1
    assert "useContador.js" in capsys.readouterr().err


def test_react_native_js(movil_js):
    assert (movil_js / "jsconfig.json").is_file()
    assert (movil_js / "app/_layout.jsx").is_file()
    assert not (movil_js / "tsconfig.json").exists()
    assert "typescript" not in json.loads(leer(movil_js / "package.json")).get("devDependencies", {})
    assert main(["nuevo", "pantalla", "detalle", "--carpeta", "productos"]) == 0
    assert main(["nuevo", "componente", "Tarjeta"]) == 0
    assert main(["nuevo", "hook", "contador"]) == 0
    assert main(["nuevo", "servicio", "producto", "nombre", "precio:decimal"]) == 0
    assert (movil_js / "app/productos/detalle.jsx").is_file()
    assert (movil_js / "components/Tarjeta.jsx").is_file()
    assert "export { Tarjeta } from './Tarjeta';" in leer(movil_js / "components/index.js")
    assert (movil_js / "hooks/useContador.js").is_file()
    assert "process.env.EXPO_PUBLIC_API_URL" in leer(movil_js / "services/http.js")
    for archivo in movil_js.rglob("*.js*"):
        assert "{{" not in leer(archivo), archivo


def test_detecta_proyecto_vite_hecho_con_npm_create_en_js(en_carpeta, monkeypatch):
    """Un proyecto creado con `npm create vite` (plantilla react, JavaScript)."""
    raiz = en_carpeta / "de-vite"
    (raiz / "src").mkdir(parents=True)
    paquete = {"dependencies": {"react": "^19.3.1", "react-dom": "^19.3.1"},
               "devDependencies": {"@types/react": "^19.3.0", "@vitejs/plugin-react": "^6.1.2", "vite": "^8.3.6"}}  # fmt: skip
    (raiz / "package.json").write_text(json.dumps(paquete), encoding="utf-8")
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "componente", "Boton"]) == 0
    assert (raiz / "src/components/Boton/Boton.jsx").is_file()
    assert (raiz / "src/components/index.js").read_text(encoding="utf-8") == "export { Boton } from './Boton';\n"


def test_detecta_typescript_por_la_dependencia(en_carpeta, monkeypatch):
    raiz = en_carpeta / "con-ts"
    raiz.mkdir()
    paquete = {"dependencies": {"react": "1"}, "devDependencies": {"vite": "1", "typescript": "1"}}
    (raiz / "package.json").write_text(json.dumps(paquete), encoding="utf-8")
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "hook", "contador"]) == 0
    assert (raiz / "src/hooks/useContador.ts").is_file()


def test_errores_de_variante(en_carpeta, capsys):
    assert main(["crear", "react", "x", "--variante", "coffee"]) == 1
    assert "Variantes: ts (TypeScript), js (JavaScript)" in capsys.readouterr().err
    assert main(["crear", "django", "x", "--js"]) == 1
    assert "no tienen variantes" in capsys.readouterr().err
    assert not (en_carpeta / "x").exists()


def test_menu_pregunta_el_lenguaje(en_carpeta, respuestas, capsys):
    preguntas = respuestas(["6", "2", "mi web", "s"])
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "¿En qué lenguaje?" in salida
    assert "TypeScript (recomendado)" in salida
    assert "Variante: JavaScript" in salida
    assert (en_carpeta / "mi-web/src/main.jsx").is_file()
    assert preguntas


APP_JS = """\
import { useEffect, useState } from 'react';
import { Tarjeta } from './components';
import { useContador } from './hooks/useContador';
import { ProductosPage } from './pages/ProductosPage';
import { productoService } from './services/productoService';

function App() {
  const { valor, setValor, reiniciar } = useContador(0);
  const [productos, setProductos] = useState([]);
  useEffect(() => {
    productoService.listar().then(setProductos).catch(() => setProductos([]));
  }, []);
  return (
    <>
      <ProductosPage />
      <Tarjeta>
        <button onClick={() => setValor(valor + 1)}>{valor}</button>
        <button onClick={reiniciar}>0</button>
        {productos.map((p) => <p key={p.id}>{p.nombre}</p>)}
      </Tarjeta>
    </>
  );
}

export default App;
"""


def test_react_js_crud(web_js):
    assert main(["nuevo", "crud", "producto", "nombre:str", "precio:decimal", "activo:bool"]) == 0
    for archivo in ["src/pages/productos/ProductoFormPage.jsx", "src/components/ProductoDetalle/ProductoDetalle.jsx", "src/hooks/useConsulta.js", "src/services/productoService.js"]:
        assert (web_js / archivo).is_file(), archivo
    assert '<Route path="/productos/:id/editar" element={<ProductoFormPage />} />' in leer(web_js / "src/App.jsx")
    assert "export { ProductoDetalle } from './ProductoDetalle';" in leer(web_js / "src/components/index.js")


def test_react_js_pagina_con_datos(web_js):
    assert main(["nuevo", "servicio", "producto", "nombre:str", "activo:bool"]) == 0
    assert (web_js / "src/hooks/useConsulta.js").is_file()
    assert main(["nuevo", "pagina", "ProductoLista", "--datos", "producto"]) == 0
    assert main(["nuevo", "pagina", "ProductoDetalle", "--datos", "producto", "--uno"]) == 0
    lista = leer(web_js / "src/pages/ProductoListaPage/ProductoListaPage.jsx")
    assert "useConsulta(productoService.listar)" in lista
    assert "import { productoService } from '../../services/productoService';" in lista
    detalle = leer(web_js / "src/pages/ProductoDetallePage/ProductoDetallePage.jsx")
    assert "<dd>{datos.activo ? 'Sí' : 'No'}</dd>" in detalle
    assert '<Route path="/producto-detalle/:id" element={<ProductoDetallePage />} />' in leer(web_js / "src/App.jsx")


@pytest.mark.lento
@requiere_node
def test_react_js_npm_install_y_build(web_js):
    for argumentos in (
        ["componente", "Tarjeta"], ["pagina", "Contacto"], ["hook", "contador"], ["servicio", "producto", "nombre"], ["crud", "producto", "nombre"],
        ["pagina", "Catalogo", "--datos", "producto"], ["pagina", "ProductoFicha", "--datos", "producto", "--uno"],
    ):  # fmt: skip
        assert main(["nuevo", *argumentos]) == 0
    (web_js / "src/pages/PruebaUso.jsx").write_text(APP_JS.replace("function App()", "export function PruebaUso()").replace("export default App;\n", "").replace("./", "../").replace("import { ProductosPage } from '../pages/ProductosPage';\n", "").replace("      <ProductosPage />\n", ""), encoding="utf-8")
    npm_install(web_js)
    ejecutar([NPM, "run", "build"], web_js)
    assert (web_js / "dist/index.html").is_file()


PANTALLA_JS = """\
import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';

import { Tarjeta } from '@/components';
import { useContador } from '@/hooks/useContador';
import { productoService } from '@/services/productoService';

export default function PruebaUso() {
  const { valor, setValor } = useContador(0);
  const [productos, setProductos] = useState([]);
  useEffect(() => {
    productoService.listar().then(setProductos).catch(() => setValor(-1));
  }, [setValor]);
  return (
    <View>
      <Tarjeta>
        <Text>{valor}</Text>
        {productos.map((p) => <Text key={p.id}>{p.nombre}</Text>)}
      </Tarjeta>
    </View>
  );
}
"""


@pytest.mark.lento
@requiere_node
def test_react_native_js_npm_install_y_export(movil_js):
    for argumentos in (["pantalla", "detalle", "--carpeta", "productos"], ["componente", "Tarjeta"], ["hook", "contador"], ["servicio", "producto", "nombre"]):
        assert main(["nuevo", *argumentos]) == 0
    (movil_js / "app/prueba-uso.jsx").write_text(PANTALLA_JS, encoding="utf-8")
    npm_install(movil_js)
    ejecutar([NPX, "expo", "install", "--check"], movil_js, env={"EXPO_OFFLINE": "1"})
    # Exportar para web compila todas las pantallas y resuelve el alias @/ de jsconfig.json.
    ejecutar([NPX, "expo", "export", "--platform", "web", "--output-dir", "dist-web"], movil_js, env={"EXPO_OFFLINE": "1"})
    assert (movil_js / "dist-web/index.html").is_file()
