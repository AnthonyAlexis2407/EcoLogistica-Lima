"""
Pruebas de integración automatizadas para la API REST de EcoLogística Lima (Sprint 1).
Verifica: Autenticación JWT (EN-002), Vehículos Ecológicos (US-001) y Pedidos (US-003).
"""

from datetime import datetime, timedelta, timezone
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.auth import hash_password
from app.models import Usuario, Bodega, Vehiculo, Pedido

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def async_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        # Crear usuario administrador
        admin_user = Usuario(
            nombre="Admin Sistema",
            email="admin@ecologistica.pe",
            password_hash=hash_password("Admin123!"),
            rol="ADMINISTRADOR",
            estado="ACTIVO"
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        # Crear bodega para pruebas de pedidos
        bodega = Bodega(
            usuario_id=admin_user.usuario_id,
            razon_social="Bodega Central Lima",
            direccion_referencial="Av. Venezuela 1500, Cercado de Lima",
            latitud=-12.0560,
            longitud=-77.0840
        )
        session.add(bodega)
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_login_exitoso(client):
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@ecologistica.pe", "password": "Admin123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_fallido(client):
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@ecologistica.pe", "password": "WrongPassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_obtener_usuario_actual(client):
    # Login
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "admin@ecologistica.pe", "password": "Admin123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_res = await client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "admin@ecologistica.pe"
    assert user_data["rol"] == "ADMINISTRADOR"


@pytest.mark.asyncio
async def test_crud_vehiculos(client):
    # Login
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "admin@ecologistica.pe", "password": "Admin123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Crear vehículo
    vehiculo_data = {
        "placa": "ECO-101",
        "capacidad_kg": 250.0,
        "tipo_combustible": "ELECTRICO",
        "factor_emision_co2": 0.0,
        "estado": "DISPONIBLE"
    }
    create_res = await client.post("/api/vehiculos", json=vehiculo_data, headers=headers)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["placa"] == "ECO-101"

    # Listar vehículos
    list_res = await client.get("/api/vehiculos", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1


@pytest.mark.asyncio
async def test_crud_pedidos(client, async_session):
    # Obtain bodega_id
    from sqlalchemy import select
    result = await async_session.execute(select(Bodega))
    bodega = result.scalars().first()

    # Login
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "admin@ecologistica.pe", "password": "Admin123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(timezone.utc)
    pedido_data = {
        "bodega_id": bodega.bodega_id,
        "direccion": "Av. Arequipa 2500, Lince",
        "latitud": -12.0890,
        "longitud": -77.0340,
        "peso_kg": 12.5,
        "ventana_inicio": now.isoformat(),
        "ventana_fin": (now + timedelta(hours=2)).isoformat(),
        "estado": "PENDIENTE"
    }
    create_res = await client.post("/api/pedidos", json=pedido_data, headers=headers)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["estado"] == "PENDIENTE"

    # Listar pedidos
    list_res = await client.get("/api/pedidos", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
