"""
Humo sobre PostgreSQL (producción): el mismo flujo de negocio que en SQLite, contra una base PostgreSQL real con el
controlador asyncpg. Verifica los tipos cifrados, las fechas con zona horaria (`timestamptz`), las restricciones únicas, los
filtros por fecha y las operaciones de cierre de ruta.

Solo se ejecuta si existe la variable `TEST_DATABASE_URL` (por ejemplo,
`postgresql+asyncpg://usuario:clave@localhost:5432/ecologistica`); GitHub Actions la define en el trabajo
«Backend sobre PostgreSQL». Cada ejecución vacía y recrea las tablas de esa base: no apunte a una base con datos.
"""

import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
import pytest_asyncio
from app import auth, database
from app.auth import hash_password
from app.cifrado import esta_cifrado
from app.database import Base
from app.main import app
from app.models import Bodega, Usuario
from app.optimizador import vaciar_cache
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="Defina TEST_DATABASE_URL para probar sobre PostgreSQL")

EVIDENCIA = {"evidencia_tipo": "FIRMA", "evidencia": "data:image/png;base64,iVBORw0KGgo=", "latitud": -12.04, "longitud": -77.0}


@pytest_asyncio.fixture
async def pg(monkeypatch):
    auth._FALLOS_DESCONOCIDOS.clear()
    vaciar_cache()
    motor = create_async_engine(URL, pool_pre_ping=True)
    async with motor.begin() as conexion:
        await conexion.run_sync(Base.metadata.drop_all)
        await conexion.run_sync(Base.metadata.create_all)
    fabrica = async_sessionmaker(motor, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(database, "AsyncSessionLocal", fabrica)

    async with fabrica() as sesion:
        for email, rol, nombre in [
            ("admin@pg.pe", "ADMIN_FLOTA", "Admin PG"), ("operador@pg.pe", "OPERADOR", "Operador PG"),
            ("bodega@pg.pe", "BODEGA", "Bodega PG"),
        ]:
            usuario = Usuario(nombre=nombre, email=email, rol=rol, password_hash=hash_password("Clave2026Pg!"))
            sesion.add(usuario)
            await sesion.flush()
            if rol == "BODEGA":
                bodega = Bodega(
                    usuario_id=usuario.usuario_id, razon_social=nombre, direccion_referencial="Av. PG 1, Ate",
                    latitud=-12.03, longitud=-76.92,
                )
                sesion.add(bodega)
                await sesion.flush()
                bodega_id = bodega.bodega_id
        await sesion.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as cliente:
        yield SimpleNamespace(client=cliente, bodega=bodega_id, fabrica=fabrica)
    await motor.dispose()


async def _login(cliente, email, clave="Clave2026Pg!"):
    res = await cliente.post("/api/auth/login", json={"email": email, "password": clave})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.mark.asyncio
async def test_flujo_completo_sobre_postgresql(pg):
    cliente = pg.client
    admin = await _login(cliente, "admin@pg.pe")
    operador = await _login(cliente, "operador@pg.pe")

    assert (await cliente.get("/api/health/ready")).json()["db"] == "ok"

    veh = await cliente.post("/api/vehiculos/", headers=admin, json={
        "placa": "PGV-001", "capacidad_kg": 2000, "volumen_m3": 12, "tipo_combustible": "DIESEL", "factor_emision_co2": 2.68,
    })
    assert veh.status_code == 201, veh.text

    # Las ventanas llegan SIN zona horaria (como el campo datetime-local del navegador): deben guardarse en UTC.
    manana = (datetime.now(timezone.utc) + timedelta(hours=1)).astimezone(timezone(timedelta(hours=-5)))
    ingreso = manana.replace(tzinfo=None, microsecond=0)
    for i in range(3):
        res = await cliente.post("/api/pedidos/", headers=operador, json={
            "bodega_id": pg.bodega, "direccion": f"Av. Postgres {i} 100", "latitud": -12.04 - i * 0.01, "longitud": -77.0,
            "peso_kg": 80, "volumen_m3": 0.5, "ventana_inicio": ingreso.isoformat(),
            "ventana_fin": (ingreso + timedelta(hours=8)).isoformat(),
        })
        assert res.status_code == 201, res.text
        assert res.json()["ventana_inicio"].endswith(("Z", "+00:00")), res.json()["ventana_inicio"]
        assert res.json()["distrito"]

    plan = (await cliente.post("/api/rutas/optimizar", headers=operador)).json()
    assert plan["pedidos_planificados"] == 3 and plan["sin_asignar"] == []

    conductor = (await cliente.post("/api/admin/conductores", headers=admin, json={
        "nombre": "Chofer PG", "email": "chofer@pg.pe", "password": "Clave2026Pg!", "licencia": "Q0000PG01",
    })).json()
    ruta_id = plan["rutas"][0]["ruta_id"]
    assert (await cliente.post(
        f"/api/rutas/{ruta_id}/conductor", headers=operador, json={"conductor_id": conductor["conductor_id"]},
    )).status_code == 200
    chofer = await _login(cliente, "chofer@pg.pe")
    assert (await cliente.post(f"/api/rutas/{ruta_id}/iniciar", headers=chofer)).status_code == 200
    ruta = (await cliente.get("/api/conductor/ruta", headers=chofer)).json()
    for parada in ruta["paradas"]:
        res = await cliente.post(f"/api/conductor/paradas/{parada['parada_id']}/entregar", headers=chofer, json=EVIDENCIA)
        assert res.status_code == 200, res.text
    assert (await cliente.post(f"/api/rutas/{ruta_id}/completar", headers=chofer)).status_code == 200

    # Indicadores con filtros de fecha sin zona horaria y reportes en los tres formatos.
    resumen = (await cliente.get("/api/indicadores/resumen?desde=2020-01-01T00:00:00", headers=admin)).json()
    assert resumen["rutas_completadas"] == 1 and resumen["pedidos"]["ENTREGADO"] == 3
    futuro = (await cliente.get("/api/indicadores/resumen?desde=2099-01-01T00:00:00", headers=admin)).json()
    assert futuro["pedidos"]["TOTAL"] == 0
    for formato in ("csv", "xlsx", "pdf"):
        assert (await cliente.get(f"/api/reportes/rutas.{formato}", headers=admin)).status_code == 200

    # Notificaciones solo de la bodega dueña.
    bodega = await _login(cliente, "bodega@pg.pe")
    tipos = {n["tipo"] for n in (await cliente.get("/api/notificaciones/", headers=bodega)).json()}
    assert {"ASIGNACION", "EN_RUTA", "ENTREGA"} <= tipos

    # Los datos personales están cifrados en la base real.
    async with pg.fabrica() as sesion:
        crudo = (await sesion.execute(text("SELECT nombre, email FROM usuarios LIMIT 1"))).one()
        assert esta_cifrado(crudo[0]) and esta_cifrado(crudo[1])
        direccion = (await sesion.execute(text("SELECT direccion, latitud FROM pedidos LIMIT 1"))).one()
        assert esta_cifrado(direccion[0]) and esta_cifrado(direccion[1])


@pytest.mark.asyncio
async def test_sincronizacion_idempotente_y_unicidad_sobre_postgresql(pg):
    cliente = pg.client
    admin = await _login(cliente, "admin@pg.pe")
    operador = await _login(cliente, "operador@pg.pe")
    await cliente.post("/api/vehiculos/", headers=admin, json={
        "placa": "PGV-002", "capacidad_kg": 2000, "tipo_combustible": "GLP", "factor_emision_co2": 1.51,
    })
    ahora = datetime.now(timezone.utc)
    await cliente.post("/api/pedidos/", headers=operador, json={
        "bodega_id": pg.bodega, "direccion": "Jr. Idempotente 1", "latitud": -12.05, "longitud": -77.03, "peso_kg": 10,
        "ventana_inicio": ahora.isoformat(), "ventana_fin": (ahora + timedelta(hours=6)).isoformat(),
    })
    ruta_id = (await cliente.post("/api/rutas/optimizar", headers=operador)).json()["rutas"][0]["ruta_id"]
    chofer_datos = {"nombre": "Chofer Dos", "email": "chofer2@pg.pe", "password": "Clave2026Pg!", "licencia": "Q0000PG02"}
    conductor = (await cliente.post("/api/admin/conductores", headers=admin, json=chofer_datos)).json()
    # Licencia y correo repetidos se rechazan (unicidad sobre columnas cifradas deterministas).
    assert (await cliente.post("/api/admin/conductores", headers=admin, json=chofer_datos)).status_code == 409
    await cliente.post(f"/api/rutas/{ruta_id}/conductor", headers=operador, json={"conductor_id": conductor["conductor_id"]})
    chofer = await _login(cliente, "chofer2@pg.pe")
    await cliente.post(f"/api/rutas/{ruta_id}/iniciar", headers=chofer)
    parada = (await cliente.get("/api/conductor/ruta", headers=chofer)).json()["paradas"][0]["parada_id"]
    accion = {"tipo": "ENTREGA", "parada_id": parada, "clave_sync": "clave-postgres-0001", **EVIDENCIA}
    primera = (await cliente.post("/api/conductor/sync", headers=chofer, json={"acciones": [accion]})).json()
    segunda = (await cliente.post("/api/conductor/sync", headers=chofer, json={"acciones": [accion]})).json()
    assert primera["aplicadas"] == 1 and segunda["duplicadas"] == 1


@pytest.mark.asyncio
async def test_anonimizacion_sobre_postgresql(pg):
    cliente = pg.client
    admin = await _login(cliente, "admin@pg.pe")
    bodega = await _login(cliente, "bodega@pg.pe")
    solicitud = (await cliente.post("/api/privacidad/solicitudes", headers=bodega)).json()
    atendida = await cliente.post(f"/api/privacidad/solicitudes/{solicitud['solicitud_id']}/atender", headers=admin)
    assert atendida.status_code == 200
    assert (await cliente.get("/api/auth/me", headers=bodega)).status_code == 401
