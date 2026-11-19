"""Stack react: crear el proyecto y generar todas las piezas."""

import json

import pytest

from andamio.cli import main

from .node import NPM, ejecutar, npm_install, requiere_node


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "react", "Mi Web"]) == 0
    raiz = en_carpeta / "mi-web"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_piezas(proyecto):
    assert main(["nuevo", "componente", "tarjeta producto"]) == 0
    assert main(["nuevo", "pagina", "ProductosPage"]) == 0
    assert main(["nuevo", "hook", "useContador"]) == 0
    assert main(["nuevo", "servicio", "producto", "nombre:str", "precio:decimal", "stock:int", "activo:bool", "vence:date"]) == 0
    assert main(["nuevo", "servicio", "cliente", "nombre", "email:email"]) == 0
    return proyecto


def test_estructura_del_proyecto(proyecto):
    for archivo in [
        "package.json", "vite.config.ts", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", "index.html",
        "src/main.tsx", "src/App.tsx", "src/components/index.ts", ".env", ".env.example", ".gitignore",
    ]:  # fmt: skip
        assert (proyecto / archivo).is_file(), archivo
    for carpeta in ["src/components", "src/hooks", "src/pages", "src/services"]:
        assert (proyecto / carpeta).is_dir()
    paquete = json.loads(leer(proyecto / "package.json"))
    assert paquete["name"] == "mi-web"
    versiones = {**paquete["dependencies"], **paquete["devDependencies"]}
    assert all(v[0].isdigit() for v in versiones.values()), "las versiones tienen que ser fijas"
    assert {"react", "react-dom", "vite", "typescript", "@vitejs/plugin-react"} <= set(versiones)
    assert "VITE_API_URL=http://localhost:8000/api" in leer(proyecto / ".env")
    assert not (proyecto / "node_modules").exists(), "andamio no ejecuta npm install"


def test_componente(con_piezas):
    carpeta = con_piezas / "src/components/TarjetaProducto"
    assert "export function TarjetaProducto(" in leer(carpeta / "TarjetaProducto.tsx")
    assert "styles.root" in leer(carpeta / "TarjetaProducto.tsx")
    assert ".root {" in leer(carpeta / "TarjetaProducto.module.css")
    assert "export { TarjetaProducto } from './TarjetaProducto';" in leer(carpeta / "index.ts")
    assert leer(con_piezas / "src/components/index.ts").endswith("export { TarjetaProducto } from './TarjetaProducto';\n")


def test_hook_y_pagina_no_duplican_prefijos(con_piezas):
    assert (con_piezas / "src/hooks/useContador.ts").is_file()
    assert "export function useContador<T>" in leer(con_piezas / "src/hooks/useContador.ts")
    assert (con_piezas / "src/pages/ProductosPage/ProductosPage.tsx").is_file()
    assert not (con_piezas / "src/pages/ProductosPagePage").exists()


def test_el_hook_se_llama_igual_con_o_sin_use(proyecto, capsys):
    assert main(["nuevo", "hook", "contador"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "hook", "use-contador"]) == 1
    assert "useContador.ts" in capsys.readouterr().err


def test_servicio(con_piezas):
    servicio = leer(con_piezas / "src/services/productoService.ts")
    for esperado in [
        "export interface Producto {",
        "  id: number;",
        "  nombre: string;",
        "  precio: number;",
        "  activo: boolean;",
        "  vence: string;",
        "const RUTA = '/productos/';",
        "http.get<Producto[]>(RUTA)",
        "http.patch<Producto>(`${RUTA}${id}/`, datos)",
    ]:
        assert esperado in servicio
    http = leer(con_piezas / "src/services/http.ts")
    assert "import.meta.env.VITE_API_URL" in http
    assert "'http://localhost:8000/api'" in http


def test_http_se_crea_una_sola_vez(proyecto, capsys):
    main(["nuevo", "servicio", "producto", "nombre"])
    (proyecto / "src/services/http.ts").write_text("// mío\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "servicio", "cliente", "nombre"]) == 0
    assert "Ya existen y no se tocan" in capsys.readouterr().out
    assert leer(proyecto / "src/services/http.ts") == "// mío\n"


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        (["componente", "App"], "ya lo usa React"),
        (["hook", "state"], "ya existe en React"),
        (["servicio", "producto", "precio:money"], "Tipos válidos"),
        (["servicio", "productos", "nombre"], "parece estar en plural"),
        (["pantalla", "inicio"], "no es una pieza"),
        (["componente", "Boton", "--carpeta", "x"], "no acepta la opción --carpeta"),
    ],
)
def test_errores_esperables(proyecto, capsys, argumentos, esperado):
    assert main(["nuevo", *argumentos]) == 1
    assert esperado in capsys.readouterr().err


def test_detecta_react_desde_src(proyecto, monkeypatch, capsys):
    monkeypatch.chdir(proyecto / "src")
    capsys.readouterr()
    assert main(["info"]) == 0
    salida = capsys.readouterr().out
    assert "Proyecto React + Vite" in salida
    for pieza in ("componente", "pagina", "hook", "servicio"):
        assert pieza in salida


def test_menu_interactivo(proyecto, respuestas, capsys):
    respuestas(["1", "Boton Grande", "s"])
    capsys.readouterr()
    assert main([]) == 0
    assert "import { BotonGrande } from './components';" in capsys.readouterr().out
    assert (proyecto / "src/components/BotonGrande/BotonGrande.tsx").is_file()


APP_QUE_USA_TODO = """\
import { useEffect, useState } from 'react';
import { TarjetaProducto } from './components';
import { useContador } from './hooks/useContador';
import { ProductosPage } from './pages/ProductosPage';
import { clienteService } from './services/clienteService';
import { productoService, type Producto } from './services/productoService';

function App() {
  const { valor, setValor, reiniciar } = useContador(0);
  const [productos, setProductos] = useState<Producto[]>([]);

  useEffect(() => {
    productoService.listar().then(setProductos).catch(() => setProductos([]));
    void clienteService.crear({ nombre: 'Ana', email: 'ana@ejemplo.com' });
    void productoService.actualizar(1, { precio: 10.5 });
  }, []);

  return (
    <>
      <ProductosPage />
      <TarjetaProducto>
        <button onClick={() => setValor(valor + 1)}>{valor}</button>
        <button onClick={reiniciar}>0</button>
        <ul>
          {productos.map((p) => (
            <li key={p.id}>
              {p.nombre} {p.precio.toFixed(2)}
            </li>
          ))}
        </ul>
      </TarjetaProducto>
    </>
  );
}

export default App;
"""


@pytest.mark.lento
@requiere_node
def test_npm_install_y_build(con_piezas):
    (con_piezas / "src/App.tsx").write_text(APP_QUE_USA_TODO, encoding="utf-8")
    npm_install(con_piezas)
    ejecutar([NPM, "run", "build"], con_piezas)
    assert (con_piezas / "dist/index.html").is_file()
