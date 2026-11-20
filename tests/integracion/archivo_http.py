"""Ejecuta un archivo .http (el formato de REST Client de VS Code) contra una API en marcha.

Sirve para comprobar que las peticiones de ejemplo que genera andamio funcionan de verdad.
Entiende lo que usan esos archivos: variables (@base = ...), peticiones separadas por ###,
encabezados, cuerpo JSON y peticiones con nombre (# @name login) cuya respuesta se usa
después ({{login.response.body.access}}).
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

_VARIABLE = re.compile(r"^@([\w-]+)\s*=\s*(.*)$")
_USO = re.compile(r"\{\{\s*([\w.-]+)\s*\}\}")
_PETICION = re.compile(r"^(GET|POST|PUT|PATCH|DELETE)\s+(\S+)")


@dataclass
class Respuesta:
    titulo: str
    metodo: str
    url: str
    estado: int
    cuerpo: object


def _resolver(texto: str, variables: dict[str, str], respuestas: dict[str, object]) -> str:
    def reemplazar(m: re.Match) -> str:
        clave = m.group(1)
        if clave in variables:
            return _resolver(variables[clave], variables, respuestas)
        partes = clave.split(".")
        if len(partes) >= 3 and partes[1] == "response" and partes[2] == "body" and partes[0] in respuestas:
            valor = respuestas[partes[0]]
            for parte in partes[3:]:
                valor = valor[parte]
            return str(valor)
        raise KeyError(f"variable sin definir: {clave}")

    return _USO.sub(reemplazar, texto)


def ejecutar(texto: str, variables_extra: dict[str, str] | None = None) -> list[Respuesta]:
    """Ejecuta las peticiones en orden. `variables_extra` pisa las del archivo (ej.: base)."""
    variables: dict[str, str] = {}
    respuestas: dict[str, object] = {}
    resultados: list[Respuesta] = []
    for indice, bloque in enumerate(re.split(r"(?m)^###", texto)):
        lineas = bloque.split("\n")
        # Lo que va antes del primer ### no tiene título (variables y comentarios).
        titulo, lineas = ("", lineas) if indice == 0 else (lineas[0].strip(), lineas[1:])
        nombre = None
        peticion = None
        encabezados: dict[str, str] = {}
        cuerpo: list[str] = []
        en_cuerpo = False
        for linea in lineas:
            limpia = linea.strip()
            if en_cuerpo:
                cuerpo.append(linea)
                continue
            if peticion is None:
                if m := re.match(r"#\s*@name\s+(\w+)", limpia):
                    nombre = m.group(1)
                elif m := _VARIABLE.match(limpia):
                    variables[m.group(1)] = m.group(2)
                elif m := _PETICION.match(limpia):
                    peticion = (m.group(1), m.group(2))
                continue
            if not limpia:
                en_cuerpo = True
            elif not limpia.startswith("#"):
                clave, _, valor = limpia.partition(":")
                encabezados[clave.strip()] = valor.strip()
        variables.update(variables_extra or {})
        if peticion is None:
            continue
        metodo, url = peticion
        url = _resolver(url, variables, respuestas)
        datos = "\n".join(cuerpo).strip()
        encabezados = {k: _resolver(v, variables, respuestas) for k, v in encabezados.items()}
        pedido = urllib.request.Request(
            url,
            data=_resolver(datos, variables, respuestas).encode("utf-8") if datos else None,
            method=metodo,
            headers=encabezados,
        )
        try:
            with urllib.request.urlopen(pedido, timeout=15) as r:
                estado, contenido = r.status, r.read()
        except urllib.error.HTTPError as e:
            estado, contenido = e.code, e.read()
        try:
            respuesta = json.loads(contenido) if contenido else None
        except json.JSONDecodeError:
            respuesta = contenido.decode("utf-8", "replace")
        if nombre:
            respuestas[nombre] = respuesta
        resultados.append(Respuesta(titulo, metodo, url, estado, respuesta))
    return resultados
