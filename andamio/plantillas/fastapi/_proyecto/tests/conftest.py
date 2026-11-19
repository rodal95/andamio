"""Configuración de los tests: una base de datos en memoria para cada test."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_sesion
from app.main import app


@pytest.fixture
def cliente():
    """Cliente de prueba de la API. Usa una base en memoria: no toca datos.db."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def sesion_de_prueba():
        with Session(engine) as sesion:
            yield sesion

    app.dependency_overrides[get_sesion] = sesion_de_prueba
    yield TestClient(app)
    app.dependency_overrides.clear()
