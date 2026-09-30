"""
Modelos ORM — Sprint 1.
Tablas: usuarios, conductores, bodegas, vehiculos, restricciones_vehiculares, pedidos.
Alineados con el DDL del Documento 11 (Base de datos V_1_0_0).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Numeric, Boolean, SmallInteger, Text,
    DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Usuarios ─────────────────────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "usuarios"

    usuario_id = Column(String(36), primary_key=True, default=_uuid)
    nombre = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(
        String(30), nullable=False,
        # CheckConstraint se omite en SQLite (no soporta CHECK con IN de forma fiable)
    )
    estado = Column(String(20), nullable=False, default="ACTIVO")
    creado_en = Column(DateTime(timezone=True), default=_now)

    # --- Intentos de login (EN-002 — brute-force lockout) ---
    login_attempts = Column(SmallInteger, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    conductor = relationship("Conductor", back_populates="usuario", uselist=False)
    bodega = relationship("Bodega", back_populates="usuario", uselist=False)


# ── Conductores ───────────────────────────────────────────────────────
class Conductor(Base):
    __tablename__ = "conductores"

    conductor_id = Column(String(36), primary_key=True, default=_uuid)
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=False)
    licencia = Column(String(20), nullable=False, unique=True)
    telefono = Column(String(20), nullable=True)

    usuario = relationship("Usuario", back_populates="conductor")


# ── Bodegas ───────────────────────────────────────────────────────────
class Bodega(Base):
    __tablename__ = "bodegas"

    bodega_id = Column(String(36), primary_key=True, default=_uuid)
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=False)
    razon_social = Column(String(200), nullable=False)
    direccion_referencial = Column(Text, nullable=False)
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)

    usuario = relationship("Usuario", back_populates="bodega")
    pedidos = relationship("Pedido", back_populates="bodega")


# ── Vehículos ─────────────────────────────────────────────────────────
class Vehiculo(Base):
    __tablename__ = "vehiculos"

    vehiculo_id = Column(String(36), primary_key=True, default=_uuid)
    placa = Column(String(10), nullable=False, unique=True)
    capacidad_kg = Column(Numeric(8, 2), nullable=False)
    tipo_combustible = Column(String(20), nullable=False)
    factor_emision_co2 = Column(Numeric(10, 4), nullable=True)
    estado = Column(String(20), nullable=False, default="DISPONIBLE")

    restricciones = relationship("RestriccionVehicular", back_populates="vehiculo", cascade="all, delete-orphan")


# ── Restricciones vehiculares (Pico y Placa) ──────────────────────────
class RestriccionVehicular(Base):
    __tablename__ = "restricciones_vehiculares"

    restriccion_id = Column(String(36), primary_key=True, default=_uuid)
    vehiculo_id = Column(String(36), ForeignKey("vehiculos.vehiculo_id"), nullable=False)
    dia_restringido = Column(SmallInteger, nullable=False)
    exonerado = Column(Boolean, nullable=False, default=False)
    motivo_exoneracion = Column(Text, nullable=True)

    vehiculo = relationship("Vehiculo", back_populates="restricciones")


# ── Pedidos ───────────────────────────────────────────────────────────
class Pedido(Base):
    __tablename__ = "pedidos"

    pedido_id = Column(String(36), primary_key=True, default=_uuid)
    bodega_id = Column(String(36), ForeignKey("bodegas.bodega_id"), nullable=False)
    direccion = Column(Text, nullable=False)
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)
    peso_kg = Column(Numeric(8, 2), nullable=False)
    ventana_inicio = Column(DateTime(timezone=True), nullable=False)
    ventana_fin = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String(30), nullable=False, default="PENDIENTE")
    creado_en = Column(DateTime(timezone=True), default=_now)

    bodega = relationship("Bodega", back_populates="pedidos")

    __table_args__ = (
        Index("idx_pedidos_estado", "estado"),
        Index("idx_pedidos_bodega", "bodega_id"),
    )
