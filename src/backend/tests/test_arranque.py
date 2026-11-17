"""Pruebas del arranque de la aplicación: datos de demostración y claves de producción."""

import pytest
from app import main as principal
from app.config import settings


async def _sin_base_de_datos():
    return None


@pytest.mark.asyncio
async def test_el_arranque_carga_los_datos_de_demostracion_solo_si_se_pide(monkeypatch):
    llamadas = []

    async def seed_falso():
        llamadas.append(1)

    monkeypatch.setattr("app.seed.seed", seed_falso)
    monkeypatch.setattr(principal, "init_db", _sin_base_de_datos)

    monkeypatch.setattr(settings, "SEED_DEMO_DATA", False)
    async with principal.lifespan(principal.app):
        pass
    assert llamadas == []

    monkeypatch.setattr(settings, "SEED_DEMO_DATA", True)
    async with principal.lifespan(principal.app):
        pass
    assert llamadas == [1]


@pytest.mark.asyncio
async def test_en_produccion_el_arranque_rechaza_la_clave_por_defecto(monkeypatch):
    monkeypatch.setattr(principal, "init_db", _sin_base_de_datos)
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "SECRET_KEY", "dev-secret-key-cambiar-en-produccion-2026")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        async with principal.lifespan(principal.app):
            pass
