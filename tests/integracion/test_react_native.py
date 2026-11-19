"""Stack react-native: crear el proyecto y generar todas las piezas."""

import json

import pytest

from andamio.cli import main
from andamio.nucleo.plantillas import carpeta_incorporada

from .node import NPX, ejecutar, npm_install, requiere_node


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "react-native", "Mi App"]) == 0
    raiz = en_carpeta / "mi-app"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_piezas(proyecto):
    assert main(["nuevo", "pantalla", "Detalle Producto", "--carpeta", "Productos"]) == 0
    assert main(["nuevo", "pantalla", "inicio", "--carpeta", "(Tabs)"]) == 0
    assert main(["nuevo", "componente", "Tarjeta"]) == 0
    assert main(["nuevo", "hook", "contador"]) == 0
    assert main(["nuevo", "servicio", "producto", "nombre:str", "precio:decimal", "stock:int"]) == 0
    assert main(["nuevo", "servicio", "cliente", "nombre", "email:email"]) == 0
    return proyecto


def test_estructura_del_proyecto(proyecto):
    for archivo in [
        "package.json", "app.json", "tsconfig.json", "expo-env.d.ts", "app/_layout.tsx", "app/index.tsx",
        "constants/app.ts", "components/index.ts", "assets/icon.png", ".env", ".env.example", ".gitignore",
    ]:  # fmt: skip
        assert (proyecto / archivo).is_file(), archivo
    paquete = json.loads(leer(proyecto / "package.json"))
    assert paquete["main"] == "expo-router/entry"
    dependencias = paquete["dependencies"]
    assert dependencias["expo"].startswith("~58.")
    assert dependencias["expo-router"].startswith("~58.")
    configuracion = json.loads(leer(proyecto / "app.json"))["expo"]
    assert configuracion["scheme"] == "mi-app"
    assert "expo-router" in configuracion["plugins"]
    assert json.loads(leer(proyecto / "tsconfig.json"))["compilerOptions"]["paths"] == {"@/*": ["./*"]}
    assert "EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api" in leer(proyecto / ".env")
    # El ícono (binario) se copia sin modificar.
    original = (carpeta_incorporada("react-native") / "_proyecto" / "assets" / "icon.png").read_bytes()
    assert (proyecto / "assets/icon.png").read_bytes() == original


def test_jsx_sin_dobles_llaves(con_piezas):
    for archivo in list(con_piezas.rglob("*.tsx")) + list(con_piezas.rglob("*.ts")):
        assert "{{" not in leer(archivo), archivo


def test_pantallas(con_piezas):
    detalle = leer(con_piezas / "app/productos/detalle-producto.tsx")
    assert "export default function DetalleProductoPantalla()" in detalle
    assert "<Stack.Screen options={opciones} />" in detalle
    assert "const opciones = { title: 'Detalle producto' };" in detalle
    assert (con_piezas / "app/(tabs)/inicio.tsx").is_file()
    assert "/** Pantalla en la ruta /inicio */" in leer(con_piezas / "app/(tabs)/inicio.tsx")


def test_pantalla_sin_sufijo_duplicado_e_index(proyecto, capsys):
    assert main(["nuevo", "pantalla", "PerfilPantalla"]) == 0
    assert "export default function PerfilPantalla()" in leer(proyecto / "app/perfil.tsx")
    capsys.readouterr()
    assert main(["nuevo", "pantalla", "index", "--carpeta", "productos"]) == 0
    assert "router.push('/productos')" in capsys.readouterr().out


def test_pantalla_que_ya_existe(proyecto, capsys):
    assert main(["nuevo", "pantalla", "index"]) == 1
    assert "app/index.tsx" in capsys.readouterr().err.replace("\\", "/")


def test_carpeta_invalida(proyecto, capsys):
    assert main(["nuevo", "pantalla", "detalle", "--carpeta", "prod!"]) == 1
    assert "La carpeta" in capsys.readouterr().err


def test_componente_hook_y_servicio(con_piezas):
    assert "StyleSheet.create" in leer(con_piezas / "components/Tarjeta.tsx")
    assert "export { Tarjeta } from './Tarjeta';" in leer(con_piezas / "components/index.ts")
    assert "export function useContador<T>" in leer(con_piezas / "hooks/useContador.ts")
    http = leer(con_piezas / "services/http.ts")
    assert "process.env.EXPO_PUBLIC_API_URL" in http
    for texto in ("localhost", "10.0.2.2", "IP-DE-TU-PC", "0.0.0.0:8000"):
        assert texto in http
    assert "const RUTA = '/productos/';" in leer(con_piezas / "services/productoService.ts")


def test_detecta_react_native_antes_que_react(proyecto):
    from andamio.nucleo.deteccion import buscar_proyecto

    paquete = json.loads(leer(proyecto / "package.json"))
    paquete["dependencies"]["vite"] = "8.3.8"
    (proyecto / "package.json").write_text(json.dumps(paquete), encoding="utf-8")
    assert buscar_proyecto(proyecto / "app")[0].clave == "react-native"


def test_menu_pantalla_con_carpeta(proyecto, respuestas, capsys):
    respuestas(["1", "detalle", "mal!", "(Tabs)", "s"])
    capsys.readouterr()
    assert main([]) == 0
    salida = capsys.readouterr().out
    assert "caracteres que no se pueden usar" in salida
    assert (proyecto / "app/(tabs)/detalle.tsx").is_file()


PANTALLA_QUE_USA_TODO = """\
import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';

import { Tarjeta } from '@/components';
import { useContador } from '@/hooks/useContador';
import { clienteService } from '@/services/clienteService';
import { productoService, type Producto } from '@/services/productoService';

export default function PruebaUso() {
  const { valor, setValor } = useContador(0);
  const [productos, setProductos] = useState<Producto[]>([]);
  useEffect(() => {
    productoService.listar().then(setProductos).catch(() => setValor(-1));
    void clienteService.eliminar(1);
  }, [setValor]);
  return (
    <View>
      <Tarjeta>
        <Text>{valor}</Text>
        {productos.map((p) => (
          <Text key={p.id}>{p.precio.toFixed(2)}</Text>
        ))}
      </Tarjeta>
    </View>
  );
}
"""


@pytest.mark.lento
@requiere_node
def test_npm_install_y_tsc(con_piezas):
    (con_piezas / "app/prueba-uso.tsx").write_text(PANTALLA_QUE_USA_TODO, encoding="utf-8")
    npm_install(con_piezas)
    ejecutar([NPX, "tsc", "--noEmit"], con_piezas)
    ejecutar([NPX, "expo", "install", "--check"], con_piezas, env={"EXPO_OFFLINE": "1"})
