"""
Script de datos semilla para desarrollo.
Crea usuarios, vehículos de ejemplo y pedidos semilla.
Ejecutar: python -m app.seed
"""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.auth import hash_password
from app.database import AsyncSessionLocal, init_db
from app.distritos import distrito_mas_cercano
from app.models import Bodega, Conductor, Pedido, Usuario, Vehiculo, ZonaProtegida


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        # ── Usuario administrador ─────────────────────────────────────
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
        bodega_obj = None
        exists = await db.execute(select(Usuario).where(Usuario.email == "bodega@tienda.pe"))
        bodega_user = exists.scalar_one_or_none()
        if not bodega_user:
            bodega_user = Usuario(
                nombre="Bodega Santa Anita",
                email="bodega@tienda.pe",
                password_hash=hash_password("Bodega2026!"),
                rol="BODEGA",
            )
            db.add(bodega_user)
            await db.flush()
            await db.refresh(bodega_user)

            bodega_obj = Bodega(
                usuario_id=bodega_user.usuario_id,
                razon_social="Distribuidora Santa Anita S.A.C.",
                direccion_referencial="Av. Santa Rosa 456, Santa Anita, Lima",
                latitud=-12.0432,
                longitud=-76.9711,
            )
            db.add(bodega_obj)
            await db.flush()
            await db.refresh(bodega_obj)
        else:
            b_res = await db.execute(select(Bodega).where(Bodega.usuario_id == bodega_user.usuario_id))
            bodega_obj = b_res.scalar_one_or_none()

        # ── Conductor y auditor de demostración ───────────────────────
        exists = await db.execute(select(Usuario).where(Usuario.email == "conductor@ecologistica.pe"))
        if not exists.scalar_one_or_none():
            chofer = Usuario(
                nombre="Conductor de Prueba", email="conductor@ecologistica.pe", telefono="+51900000001",
                password_hash=hash_password("Conductor2026!"), rol="CONDUCTOR",
            )
            db.add(chofer)
            await db.flush()
            db.add(Conductor(usuario_id=chofer.usuario_id, licencia="Q12345678", telefono="+51900000001"))
        exists = await db.execute(select(Usuario).where(Usuario.email == "auditor@ecologistica.pe"))
        if not exists.scalar_one_or_none():
            db.add(Usuario(
                nombre="Auditor Externo", email="auditor@ecologistica.pe",
                password_hash=hash_password("Auditor2026!"), rol="AUDITOR",
            ))

        # ── Zona protegida de demostración (RN-003) ───────────────────
        exists = await db.execute(select(ZonaProtegida).where(ZonaProtegida.nombre == "Zona protegida de demostración"))
        if not exists.scalar_one_or_none():
            db.add(ZonaProtegida(nombre="Zona protegida de demostración", latitud=-11.9000, longitud=-76.9000, radio_km=1.5))

        # ── Vehículos de ejemplo ──────────────────────────────────────
        vehiculos_data = [
            {"placa": "ABC-123", "volumen_m3": 9.0, "capacidad_kg": 1500.00, "tipo_combustible": "DIESEL", "factor_emision_co2": 2.68, "estado": "DISPONIBLE"},
            {"placa": "DEF-456", "volumen_m3": 12.0, "capacidad_kg": 2000.00, "tipo_combustible": "GASOLINA", "factor_emision_co2": 2.31, "estado": "DISPONIBLE"},
            {"placa": "GHI-789", "volumen_m3": 5.0, "capacidad_kg": 800.00, "tipo_combustible": "GLP", "factor_emision_co2": 1.51, "estado": "DISPONIBLE"},
            {"placa": "JKL-012", "volumen_m3": 18.0, "capacidad_kg": 3000.00, "tipo_combustible": "DIESEL", "factor_emision_co2": 2.68, "estado": "DISPONIBLE"},
            {"placa": "MNO-345", "volumen_m3": 8.0, "capacidad_kg": 1200.00, "tipo_combustible": "HIBRIDO", "factor_emision_co2": 1.10, "estado": "DISPONIBLE"},
            {"placa": "PQR-678", "volumen_m3": 15.0, "capacidad_kg": 2500.00, "tipo_combustible": "ELECTRICO", "factor_emision_co2": 0.00, "estado": "DISPONIBLE"},
        ]
        for v in vehiculos_data:
            exists = await db.execute(select(Vehiculo).where(Vehiculo.placa == v["placa"]))
            if not exists.scalar_one_or_none():
                db.add(Vehiculo(**v))

        await db.flush()

        # ── Pedidos de ejemplo ───────────────────────────────────────
        if bodega_obj:
            now = datetime.now(timezone.utc)
            pedidos_data = [
                {
                    "direccion": "Av. Larco 1020, Miraflores, Lima",
                    "latitud": -12.1220,
                    "longitud": -77.0305,
                    "peso_kg": 350.00,
                    "estado": "PENDIENTE",
                    "ventana_inicio": now + timedelta(hours=1),
                    "ventana_fin": now + timedelta(hours=5),
                },
                {
                    "direccion": "Av. Javier Prado Este 2465, San Borja, Lima",
                    "latitud": -12.0864,
                    "longitud": -77.0012,
                    "peso_kg": 680.00,
                    "estado": "ASIGNADO",
                    "ventana_inicio": now + timedelta(hours=2),
                    "ventana_fin": now + timedelta(hours=6),
                },
                {
                    "direccion": "Av. Carlos Izaguirre 890, Los Olivos, Lima",
                    "latitud": -11.9922,
                    "longitud": -77.0654,
                    "peso_kg": 1200.00,
                    "estado": "EN_RUTA",
                    "ventana_inicio": now + timedelta(hours=3),
                    "ventana_fin": now + timedelta(hours=7),
                },
                {
                    "direccion": "Av. Benavides 3450, Surco, Lima",
                    "latitud": -12.1287,
                    "longitud": -76.9944,
                    "peso_kg": 450.00,
                    "estado": "ENTREGADO",
                    "ventana_inicio": now - timedelta(hours=4),
                    "ventana_fin": now - timedelta(hours=1),
                },
                {
                    "direccion": "Av. La Marina 2100, San Miguel, Lima",
                    "latitud": -12.0776,
                    "longitud": -77.0890,
                    "peso_kg": 850.00,
                    "estado": "PENDIENTE",
                    "ventana_inicio": now + timedelta(hours=4),
                    "ventana_fin": now + timedelta(hours=8),
                },
            ]
            for p in pedidos_data:
                exists = await db.execute(select(Pedido).where(Pedido.direccion == p["direccion"]))
                if not exists.scalar_one_or_none():
                    p = {**p, "volumen_m3": round(p["peso_kg"] / 150, 2), "distrito": distrito_mas_cercano(p["latitud"], p["longitud"])}
                db.add(Pedido(bodega_id=bodega_obj.bodega_id, **p))

        await db.commit()
        print("✅ Datos semilla insertados exitosamente")
        print("   Admin: admin@ecologistica.pe / Admin2026!")
        print("   Operador: operador@ecologistica.pe / Operador2026!")
        print("   Bodega: bodega@tienda.pe / Bodega2026!")
        print("   Conductor: conductor@ecologistica.pe / Conductor2026!")
        print("   Auditor: auditor@ecologistica.pe / Auditor2026!")


if __name__ == "__main__":
    asyncio.run(seed())
