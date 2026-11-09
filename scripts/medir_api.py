"""Mide el tiempo de respuesta y el tamaño de los listados de la API (Informe Green IT).

Siembra una base SQLite en memoria con 1 000 vehículos y 1 000 pedidos, llama a los
endpoints de listado en el mismo proceso (sin red) y reporta la mediana de 200 repeticiones.

Uso (desde la raíz del repositorio):
    PYTHONPATH=src/backend python scripts/medir_api.py
"""

import asyncio
import statistics
import time
from datetime import datetime, timedelta, timezone

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import database
from app.auth import hash_password
from app.database import Base
from app.main import app
from app.models import Bodega, Pedido, Usuario, Vehiculo

REPETICIONES = 200
N_REGISTROS = 1000


async def sembrar(fabrica):
    async with fabrica() as s:
        admin = Usuario(nombre="Admin", email="admin@bench.pe", rol="ADMIN_FLOTA", estado="ACTIVO",
                        password_hash=hash_password("Admin2026!"))
        s.add(admin)
        await s.flush()
        bodega = Bodega(usuario_id=admin.usuario_id, razon_social="Bodega", direccion_referencial="Lima",
                        latitud=-12.0, longitud=-77.0)
        s.add(bodega)
        await s.flush()
        ahora = datetime.now(timezone.utc)
        s.add_all(Vehiculo(placa=f"B{i:05d}", capacidad_kg=500 + i % 900, tipo_combustible="DIESEL",
                           estado="DISPONIBLE") for i in range(N_REGISTROS))
        s.add_all(Pedido(bodega_id=bodega.bodega_id, direccion=f"Av. Los Pinos {i}, Lima", latitud=-12.04,
                         longitud=-77.0, peso_kg=10 + i % 90, ventana_inicio=ahora,
                         ventana_fin=ahora + timedelta(hours=2)) for i in range(N_REGISTROS))
        await s.commit()


async def medir(cliente, ruta, cabeceras):
    tiempos, tamano, codificacion = [], 0, ""
    for _ in range(REPETICIONES):
        t0 = time.perf_counter()
        r = await cliente.get(ruta, headers=cabeceras)
        tiempos.append((time.perf_counter() - t0) * 1000)
        tamano = int(r.headers.get("content-length", len(r.content)))
        codificacion = r.headers.get("content-encoding", "ninguna")
        assert r.status_code == 200, (ruta, r.status_code)
    return statistics.median(tiempos), tamano, codificacion


async def main():
    motor = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool,
                                connect_args={"check_same_thread": False})
    async with motor.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    fabrica = async_sessionmaker(motor, class_=AsyncSession, expire_on_commit=False)
    database.AsyncSessionLocal = fabrica
    await sembrar(fabrica)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://bench") as c:
        token = (await c.post("/api/auth/login", json={"email": "admin@bench.pe", "password": "Admin2026!"})).json()["access_token"]
        base = {"Authorization": f"Bearer {token}"}
        casos = [
            ("vehiculos limit=50 sin compresión", "/api/vehiculos/?limit=50", {**base, "Accept-Encoding": "identity"}),
            ("vehiculos limit=50 gzip/br", "/api/vehiculos/?limit=50", {**base, "Accept-Encoding": "gzip, br"}),
            ("pedidos limit=50 sin compresión", "/api/pedidos/?limit=50", {**base, "Accept-Encoding": "identity"}),
            ("pedidos limit=50 gzip/br", "/api/pedidos/?limit=50", {**base, "Accept-Encoding": "gzip, br"}),
        ]
        if "page" in str(app.openapi()["paths"]["/api/vehiculos/"]["get"]["parameters"]):
            casos += [
                ("vehiculos página 1 (12) gzip/br", "/api/vehiculos/?page=1", {**base, "Accept-Encoding": "gzip, br"}),
                ("pedidos página 1 (12) gzip/br", "/api/pedidos/?page=1", {**base, "Accept-Encoding": "gzip, br"}),
            ]
        print(f"{'caso':42s} {'mediana ms':>11s} {'bytes':>9s}  codificación")
        for nombre, ruta, cab in casos:
            ms, b, cod = await medir(c, ruta, cab)
            print(f"{nombre:42s} {ms:11.2f} {b:9d}  {cod}")
    await motor.dispose()


if __name__ == "__main__":
    asyncio.run(main())
