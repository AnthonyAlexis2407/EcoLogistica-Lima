"""
Pruebas de aceptación y regresión — Sprint 2.

Verifican los escenarios de rechazo (Ruta Infeliz) de los criterios de aceptación
de US-001 (EL-7), US-003 (EL-9) y EN-002 (EL-18), usando usuarios con los roles
reales del seed (ADMIN_FLOTA, OPERADOR, BODEGA) y la dependencia `get_db` REAL
(con su commit/rollback), no una sesión compartida: así detectan defectos de
persistencia que `tests/test_api.py` no puede ver.

Ejecutar:  cd src/backend && python -m pytest -q
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import database
from app.auth import hash_password
from app.database import Base
from app.main import app
from app.models import Bodega, Usuario

PASSWORDS = {
    "admin@test.pe": "Admin2026!",
    "operador@test.pe": "Operador2026!",
    "bodega.a@test.pe": "BodegaA2026!",
    "bodega.b@test.pe": "BodegaB2026!",
}


@pytest_asyncio.fixture
async def api(monkeypatch):
    """BD SQLite en memoria + get_db real (commit/rollback) + usuarios con roles reales."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(database, "AsyncSessionLocal", session_factory)

    bodegas = {}
    async with session_factory() as s:
        for email, rol, nombre in [
            ("admin@test.pe", "ADMIN_FLOTA", "Admin Flota"),
            ("operador@test.pe", "OPERADOR", "Operador Logístico"),
            ("bodega.a@test.pe", "BODEGA", "Bodega A"),
            ("bodega.b@test.pe", "BODEGA", "Bodega B"),
        ]:
            u = Usuario(
                nombre=nombre, email=email, rol=rol, estado="ACTIVO",
                password_hash=hash_password(PASSWORDS[email]),
            )
            s.add(u)
            await s.flush()
            if rol == "BODEGA":
                b = Bodega(
                    usuario_id=u.usuario_id, razon_social=nombre,
                    direccion_referencial="Av. Próceres de la Independencia, SJL",
                    latitud=-12.0, longitud=-77.0,
                )
                s.add(b)
                await s.flush()
                bodegas[email] = b.bodega_id
        await s.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield SimpleNamespace(
            client=client, bodega_a=bodegas["bodega.a@test.pe"], bodega_b=bodegas["bodega.b@test.pe"]
        )
    await engine.dispose()


async def _login(client, email):
    res = await client.post("/api/auth/login", json={"email": email, "password": PASSWORDS[email]})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _pedido(bodega_id, peso_kg):
    ahora = datetime.now(timezone.utc)
    return {
        "bodega_id": bodega_id, "direccion": "Jr. Los Pinos 123, El Agustino",
        "latitud": -12.04, "longitud": -77.00, "peso_kg": peso_kg,
        "ventana_inicio": ahora.isoformat(),
        "ventana_fin": (ahora + timedelta(hours=2)).isoformat(),
    }


# ── US-001 / EL-7 ─────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_us001_registro_valido_y_rechazo_de_placa_duplicada(api):
    h = await _login(api.client, "admin@test.pe")
    vehiculo = {"placa": "ABC-123", "capacidad_kg": 500, "tipo_combustible": "DIESEL"}

    ok = await api.client.post("/api/vehiculos/", json=vehiculo, headers=h)
    assert ok.status_code == 201

    dup = await api.client.post("/api/vehiculos/", json=vehiculo, headers=h)
    assert dup.status_code == 409
    assert "duplicidad" in dup.json()["detail"]


@pytest.mark.asyncio
async def test_us001_baja_logica_conserva_el_registro(api):
    h = await _login(api.client, "admin@test.pe")
    creado = await api.client.post(
        "/api/vehiculos/", json={"placa": "XYZ-987", "capacidad_kg": 300, "tipo_combustible": "GLP"}, headers=h
    )
    vehiculo_id = creado.json()["vehiculo_id"]

    baja = await api.client.delete(f"/api/vehiculos/{vehiculo_id}", headers=h)
    assert baja.status_code == 200

    fuera = await api.client.get("/api/vehiculos/?estado=FUERA_DE_SERVICIO", headers=h)
    assert [v["placa"] for v in fuera.json()] == ["XYZ-987"]


# ── US-003 / EL-9 ─────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_us003_pedido_valido_y_rechazo_por_exceso_de_capacidad(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await api.client.post(
        "/api/vehiculos/", json={"placa": "CAP-250", "capacidad_kg": 250, "tipo_combustible": "ELECTRICO"}, headers=admin
    )

    ok = await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 100), headers=operador)
    assert ok.status_code == 201
    assert ok.json()["estado"] == "PENDIENTE"

    excede = await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 900), headers=operador)
    assert excede.status_code == 422
    assert "excede la capacidad" in excede.json()["detail"]


# ── EN-002 / EL-18 (regresión del defecto DEF-001) ────────────────────
@pytest.mark.asyncio
async def test_en002_cuenta_se_bloquea_tras_tres_intentos_fallidos(api):
    email = "operador@test.pe"
    for _ in range(3):
        res = await api.client.post("/api/auth/login", json={"email": email, "password": "incorrecta"})
        assert res.status_code == 401

    # Con el bloqueo vigente, ni la contraseña correcta debe permitir el acceso (RN-001).
    bloqueado = await api.client.post("/api/auth/login", json={"email": email, "password": PASSWORDS[email]})
    assert bloqueado.status_code == 423


# ── RN-010 (aislamiento por bodega) ───────────────────────────────────
@pytest.mark.asyncio
async def test_rn010_bodega_solo_lista_sus_propios_pedidos(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    await api.client.post(
        "/api/vehiculos/", json={"placa": "AIS-001", "capacidad_kg": 800, "tipo_combustible": "DIESEL"}, headers=admin
    )
    await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 50), headers=operador)
    await api.client.post("/api/pedidos/", json=_pedido(api.bodega_b, 60), headers=operador)

    listado = await api.client.get("/api/pedidos/", headers=bodega_a)
    assert listado.status_code == 200
    assert {p["bodega_id"] for p in listado.json()} == {api.bodega_a}


@pytest.mark.asyncio
async def test_rn010_bodega_no_puede_registrar_pedido_para_otra_bodega(api):
    """Regresión de DEF-002."""
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    res = await api.client.post("/api/pedidos/", json=_pedido(api.bodega_b, 10), headers=bodega_a)
    assert res.status_code == 403


# ── RBAC / EN-002 (regresión de DEF-003) ──────────────────────────────
@pytest.mark.asyncio
async def test_en002_registro_publico_no_permite_autoasignarse_rol_de_administracion(api):
    """Regresión de DEF-003."""
    res = await api.client.post(
        "/api/auth/register",
        json={"nombre": "Persona Anonima", "email": "anonimo@test.pe", "password": "Clave12345", "rol": "ADMIN_FLOTA"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_en002_registro_publico_permite_el_rol_bodega(api):
    res = await api.client.post(
        "/api/auth/register",
        json={"nombre": "Bodega Nueva", "email": "nueva@test.pe", "password": "Clave12345", "rol": "BODEGA"},
    )
    assert res.status_code == 201
    assert res.json()["rol"] == "BODEGA"


@pytest.mark.asyncio
async def test_en002_admin_flota_puede_crear_usuarios_con_cualquier_rol(api):
    admin = await _login(api.client, "admin@test.pe")
    res = await api.client.post(
        "/api/auth/register",
        json={"nombre": "Operador Nuevo", "email": "op.nuevo@test.pe", "password": "Clave12345", "rol": "OPERADOR"},
        headers=admin,
    )
    assert res.status_code == 201
    assert res.json()["rol"] == "OPERADOR"


@pytest.mark.asyncio
async def test_rn010_bodega_si_puede_registrar_pedido_de_su_propia_bodega(api):
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    res = await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 10), headers=bodega_a)
    assert res.status_code == 201
    assert res.json()["bodega_id"] == api.bodega_a
