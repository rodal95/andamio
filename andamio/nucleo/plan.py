"""Plan de cambios: primero se calcula todo, después se valida y recién al final se escribe.

- Nunca se sobrescribe un archivo: si alguno ya existe, no se escribe nada.
- Si falla una escritura a mitad de camino (archivo bloqueado, disco lleno, Ctrl+C),
  se deshace todo lo hecho.
- Si falta un marcador, la pieza se genera igual y se indica qué pegar a mano.
"""

from __future__ import annotations

import codecs
import os
from dataclasses import dataclass, field
from pathlib import Path, PurePath

from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.insercion import (
    agregar_al_final,
    insertar_antes_de_marcador,
    linea_marcador,
    ya_presente,
)


@dataclass
class _Nuevo:
    ruta: Path
    contenido: bytes


@dataclass
class _Modificado:
    ruta: Path
    original: bytes
    texto: str
    bom: bool
    descripciones: list[str] = field(default_factory=list)

    def a_bytes(self) -> bytes:
        datos = self.texto.encode("utf-8")
        return codecs.BOM_UTF8 + datos if self.bom else datos


@dataclass
class Manual:
    ruta: Path
    texto: str
    motivo: str
    donde: str


class Plan:
    def __init__(self, raiz: Path) -> None:
        self.raiz = raiz
        self.nuevos: dict[Path, _Nuevo] = {}
        self.modificados: dict[Path, _Modificado] = {}
        self.carpetas: list[Path] = []
        self.manuales: list[Manual] = []
        self.mantenidos: list[Path] = []
        self.conflictos: list[str] = []

    # --- Construcción -------------------------------------------------------

    def rel(self, ruta: Path) -> str:
        try:
            return str(ruta.relative_to(self.raiz))
        except ValueError:
            return str(ruta)

    def _ruta(self, rel: str | PurePath) -> Path:
        return self.raiz / Path(rel)

    def crear(self, rel: str | PurePath, contenido: str | bytes, si_no_existe: bool = False) -> None:
        ruta = self._ruta(rel)
        datos = contenido.encode("utf-8") if isinstance(contenido, str) else contenido
        if ruta in self.nuevos:
            raise AndamioError(f"Dos plantillas generan el mismo archivo: {self.rel(ruta)}")
        if ruta.exists():
            if si_no_existe:
                self.mantenidos.append(ruta)
            else:
                self.conflictos.append(self.rel(ruta))
            return
        self.nuevos[ruta] = _Nuevo(ruta, datos)

    def crear_carpeta(self, rel: str | PurePath) -> None:
        ruta = self._ruta(rel)
        if not ruta.exists():
            self.carpetas.append(ruta)

    def exigir_inexistente(self, rel: str | PurePath) -> None:
        ruta = self._ruta(rel)
        if ruta.exists():
            self.conflictos.append(self.rel(ruta))

    def _texto_actual(self, ruta: Path) -> tuple[str, bytes, bool] | None:
        if ruta in self.modificados:
            m = self.modificados[ruta]
            return m.texto, m.original, m.bom
        if not ruta.is_file():
            return None
        original = ruta.read_bytes()
        bom = original.startswith(codecs.BOM_UTF8)
        return original.decode("utf-8-sig"), original, bom

    def insertar(
        self,
        rel: str | PurePath,
        bloque: str,
        marcador: str | None = None,
        descripcion: str = "",
        comentario: str = "#",
        crear_si_falta: bool = False,
        ubicacion: str = "",
    ) -> None:
        """Agrega `bloque` antes del marcador (o al final del archivo si marcador es None).

        `ubicacion` describe en palabras dónde va el bloque ("dentro de LOCAL_APPS"), para
        explicarle al alumno qué hacer si falta el marcador.
        """
        ruta = self._ruta(rel)
        donde = (
            f'antes de la línea "{linea_marcador(marcador, comentario)}"'
            if marcador
            else "al final del archivo"
        )
        sin_marcador = ubicacion or "en el lugar que corresponda"
        if ruta in self.nuevos:
            nuevo = self.nuevos[ruta]
            texto = nuevo.contenido.decode("utf-8")
            resultado = insertar_antes_de_marcador(texto, marcador, bloque) if marcador else agregar_al_final(texto, bloque)
            if resultado is None:
                self.manuales.append(Manual(ruta, bloque, "no se encontró el marcador", sin_marcador))
            else:
                nuevo.contenido = resultado.encode("utf-8")
            return
        try:
            actual = self._texto_actual(ruta)
        except UnicodeDecodeError:
            self.manuales.append(Manual(ruta, bloque, "el archivo no está guardado en UTF-8", donde))
            return
        except OSError as e:
            self.manuales.append(Manual(ruta, bloque, f"no se pudo leer ({e.strerror})", donde))
            return
        if actual is None:
            if crear_si_falta:
                self.crear(rel, bloque + "\n")
            else:
                self.manuales.append(Manual(ruta, bloque, "el archivo no existe", donde))
            return
        texto, original, bom = actual
        if ya_presente(texto, bloque):
            return
        if marcador:
            resultado = insertar_antes_de_marcador(texto, marcador, bloque)
            if resultado is None:
                self.manuales.append(
                    Manual(ruta, bloque, f'no se encontró la línea "{linea_marcador(marcador, comentario)}"', sin_marcador)
                )
                return
        else:
            resultado = agregar_al_final(texto, bloque)
        mod = self.modificados.setdefault(ruta, _Modificado(ruta, original, texto, bom))
        mod.texto = resultado
        if descripcion and descripcion not in mod.descripciones:
            mod.descripciones.append(descripcion)

    # --- Validación y resumen ----------------------------------------------

    def validar(self) -> None:
        if self.conflictos:
            lista = "\n".join(f"  - {c}" for c in dict.fromkeys(self.conflictos))
            raise AndamioError(
                f"No se generó nada porque estos archivos ya existen:\n{lista}",
                "andamio nunca sobrescribe archivos. Elegí otro nombre, o borrá esos archivos si querés generarlos de nuevo.",
            )

    def creados(self) -> list[Path]:
        return list(self.nuevos)

    def mostrar(self, titulo_creados: str = "Se van a crear", titulo_modificados: str = "Se van a modificar") -> None:
        if self.nuevos:
            consola.titulo(f"{titulo_creados}:")
            for ruta in self.nuevos:
                consola.escribir(consola.color("  + ", "verde") + self.rel(ruta))
        if self.modificados:
            consola.titulo(f"{titulo_modificados}:")
            for ruta, mod in self.modificados.items():
                detalle = f"  ({', '.join(mod.descripciones)})" if mod.descripciones else ""
                consola.escribir(consola.color("  ~ ", "amarillo") + self.rel(ruta) + consola.color(detalle, "gris"))
        if self.mantenidos:
            consola.titulo("Ya existen y no se tocan:")
            for ruta in self.mantenidos:
                consola.escribir(consola.color("  = ", "gris") + self.rel(ruta))
        if self.manuales:
            consola.titulo("Vas a tener que agregar a mano:")
            for m in self.manuales:
                consola.escribir(consola.color("  ! ", "rojo") + f"{self.rel(m.ruta)} ({m.motivo})")

    def mostrar_manuales(self) -> None:
        """Explica exactamente qué pegar y dónde, para los marcadores que faltaban."""
        for m in self.manuales:
            consola.escribir()
            consola.aviso(f"No se pudo modificar {self.rel(m.ruta)}: {m.motivo}.")
            consola.escribir(f"Abrí {self.rel(m.ruta)} y pegá estas líneas {m.donde}:")
            consola.escribir()
            for linea in m.texto.split("\n"):
                consola.escribir("    " + consola.color(linea, "cian"))

    # --- Escritura ----------------------------------------------------------

    def aplicar(self) -> None:
        self.validar()
        creadas: list[Path] = []
        escritos: list[Path] = []
        restaurar: list[_Modificado] = []
        try:
            for carpeta in self.carpetas:
                self._crear_carpetas(carpeta, creadas)
            for nuevo in self.nuevos.values():
                self._crear_carpetas(nuevo.ruta.parent, creadas)
                # "x": falla si el archivo apareció entre la validación y la escritura.
                with open(nuevo.ruta, "xb") as f:
                    escritos.append(nuevo.ruta)
                    f.write(nuevo.contenido)
            for mod in self.modificados.values():
                if mod.ruta.read_bytes() != mod.original:
                    raise AndamioError(f"{self.rel(mod.ruta)} cambió mientras andamio trabajaba. Se deshicieron los cambios.")
                restaurar.append(mod)
                mod.ruta.write_bytes(mod.a_bytes())
        except BaseException as e:
            self._deshacer(creadas, escritos, restaurar)
            if isinstance(e, OSError):
                ruta = self.rel(Path(e.filename)) if e.filename else "un archivo"
                raise AndamioError(
                    f"No se pudo escribir {ruta} ({e.strerror}). Se deshicieron todos los cambios.",
                    "Cerrá ese archivo si está abierto en otro programa y verificá que tengas permiso para escribir en la carpeta.",
                ) from e
            raise

    @staticmethod
    def _crear_carpetas(carpeta: Path, creadas: list[Path]) -> None:
        faltantes: list[Path] = []
        actual = carpeta
        while not actual.exists():
            faltantes.append(actual)
            actual = actual.parent
        for c in reversed(faltantes):
            c.mkdir()
            creadas.append(c)

    @staticmethod
    def _deshacer(creadas: list[Path], escritos: list[Path], restaurar: list[_Modificado]) -> None:
        for mod in restaurar:
            try:
                mod.ruta.write_bytes(mod.original)
            except OSError:
                pass
        for ruta in reversed(escritos):
            try:
                os.remove(ruta)
            except OSError:
                pass
        for carpeta in reversed(creadas):
            try:
                carpeta.rmdir()
            except OSError:
                pass
