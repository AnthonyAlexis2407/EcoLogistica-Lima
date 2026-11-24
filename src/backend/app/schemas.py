"""
Schemas Pydantic — validación de entrada/salida para la API REST.
Sprint 1: Auth, Vehículos (US-001), Pedidos (US-003).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

# ═══════════════════════════════════════════════════════════════════════
#  AUTH (EN-002)
# ═══════════════════════════════════════════════════════════════════════

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    rol: str = Field(..., pattern=r"^(ADMIN_FLOTA|OPERADOR|CONDUCTOR|BODEGA|AUDITOR)$")


class UsuarioOut(BaseModel):
    usuario_id: str
    nombre: str
    email: str
    rol: str
    estado: str
    creado_en: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ═══════════════════════════════════════════════════════════════════════
#  VEHÍCULOS (US-001)
# ═══════════════════════════════════════════════════════════════════════

TIPOS_COMBUSTIBLE = {"GASOLINA", "DIESEL", "GLP", "HIBRIDO", "ELECTRICO"}
ESTADOS_VEHICULO = {"DISPONIBLE", "EN_MANTENIMIENTO", "FUERA_DE_SERVICIO"}


class VehiculoCreate(BaseModel):
    placa: str = Field(..., min_length=5, max_length=10)
    capacidad_kg: Decimal = Field(..., gt=0)
    tipo_combustible: str
    factor_emision_co2: Optional[Decimal] = None
    estado: str = "DISPONIBLE"

    @field_validator("tipo_combustible")
    @classmethod
    def validate_combustible(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in TIPOS_COMBUSTIBLE:
            raise ValueError(f"Tipo de combustible inválido. Valores permitidos: {', '.join(sorted(TIPOS_COMBUSTIBLE))}")
        return v

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in ESTADOS_VEHICULO:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(sorted(ESTADOS_VEHICULO))}")
        return v

    @field_validator("placa")
    @classmethod
    def normalize_placa(cls, v: str) -> str:
        return v.upper().strip().replace(" ", "")


class VehiculoUpdate(BaseModel):
    placa: Optional[str] = None
    capacidad_kg: Optional[Decimal] = None
    tipo_combustible: Optional[str] = None
    factor_emision_co2: Optional[Decimal] = None
    estado: Optional[str] = None

    @field_validator("tipo_combustible")
    @classmethod
    def validate_combustible(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip()
        if v not in TIPOS_COMBUSTIBLE:
            raise ValueError(f"Tipo de combustible inválido. Valores permitidos: {', '.join(sorted(TIPOS_COMBUSTIBLE))}")
        return v

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip()
        if v not in ESTADOS_VEHICULO:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(sorted(ESTADOS_VEHICULO))}")
        return v

    @field_validator("placa")
    @classmethod
    def normalize_placa(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.upper().strip().replace(" ", "")


class VehiculoOut(BaseModel):
    vehiculo_id: str
    placa: str
    capacidad_kg: Decimal
    tipo_combustible: str
    factor_emision_co2: Optional[Decimal] = None
    estado: str

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════
#  PEDIDOS (US-003)
# ═══════════════════════════════════════════════════════════════════════

class PedidoCreate(BaseModel):
    bodega_id: Optional[str] = None
    direccion: str = Field(..., min_length=3)
    latitud: Decimal = Field(..., ge=-90, le=90)
    longitud: Decimal = Field(..., ge=-180, le=180)
    peso_kg: Decimal = Field(..., gt=0)
    ventana_inicio: datetime
    ventana_fin: datetime

    @field_validator("ventana_fin")
    @classmethod
    def ventana_fin_posterior(cls, v: datetime, info) -> datetime:
        inicio = info.data.get("ventana_inicio")
        if inicio and v <= inicio:
            raise ValueError("ventana_fin debe ser posterior a ventana_inicio")
        return v


class PedidoUpdate(BaseModel):
    direccion: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    peso_kg: Optional[Decimal] = None
    ventana_inicio: Optional[datetime] = None
    ventana_fin: Optional[datetime] = None
    estado: Optional[str] = None


class PedidoOut(BaseModel):
    pedido_id: str
    bodega_id: str
    direccion: str
    latitud: Decimal
    longitud: Decimal
    peso_kg: Decimal
    ventana_inicio: datetime
    ventana_fin: datetime
    estado: str
    creado_en: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════
#  RUTAS, INDICADORES Y CARBONO (RF-003, RF-004, RF-005, RF-010)
# ═══════════════════════════════════════════════════════════════════════

class OptimizarRequest(BaseModel):
    limite_segundos: float = Field(40.0, ge=1, le=45, description="Tiempo máximo de cálculo; el SLA de RNF-001 es 45 s")


class ParadaOut(BaseModel):
    pedido_id: str
    orden: int
    direccion: str
    latitud: float
    longitud: float
    peso_kg: float
    distancia_desde_anterior_km: float
    llegada_estimada: Optional[datetime] = None
    espera_min: float = 0
    en_ventana: Optional[bool] = None


class RutaOut(BaseModel):
    ruta_id: str
    vehiculo_id: str
    placa: str
    tipo_combustible: str
    capacidad_kg: float
    estado: str
    distancia_km: float
    carga_kg: float
    co2_kg: float
    duracion_min: float
    paradas: list[ParadaOut]


class SinAsignarOut(BaseModel):
    pedido_id: str
    motivo: str


class VehiculoExcluidoOut(BaseModel):
    placa: str
    motivo: str


class OptimizacionOut(BaseModel):
    optimizacion_id: str
    algoritmo: str
    pedidos_planificados: int
    pedidos_sin_asignar: int
    distancia_km: float
    distancia_base_km: float
    ahorro_km_pct: float
    co2_kg: float
    co2_base_kg: float
    co2_evitado_kg: float
    ahorro_co2_pct: float
    arboles_equivalentes: float
    tiempo_ms: float
    limite_alcanzado: bool
    rutas: list[RutaOut]
    sin_asignar: list[SinAsignarOut]
    vehiculos_excluidos: list[VehiculoExcluidoOut] = []


class DepositoOut(BaseModel):
    latitud: float
    longitud: float


class RutasActivasOut(BaseModel):
    deposito: DepositoOut
    rutas: list[RutaOut]


class IndicadoresOut(BaseModel):
    vehiculos: dict[str, int]
    pedidos: dict[str, int]
    rutas_activas: int
    distancia_planificada_km: float
    co2_planificado_kg: float
    pedidos_en_ventana_pct: Optional[float] = None
    optimizaciones: int
    co2_evitado_kg: float
    ahorro_co2_pct: float
    ahorro_km_pct: float
    arboles_equivalentes: float


# ═══════════════════════════════════════════════════════════════════════
#  RESPUESTAS GENÉRICAS
# ═══════════════════════════════════════════════════════════════════════

class MensajeResponse(BaseModel):
    mensaje: str


class PaginatedResponse(BaseModel):
    total: int
    items: list
