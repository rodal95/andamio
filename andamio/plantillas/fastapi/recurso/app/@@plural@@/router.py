"""API de @@titulo@@: /api/@@plural@@/

La lista acepta estos parámetros (igual que la API de Django):
    ?search=texto       busca en los campos de texto
    ?ordering=-creado   ordena por un campo (con "-" es de mayor a menor)
    ?campo=valor        filtra por igualdad
"""

@@imports_router@@
from fastapi import APIRouter, HTTPException, Response
@@import_sqlmodel@@

from app.db import Sesion
@@import_tipos_router@@

from .modelo import @@Nombre@@, @@Nombre@@Actualizar, @@Nombre@@Crear, @@Nombre@@Leer

router = APIRouter(prefix="/api/@@plural@@", tags=["@@titulo@@"])

# Campos por los que se puede ordenar con ?ordering=
ORDEN = {
    @@campos_orden@@
}


def buscar_o_404(sesion: Sesion, id_@@nombre@@: int) -> @@Nombre@@:
    @@nombre@@ = sesion.get(@@Nombre@@, id_@@nombre@@)
    if @@nombre@@ is None:
        raise HTTPException(status_code=404, detail="No encontrado.")
    return @@nombre@@


@router.get("/", response_model=list[@@Nombre@@Leer])
def listar(
    sesion: Sesion,
    search: str | None = None,
    ordering: str | None = None,
    @@parametros_filtro@@
):
    """Lista, con búsqueda, orden y filtros opcionales."""
    consulta = select(@@Nombre@@)
    @@filtros@@
    @@bloque_busqueda@@
    campo = (ordering or "id").lstrip("-")
    if campo in ORDEN:
        columna = col(ORDEN[campo])
        consulta = consulta.order_by(columna.desc() if (ordering or "").startswith("-") else columna)
    return sesion.exec(consulta).all()


@router.post("/", response_model=@@Nombre@@Leer, status_code=201)
def crear(datos: @@Nombre@@Crear, sesion: Sesion):
    @@nombre@@ = @@Nombre@@.model_validate(datos)
    sesion.add(@@nombre@@)
    sesion.commit()
    sesion.refresh(@@nombre@@)
    return @@nombre@@


@router.get("/{id_@@nombre@@}/", response_model=@@Nombre@@Leer)
def obtener(id_@@nombre@@: int, sesion: Sesion):
    return buscar_o_404(sesion, id_@@nombre@@)


@router.put("/{id_@@nombre@@}/", response_model=@@Nombre@@Leer)
def reemplazar(id_@@nombre@@: int, datos: @@Nombre@@Crear, sesion: Sesion):
    """Modifica todos los campos."""
    return guardar_cambios(sesion, buscar_o_404(sesion, id_@@nombre@@), datos.model_dump())


@router.patch("/{id_@@nombre@@}/", response_model=@@Nombre@@Leer)
def actualizar(id_@@nombre@@: int, datos: @@Nombre@@Actualizar, sesion: Sesion):
    """Modifica solo los campos que se envían."""
    # exclude_none: un campo enviado como null se ignora (los campos no pueden quedar vacíos).
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    return guardar_cambios(sesion, buscar_o_404(sesion, id_@@nombre@@), cambios)


@router.delete("/{id_@@nombre@@}/", status_code=204)
def eliminar(id_@@nombre@@: int, sesion: Sesion):
    sesion.delete(buscar_o_404(sesion, id_@@nombre@@))
    sesion.commit()
    return Response(status_code=204)


def guardar_cambios(sesion: Sesion, @@nombre@@: @@Nombre@@, cambios: dict) -> @@Nombre@@:
    @@nombre@@.sqlmodel_update(cambios)
    @@nombre@@.actualizado = ahora()
    sesion.add(@@nombre@@)
    sesion.commit()
    sesion.refresh(@@nombre@@)
    return @@nombre@@
