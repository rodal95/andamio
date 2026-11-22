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
    assert main(["nuevo", "pagina", "ContactoPage"]) == 0
    assert main(["nuevo", "hook", "useContador"]) == 0
    assert main(["nuevo", "servicio", "producto", "nombre:str", "precio:decimal", "stock:int", "activo:bool", "vence:date"]) == 0
    assert main(["nuevo", "servicio", "cliente", "nombre", "email:email"]) == 0
    assert main(["nuevo", "crud", "producto", "nombre:str", "precio:decimal", "stock:int", "activo:bool", "vence:date"]) == 0
    assert main(["nuevo", "pagina", "ClienteLista", "--datos", "cliente"]) == 0
    assert main(["nuevo", "pagina", "ProductoFicha", "--datos", "producto", "--uno"]) == 0
    assert main(["nuevo", "pagina", "ProductoEditar", "--datos", "producto", "--form"]) == 0
    # Relaciones: un pedido es de un cliente (clienteService ya existe).
    assert main(["nuevo", "crud", "pedido", "numero:int", "cliente:fk"]) == 0
    assert main(["nuevo", "pagina", "PedidoAlta", "--datos", "pedido", "--form"]) == 0
    assert main(["nuevo", "pagina", "PedidoFicha", "--datos", "pedido", "--uno"]) == 0
    # Login, rutas protegidas y un formulario que solo envía (servicio --solo crear).
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    assert main(["nuevo", "crud", "factura", "numero:int", "--protegido"]) == 0
    assert main(["nuevo", "servicio", "mensaje", "texto:text", "--solo", "crear"]) == 0
    assert main(["nuevo", "pagina", "Mensaje", "--datos", "mensaje", "--form", "--protegido"]) == 0
    return proyecto


def test_relacion_en_el_servicio_y_el_crud(con_piezas):
    servicio = leer(con_piezas / "src/services/pedidoService.ts")
    assert "  cliente: number | null;" in servicio
    assert "  cliente_texto?: string | null;" in servicio
    formulario = leer(con_piezas / "src/pages/pedidos/PedidoFormPage.tsx")
    for esperado in (
        "import { clienteService } from '../../services/clienteService';",
        "const { datos: clientes } = useConsulta(clienteService.listar);",
        "<select value={datos.cliente ?? ''}",
        "{opcion.nombre}",
        "  cliente: null,",
    ):
        assert esperado in formulario, esperado
    assert "{pedido.cliente_texto ?? pedido.cliente}" in leer(con_piezas / "src/components/PedidoDetalle/PedidoDetalle.tsx")
    alta = leer(con_piezas / "src/pages/PedidoAltaPage/PedidoAltaPage.tsx")
    assert "useConsulta(clienteService.listar)" in alta and "<select" in alta
    assert "{datos.cliente_texto ?? datos.cliente}" in leer(con_piezas / "src/pages/PedidoFichaPage/PedidoFichaPage.tsx")


def test_relacion_necesita_el_otro_servicio(proyecto, capsys):
    assert main(["nuevo", "servicio", "pedido", "numero:int", "cliente:fk"]) == 0  # el servicio solo guarda el id
    capsys.readouterr()
    assert main(["nuevo", "crud", "venta", "total:decimal", "cliente:fk"]) == 1
    assert "nuevo servicio cliente" in capsys.readouterr().err
    assert main(["nuevo", "pagina", "PedidoAlta", "--datos", "pedido", "--form"]) == 1


def test_estructura_del_proyecto(proyecto):
    for archivo in [
        "package.json", "vite.config.ts", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", "index.html",
        "src/main.tsx", "src/App.tsx", "src/components/index.ts", ".env", ".env.example", ".gitignore",
        "src/pages/InicioPage/InicioPage.tsx",
    ]:  # fmt: skip
        assert (proyecto / archivo).is_file(), archivo
    for carpeta in ["src/components", "src/hooks", "src/pages", "src/services"]:
        assert (proyecto / carpeta).is_dir()
    paquete = json.loads(leer(proyecto / "package.json"))
    assert paquete["name"] == "mi-web"
    versiones = {**paquete["dependencies"], **paquete["devDependencies"]}
    assert all(v[0].isdigit() for v in versiones.values()), "las versiones tienen que ser fijas"
    assert {"react", "react-dom", "react-router", "vite", "typescript", "@vitejs/plugin-react"} <= set(versiones)
    app = leer(proyecto / "src/App.tsx")
    for marcador in ("andamio:imports", "andamio:rutas", "andamio:enlaces"):
        assert marcador in app
    assert "Mi web" in leer(proyecto / "src/pages/InicioPage/InicioPage.tsx")
    assert "VITE_API_URL=http://localhost:8000/api" in leer(proyecto / ".env")
    assert not (proyecto / "node_modules").exists(), "andamio no ejecuta npm install"


def test_componente(con_piezas):
    carpeta = con_piezas / "src/components/TarjetaProducto"
    assert "export function TarjetaProducto(" in leer(carpeta / "TarjetaProducto.tsx")
    assert "styles.root" in leer(carpeta / "TarjetaProducto.tsx")
    assert ".root {" in leer(carpeta / "TarjetaProducto.module.css")
    assert "export { TarjetaProducto } from './TarjetaProducto';" in leer(carpeta / "index.ts")
    assert "export { TarjetaProducto } from './TarjetaProducto';\n" in leer(con_piezas / "src/components/index.ts")


def test_hook_y_pagina_no_duplican_prefijos(con_piezas):
    assert (con_piezas / "src/hooks/useContador.ts").is_file()
    assert "export function useContador<T>" in leer(con_piezas / "src/hooks/useContador.ts")
    assert (con_piezas / "src/pages/ContactoPage/ContactoPage.tsx").is_file()
    assert not (con_piezas / "src/pages/ContactoPagePage").exists()


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


def test_pagina_registra_su_ruta_y_su_enlace(con_piezas):
    app = leer(con_piezas / "src/App.tsx")
    assert "import { ContactoPage } from './pages/ContactoPage';" in app
    assert '<Route path="/contacto" element={<ContactoPage />} />' in app
    assert '<Link to="/contacto">Contacto</Link>' in app


def test_servicio_trae_el_hook_de_consulta(proyecto):
    assert not (proyecto / "src/hooks/useConsulta.ts").exists()
    assert main(["nuevo", "servicio", "producto", "nombre"]) == 0
    assert "export function useConsulta<T>" in leer(proyecto / "src/hooks/useConsulta.ts")


def test_pagina_sin_datos_no_usa_la_api(proyecto):
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    pagina = leer(proyecto / "src/pages/ContactoPage/ContactoPage.tsx")
    assert pagina.startswith("import styles from './ContactoPage.module.css';")
    assert "useConsulta" not in pagina and "@@" not in pagina
    assert "export function ContactoPage() {\n  return (" in pagina
    assert not (proyecto / "src/hooks/useConsulta.ts").exists(), "sin --datos no hace falta el hook"


def test_pagina_con_datos_lista(con_piezas):
    pagina = leer(con_piezas / "src/pages/ClienteListaPage/ClienteListaPage.tsx")
    for esperado in (
        "import { useConsulta } from '../../hooks/useConsulta';",
        "import { clienteService } from '../../services/clienteService';",
        "const { datos, cargando, error } = useConsulta(clienteService.listar);",
        "{cargando && <p>Cargando…</p>}",
        "{datos?.length === 0 && <p>Todavía no hay registros.</p>}",
        "<li key={item.id}>{item.nombre}</li>",  # el primer campo de texto del servicio
        "// useConsulta pide los datos a la API",
    ):
        assert esperado in pagina, esperado
    app = leer(con_piezas / "src/App.tsx")
    assert '<Route path="/cliente-lista" element={<ClienteListaPage />} />' in app
    assert '<Link to="/cliente-lista">Cliente lista</Link>' in app


def test_pagina_con_datos_de_uno(con_piezas):
    pagina = leer(con_piezas / "src/pages/ProductoFichaPage/ProductoFichaPage.tsx")
    for esperado in (
        "import { useParams } from 'react-router';",
        "const id = Number(useParams().id);",
        "useConsulta(() => productoService.obtener(id), [id]);",
        "<dt>Precio</dt>",
        "<dd>{datos.activo ? 'Sí' : 'No'}</dd>",
    ):
        assert esperado in pagina, esperado
    app = leer(con_piezas / "src/App.tsx")
    assert '<Route path="/producto-ficha/:id" element={<ProductoFichaPage />} />' in app
    assert '"/producto-ficha"' not in app, "una página con :id no va en el menú"


def test_pagina_con_formulario(con_piezas):
    pagina = leer(con_piezas / "src/pages/ProductoEditarPage/ProductoEditarPage.tsx")
    for esperado in (
        "import { useFormulario } from '../../hooks/useFormulario';",
        "import { productoService, type Producto, type ProductoDatos } from '../../services/productoService';",
        "const VACIO: ProductoDatos = {",
        "  vence: '',",
        "    activo: registro.activo,",
        "const { datos, cambiar, errores, guardar, editando, cargado } = useFormulario(",
        "// TODO(logica): validaciones del formulario",
        "<input type=\"date\" required value={datos.vence}",
        "{editando ? 'Guardar cambios' : 'Agregar'}",
    ):
        assert esperado in pagina, esperado
    assert ".formulario {" in leer(con_piezas / "src/pages/ProductoEditarPage/ProductoEditarPage.module.css")
    assert ".formulario" not in leer(con_piezas / "src/pages/ContactoPage/ContactoPage.module.css")
    app = leer(con_piezas / "src/App.tsx")
    assert '<Route path="/producto-editar" element={<ProductoEditarPage />} />' in app
    assert '<Route path="/producto-editar/:id" element={<ProductoEditarPage />} />' in app
    assert '<Link to="/producto-editar">' in app


def test_cada_pagina_crea_solo_el_hook_que_usa(proyecto):
    (proyecto / "src/services").mkdir(exist_ok=True)
    assert main(["nuevo", "servicio", "producto", "nombre"]) == 0
    for hook in ("useConsulta", "useFormulario"):
        (proyecto / f"src/hooks/{hook}.ts").unlink()
    assert main(["nuevo", "pagina", "Alta", "--datos", "producto", "--form"]) == 0
    assert (proyecto / "src/hooks/useFormulario.ts").is_file() and not (proyecto / "src/hooks/useConsulta.ts").exists()
    assert main(["nuevo", "pagina", "Lista", "--datos", "producto"]) == 0
    assert (proyecto / "src/hooks/useConsulta.ts").is_file()


def test_pagina_con_datos_sin_guia_y_sin_historial(proyecto):
    assert main(["nuevo", "servicio", "producto", "nombre"]) == 0
    (proyecto / ".andamio/historial.jsonl").unlink()  # un servicio sin historial: no se saben los campos
    assert main(["nuevo", "pagina", "Productos", "--datos", "producto", "--sin-guia"]) == 0
    assert main(["nuevo", "pagina", "Producto", "--datos", "producto", "--uno"]) == 0
    lista = leer(proyecto / "src/pages/ProductosPage/ProductosPage.tsx")
    assert "<li key={item.id}>{`Producto ${item.id}`}</li>" in lista
    assert "//" not in lista
    assert "{datos && <pre>{JSON.stringify(datos, null, 2)}</pre>}" in leer(proyecto / "src/pages/ProductoPage/ProductoPage.tsx")


def test_pagina_con_datos_reusa_el_hook(proyecto, capsys):
    assert main(["nuevo", "servicio", "producto", "nombre"]) == 0
    hook = proyecto / "src/hooks/useConsulta.ts"
    hook.write_text(leer(hook) + "// mío\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "pagina", "Productos", "--datos", "producto"]) == 0
    assert leer(hook).endswith("// mío\n")
    assert "src/hooks/useConsulta.ts" in capsys.readouterr().out  # en el orden de lectura


@pytest.mark.parametrize(
    "argumentos, mensaje",
    [
        (["pagina", "Productos", "--datos", "producto"], "src/services/productoService.ts, que todavía no existe"),
        (["pagina", "Productos", "--datos", "productos"], "parece plural"),
        (["pagina", "Contacto", "--uno"], "--uno va junto con --datos"),
        (["pagina", "Contacto", "--form"], "--form va junto con --datos"),
        (["componente", "Tarjeta", "--datos", "producto"], "no acepta la opción --datos"),
    ],
)
def test_pagina_con_datos_errores(proyecto, capsys, argumentos, mensaje):
    capsys.readouterr()
    assert main(["nuevo", *argumentos]) == 1
    assert mensaje in capsys.readouterr().err
    assert not list((proyecto / "src/pages").glob("Productos*")) and not (proyecto / "src/pages/ContactoPage").exists()


def test_pagina_y_crud_no_repiten_componentes(proyecto, capsys):
    """El crud ya tiene ProductoListaPage: una página ProductoLista no compilaría (y al revés)."""
    assert main(["nuevo", "crud", "producto", "nombre"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "pagina", "ProductoLista", "--datos", "producto"]) == 1
    assert "ya usa un componente ProductoListaPage" in capsys.readouterr().err
    assert main(["nuevo", "pagina", "ProductoDetalle"]) == 1
    assert main(["nuevo", "pagina", "Catalogo", "--datos", "producto"]) == 0
    assert main(["nuevo", "pagina", "ClienteForm"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "crud", "cliente", "nombre"]) == 1
    assert "ya usa un componente ClienteFormPage" in capsys.readouterr().err


def test_mapa_revisa_las_paginas_con_datos(con_piezas, capsys):
    capsys.readouterr()
    assert main(["mapa"]) == 0
    salida = capsys.readouterr().out
    assert "no se pudo revisar" not in salida
    assert "pagina producto_ficha --datos producto --uno" in salida


def test_crud(con_piezas):
    raiz = con_piezas
    for archivo in [
        "src/pages/productos/ProductoListaPage.tsx", "src/pages/productos/ProductoDetallePage.tsx",
        "src/pages/productos/ProductoFormPage.tsx", "src/pages/productos/productos.module.css",
        "src/pages/productos/index.ts", "src/components/ProductoDetalle/ProductoDetalle.tsx",
        "src/hooks/useConsulta.ts",
    ]:  # fmt: skip
        assert (raiz / archivo).is_file(), archivo
    app = leer(raiz / "src/App.tsx")
    assert "import { ProductoDetallePage, ProductoFormPage, ProductoListaPage } from './pages/productos';" in app
    for ruta in ('"/productos"', '"/productos/nuevo"', '"/productos/:id"', '"/productos/:id/editar"'):
        assert f"<Route path={ruta}" in app
    assert '<Link to="/productos">Productos</Link>' in app
    assert "export { ProductoDetalle } from './ProductoDetalle';" in leer(raiz / "src/components/index.ts")
    formulario = leer(raiz / "src/pages/productos/ProductoFormPage.tsx")
    assert "<input type=\"checkbox\" checked={datos.activo}" in formulario
    assert "<input type=\"date\" required value={datos.vence}" in formulario
    assert 'step="0.01"' in formulario
    assert "useFormulario(" in formulario and "productoService," in formulario
    assert "e.estado === 400" in leer(raiz / "src/hooks/useFormulario.ts")
    detalle = leer(raiz / "src/components/ProductoDetalle/ProductoDetalle.tsx")
    assert "<dd>{producto.activo ? 'Sí' : 'No'}</dd>" in detalle
    assert "productoService." not in detalle, "el componente no tiene que llamar a la API (solo usa el tipo)"
    assert "{item.nombre}" in leer(raiz / "src/pages/productos/ProductoListaPage.tsx")


def test_crud_reusa_el_servicio_que_ya_existe(proyecto, capsys):
    main(["nuevo", "servicio", "producto", "nombre"])
    servicio = proyecto / "src/services/productoService.ts"
    servicio.write_text(leer(servicio) + "// mío\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "crud", "producto", "nombre"]) == 0
    assert leer(servicio).endswith("// mío\n")
    assert "Ya existen y no se tocan" in capsys.readouterr().out


def test_ruta_repetida(proyecto, capsys):
    assert main(["nuevo", "pagina", "Productos"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "crud", "producto", "nombre"]) == 1
    assert "Ya hay una página en la ruta /productos" in capsys.readouterr().err
    assert not (proyecto / "src/pages/productos").exists()


def test_proyecto_sin_router(proyecto, capsys):
    """Un proyecto creado antes del router (o con npm create vite): genera igual y explica."""
    import json

    paquete = json.loads(leer(proyecto / "package.json"))
    del paquete["dependencies"]["react-router"]
    (proyecto / "package.json").write_text(json.dumps(paquete), encoding="utf-8")
    (proyecto / "src/App.tsx").write_text("function App() {\n  return <h1>Hola</h1>;\n}\nexport default App;\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "crud", "producto", "nombre"]) == 0
    salida = capsys.readouterr().out
    assert (proyecto / "src/pages/productos/ProductoListaPage.tsx").is_file()
    assert "npm install react-router@7.18.6" in salida
    assert "dentro de <Routes>" in salida
    assert '<Route path="/productos" element={<ProductoListaPage />} />' in salida


USO_DE_LAS_PIEZAS = """\
import { useEffect, useState } from 'react';
import { TarjetaProducto } from '../components';
import { useContador } from '../hooks/useContador';
import { clienteService } from '../services/clienteService';
import { productoService, type Producto } from '../services/productoService';

export function PruebaUso() {
  const { valor, setValor, reiniciar } = useContador(0);
  const [productos, setProductos] = useState<Producto[]>([]);

  useEffect(() => {
    productoService.listar().then(setProductos).catch(() => setProductos([]));
    void clienteService.crear({ nombre: 'Ana', email: 'ana@ejemplo.com' });
    void productoService.actualizar(1, { precio: 10.5 });
  }, []);

  return (
    <TarjetaProducto>
      <button onClick={() => setValor(valor + 1)}>{valor}</button>
      <button onClick={reiniciar}>0</button>
      {productos.map((p) => (
        <p key={p.id}>{p.nombre} {p.precio.toFixed(2)}</p>
      ))}
    </TarjetaProducto>
  );
}
"""


@pytest.mark.lento
@requiere_node
def test_npm_install_y_build(con_piezas):
    # App queda como lo generó andamio (router, página y CRUD); además se usa cada pieza.
    (con_piezas / "src/pages/PruebaUso.tsx").write_text(USO_DE_LAS_PIEZAS, encoding="utf-8")
    npm_install(con_piezas)
    ejecutar([NPM, "run", "build"], con_piezas)
    assert (con_piezas / "dist/index.html").is_file()


def test_formulario_necesita_los_campos(proyecto, capsys):
    assert main(["nuevo", "servicio", "producto", "nombre"]) == 0
    assert main(["nuevo", "pagina", "Alta", "--datos", "producto", "--uno", "--form"]) == 1
    assert "no los dos" in capsys.readouterr().err
    (proyecto / ".andamio/historial.jsonl").unlink()
    assert main(["nuevo", "pagina", "Alta", "--datos", "producto", "--form"]) == 1
    assert "hacen falta los campos de productoService" in capsys.readouterr().err
