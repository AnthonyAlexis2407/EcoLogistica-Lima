"""
Modelos ORM de EcoLogística Lima. Alineados con el DDL del Documento 11 (Base de datos), sección 6 incluida.

Tablas: usuarios, conductores, bodegas, vehiculos, restricciones_vehiculares, pedidos, ejecuciones_optimizacion, rutas,
ruta_paradas, incidencias, notificaciones, emisiones_co2, zonas_protegidas, parametros_sistema y solicitudes_privacidad.

Los datos personales (nombre, correo, teléfono, licencia, direcciones, coordenadas y evidencia de entrega) se guardan
cifrados (RNF-008, RN-008); ver `app/cifrado.py`.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.cifrado import NumeroCifrado, TextoCifrado
from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Usuarios ─────────────────────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "usuarios"

    usuario_id = Column(String(36), primary_key=True, default=_uuid)
    nombre = Column(TextoCifrado, nullable=False)
    email = Column(TextoCifrado, nullable=False, unique=True, index=True)
    telefono = Column(TextoCifrado, nullable=True)
    # Canal por el que recibe avisos (RF-009): PORTAL, EMAIL, SMS o NINGUNO.
    canal_notificacion = Column(String(10), nullable=False, default="PORTAL")
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(30), nullable=False)
    estado = Column(String(20), nullable=False, default="ACTIVO")  # ACTIVO | ANONIMIZADO
    creado_en = Column(DateTime(timezone=True), default=_now)

    # --- Intentos de login (EN-002 — brute-force lockout) ---
    login_attempts = Column(SmallInteger, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    conductor = relationship("Conductor", back_populates="usuario", uselist=False)
    bodega = relationship("Bodega", back_populates="usuario", uselist=False)


# ── Conductores ───────────────────────────────────────────────────────
class Conductor(Base):
    __tablename__ = "conductores"

    conductor_id = Column(String(36), primary_key=True, default=_uuid)
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=False)
    licencia = Column(TextoCifrado, nullable=False, unique=True)
    telefono = Column(TextoCifrado, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    usuario = relationship("Usuario", back_populates="conductor")


# ── Bodegas ───────────────────────────────────────────────────────────
class Bodega(Base):
    __tablename__ = "bodegas"

    bodega_id = Column(String(36), primary_key=True, default=_uuid)
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=False)
    razon_social = Column(String(200), nullable=False)
    direccion_referencial = Column(TextoCifrado, nullable=False)
    latitud = Column(NumeroCifrado, nullable=False)
    longitud = Column(NumeroCifrado, nullable=False)

    usuario = relationship("Usuario", back_populates="bodega")
    pedidos = relationship("Pedido", back_populates="bodega")


# ── Vehículos ─────────────────────────────────────────────────────────
class Vehiculo(Base):
    __tablename__ = "vehiculos"

    vehiculo_id = Column(String(36), primary_key=True, default=_uuid)
    placa = Column(String(10), nullable=False, unique=True)
    capacidad_kg = Column(Numeric(8, 2), nullable=False)
    volumen_m3 = Column(Numeric(8, 2), nullable=True)
    tipo_combustible = Column(String(20), nullable=False)
    factor_emision_co2 = Column(Numeric(10, 4), nullable=True)
    estado = Column(String(20), nullable=False, default="DISPONIBLE")

    restricciones = relationship("RestriccionVehicular", back_populates="vehiculo", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_vehiculos_estado", "estado"),)


# ── Restricciones vehiculares (Pico y Placa) ──────────────────────────
class RestriccionVehicular(Base):
    __tablename__ = "restricciones_vehiculares"

    restriccion_id = Column(String(36), primary_key=True, default=_uuid)
    vehiculo_id = Column(String(36), ForeignKey("vehiculos.vehiculo_id"), nullable=False)
    dia_restringido = Column(SmallInteger, nullable=False)  # 1 = lunes … 7 = domingo
    exonerado = Column(Boolean, nullable=False, default=False)
    motivo_exoneracion = Column(Text, nullable=True)

    vehiculo = relationship("Vehiculo", back_populates="restricciones")


# ── Pedidos ───────────────────────────────────────────────────────────
class Pedido(Base):
    __tablename__ = "pedidos"

    pedido_id = Column(String(36), primary_key=True, default=_uuid)
    bodega_id = Column(String(36), ForeignKey("bodegas.bodega_id"), nullable=False)
    direccion = Column(TextoCifrado, nullable=False)
    latitud = Column(NumeroCifrado, nullable=False)
    longitud = Column(NumeroCifrado, nullable=False)
    distrito = Column(String(40), nullable=True)
    peso_kg = Column(Numeric(8, 2), nullable=False)
    volumen_m3 = Column(Numeric(8, 2), nullable=True)
    ventana_inicio = Column(DateTime(timezone=True), nullable=False)
    ventana_fin = Column(DateTime(timezone=True), nullable=False)
    # PENDIENTE, ASIGNADO, EN_RUTA, ENTREGADO, CANCELADO
    estado = Column(String(30), nullable=False, default="PENDIENTE")
    reprogramaciones = Column(SmallInteger, nullable=False, default=0)
    entregado_en = Column(DateTime(timezone=True), nullable=True)
    creado_en = Column(DateTime(timezone=True), default=_now)

    bodega = relationship("Bodega", back_populates="pedidos")

    __table_args__ = (
        Index("idx_pedidos_estado", "estado"),
        Index("idx_pedidos_bodega", "bodega_id"),
        Index("idx_pedidos_creado_en", "creado_en"),
    )


# ── Optimizaciones y rutas (RF-003, RF-005, RF-010) ────────────────────
class Optimizacion(Base):
    """Una corrida del motor de rutas: su registro permite auditar tiempos y algoritmos (RF-003)."""

    __tablename__ = "ejecuciones_optimizacion"

    optimizacion_id = Column(String(36), primary_key=True, default=_uuid)
    creado_por = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=True)
    creado_en = Column(DateTime(timezone=True), default=_now)
    algoritmo = Column(String(60), nullable=False)
    pedidos_planificados = Column(SmallInteger, nullable=False, default=0)
    pedidos_sin_asignar = Column(SmallInteger, nullable=False, default=0)
    distancia_km = Column(Numeric(12, 3), nullable=False, default=0)
    distancia_base_km = Column(Numeric(12, 3), nullable=False, default=0)
    co2_kg = Column(Numeric(12, 3), nullable=False, default=0)
    co2_base_kg = Column(Numeric(12, 3), nullable=False, default=0)
    tiempo_ms = Column(Numeric(10, 1), nullable=False, default=0)
    limite_alcanzado = Column(Boolean, nullable=False, default=False)
    es_reoptimizacion = Column(Boolean, nullable=False, default=False)
    desde_cache = Column(Boolean, nullable=False, default=False)

    rutas = relationship("Ruta", back_populates="optimizacion", cascade="all, delete-orphan")


class Ruta(Base):
    __tablename__ = "rutas"

    ruta_id = Column(String(36), primary_key=True, default=_uuid)
    optimizacion_id = Column(String(36), ForeignKey("ejecuciones_optimizacion.optimizacion_id"), nullable=False)
    vehiculo_id = Column(String(36), ForeignKey("vehiculos.vehiculo_id"), nullable=False)
    conductor_id = Column(String(36), ForeignKey("conductores.conductor_id"), nullable=True)
    # PLANIFICADA, EN_CURSO, COMPLETADA, CANCELADA, INTERRUMPIDA (avería: sus paradas pendientes pasan a otra ruta)
    estado = Column(String(20), nullable=False, default="PLANIFICADA")
    distancia_km = Column(Numeric(10, 3), nullable=False)
    distancia_base_km = Column(Numeric(10, 3), nullable=False, default=0)
    carga_kg = Column(Numeric(10, 2), nullable=False)
    co2_kg = Column(Numeric(10, 3), nullable=False)
    co2_base_kg = Column(Numeric(10, 3), nullable=False, default=0)
    duracion_min = Column(Numeric(8, 1), nullable=False)
    iniciada_en = Column(DateTime(timezone=True), nullable=True)
    completada_en = Column(DateTime(timezone=True), nullable=True)
    creado_en = Column(DateTime(timezone=True), default=_now)

    optimizacion = relationship("Optimizacion", back_populates="rutas")
    vehiculo = relationship("Vehiculo")
    conductor = relationship("Conductor")
    paradas = relationship(
        "ParadaRuta", back_populates="ruta", cascade="all, delete-orphan", order_by="ParadaRuta.orden",
    )

    __table_args__ = (Index("idx_rutas_estado", "estado"), Index("idx_rutas_vehiculo", "vehiculo_id"))


class ParadaRuta(Base):
    __tablename__ = "ruta_paradas"

    parada_id = Column(String(36), primary_key=True, default=_uuid)
    ruta_id = Column(String(36), ForeignKey("rutas.ruta_id"), nullable=False)
    pedido_id = Column(String(36), ForeignKey("pedidos.pedido_id"), nullable=False)
    orden = Column(SmallInteger, nullable=False)
    distancia_desde_anterior_km = Column(Numeric(10, 3), nullable=False, default=0)
    llegada_estimada = Column(DateTime(timezone=True), nullable=True)
    espera_min = Column(Numeric(8, 1), nullable=False, default=0)
    en_ventana = Column(Boolean, nullable=True)
    # PENDIENTE, ENTREGADA, REPROGRAMADA, RETIRADA
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    entregada_en = Column(DateTime(timezone=True), nullable=True)
    latitud_entrega = Column(NumeroCifrado, nullable=True)
    longitud_entrega = Column(NumeroCifrado, nullable=True)
    evidencia_tipo = Column(String(10), nullable=True)  # FOTO | FIRMA (RN-007)
    evidencia = Column(TextoCifrado, nullable=True)
    motivo = Column(Text, nullable=True)
    clave_sync = Column(String(64), nullable=True, unique=True)  # evita duplicar entregas al sincronizar sin conexión

    ruta = relationship("Ruta", back_populates="paradas")
    pedido = relationship("Pedido")


# ── Incidencias y re-optimización (RF-007) ─────────────────────────────
class Incidencia(Base):
    __tablename__ = "incidencias"

    incidencia_id = Column(String(36), primary_key=True, default=_uuid)
    ruta_id = Column(String(36), ForeignKey("rutas.ruta_id"), nullable=False)
    tipo = Column(String(20), nullable=False)  # VIA_CERRADA, ACCIDENTE, AVERIA, PEDIDO_CANCELADO, RETRASO
    descripcion = Column(Text, nullable=True)
    latitud = Column(Numeric(10, 7), nullable=True)
    longitud = Column(Numeric(10, 7), nullable=True)
    radio_km = Column(Numeric(6, 2), nullable=True)
    resultado = Column(Text, nullable=True)
    paradas_afectadas = Column(SmallInteger, nullable=False, default=0)
    tiempo_ms = Column(Numeric(10, 1), nullable=False, default=0)
    creado_por = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=True)
    creado_en = Column(DateTime(timezone=True), default=_now)


# ── Notificaciones (RF-009) ───────────────────────────────────────────
class Notificacion(Base):
    __tablename__ = "notificaciones"

    notificacion_id = Column(String(36), primary_key=True, default=_uuid)
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=False)  # destinatario
    pedido_id = Column(String(36), ForeignKey("pedidos.pedido_id"), nullable=True)
    tipo = Column(String(20), nullable=False)  # ASIGNACION, EN_RUTA, RETRASO, ENTREGA, REPROGRAMACION, INCIDENCIA
    canal = Column(String(10), nullable=False)  # PORTAL, EMAIL, SMS
    mensaje = Column(Text, nullable=False)
    hora_estimada = Column(DateTime(timezone=True), nullable=True)
    estado_envio = Column(String(15), nullable=False, default="ENVIADA")  # ENVIADA | NO_ENTREGADA
    leida = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime(timezone=True), default=_now)

    __table_args__ = (Index("idx_notificaciones_usuario", "usuario_id"),)


# ── Emisiones de CO₂ (RF-010, RN-006, RN-009) ──────────────────────────
class EmisionCO2(Base):
    __tablename__ = "emisiones_co2"

    emision_id = Column(String(36), primary_key=True, default=_uuid)
    ruta_id = Column(String(36), ForeignKey("rutas.ruta_id"), nullable=False, unique=True)
    kg_co2_emitido = Column(Numeric(12, 4), nullable=False)
    kg_co2_evitado = Column(Numeric(12, 4), nullable=False)
    arboles_equivalentes = Column(Numeric(10, 2), nullable=False)
    metodologia_calculo = Column(String(30), nullable=False, default="GLEC_ISO14083")
    creado_en = Column(DateTime(timezone=True), default=_now)


# ── Zonas protegidas (RN-003) y parámetros (administrador) ───────────────
class ZonaProtegida(Base):
    __tablename__ = "zonas_protegidas"

    zona_id = Column(String(36), primary_key=True, default=_uuid)
    nombre = Column(String(120), nullable=False, unique=True)
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)
    radio_km = Column(Numeric(6, 2), nullable=False)
    activa = Column(Boolean, nullable=False, default=True)


class ParametroSistema(Base):
    __tablename__ = "parametros_sistema"

    clave = Column(String(60), primary_key=True)
    valor = Column(String(120), nullable=False)
    actualizado_en = Column(DateTime(timezone=True), default=_now, onupdate=_now)


# ── Solicitudes de eliminación o anonimización (RN-008, RNF-008) ─────────
class SolicitudPrivacidad(Base):
    __tablename__ = "solicitudes_privacidad"

    solicitud_id = Column(String(36), primary_key=True, default=_uuid)
    usuario_id = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=False)
    estado = Column(String(15), nullable=False, default="PENDIENTE")  # PENDIENTE | ATENDIDA
    solicitada_en = Column(DateTime(timezone=True), default=_now)
    plazo_limite = Column(DateTime(timezone=True), nullable=False)  # 5 días hábiles
    atendida_en = Column(DateTime(timezone=True), nullable=True)
    atendida_por = Column(String(36), ForeignKey("usuarios.usuario_id"), nullable=True)
