"""
Script de datos semilla para desarrollo.
Crea un usuario administrador y vehículos/bodegas de ejemplo.
Ejecutar: python -m app.seed
"""

import asyncio
from app.database import AsyncSessionLocal, init_db
from app.models import Usuario, Vehiculo, Bodega
from app.auth import hash_password


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        # ── Usuario administrador ─────────────────────────────────────
        from sqlalchemy import select
        exists = await db.execute(select(Usuario).where(Usuario.email == "admin@ecologistica.pe"))
        if not exists.scalar_one_or_none():
            admin = Usuario(
                nombre="Administrador EcoLogística",
                email="admin@ecologistica.pe",
                password_hash=hash_password("Admin2026!"),
                rol="ADMIN_FLOTA",
            )
            db.add(admin)

        # ── Usuario operador ──────────────────────────────────────────
        exists = await db.execute(select(Usuario).where(Usuario.email == "operador@ecologistica.pe"))
        if not exists.scalar_one_or_none():
            operador = Usuario(
                nombre="Operador Logístico",
                email="operador@ecologistica.pe",
                password_hash=hash_password("Operador2026!"),
                rol="OPERADOR",
            )
            db.add(operador)

        # ── Usuario bodega ────────────────────────────────────────────
        exists = await db.execute(select(Usuario).where(Usuario.email == "bodega@tienda.pe"))
        if not exists.scalar_one_or_none():
            bodega_user = Usuario(
                nombre="Bodega Santa Anita",
                email="bodega@tienda.pe",
                password_hash=hash_password("Bodega2026!"),
                rol="BODEGA",
            )
            db.add(bodega_user)
            await db.flush()
            await db.refresh(bodega_user)

            bodega = Bodega(
                usuario_id=bodega_user.usuario_id,
                razon_social="Distribuidora Santa Anita S.A.C.",
                direccion_referencial="Av. Santa Rosa 456, Santa Anita, Lima",
                latitud=-12.0432,
                longitud=-76.9711,
            )
            db.add(bodega)

        # ── Vehículos de ejemplo ──────────────────────────────────────
        vehiculos_data = [
            {"placa": "ABC-123", "capacidad_kg": 1500.00, "tipo_combustible": "DIESEL", "factor_emision_co2": 2.68},
            {"placa": "DEF-456", "capacidad_kg": 2000.00, "tipo_combustible": "GASOLINA", "factor_emision_co2": 2.31},
            {"placa": "GHI-789", "capacidad_kg": 800.00, "tipo_combustible": "GLP", "factor_emision_co2": 1.51},
            {"placa": "JKL-012", "capacidad_kg": 3000.00, "tipo_combustible": "DIESEL", "factor_emision_co2": 2.68},
            {"placa": "MNO-345", "capacidad_kg": 1200.00, "tipo_combustible": "HIBRIDO", "factor_emision_co2": 1.10},
        ]
        for v in vehiculos_data:
            exists = await db.execute(select(Vehiculo).where(Vehiculo.placa == v["placa"]))
            if not exists.scalar_one_or_none():
                db.add(Vehiculo(**v))

        await db.commit()
        print("✅ Datos semilla insertados exitosamente")
        print("   Admin: admin@ecologistica.pe / Admin2026!")
        print("   Operador: operador@ecologistica.pe / Operador2026!")
        print("   Bodega: bodega@tienda.pe / Bodega2026!")


if __name__ == "__main__":
    asyncio.run(seed())
