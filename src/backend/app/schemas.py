"""
Schemas Pydantic — validación de entrada/salida para la API REST.
Sprint 1: Auth, Vehículos (US-001), Pedidos (US-003).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.tiempo import como_utc, lima_a_utc

# ═══════════════════════════════════════════════════════════════════════
#  AUTH (EN-002)
# ═══════════════════════════════════════════════════════════════════════

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    rol: str = Field(..., pattern=r"^(ADMIN_FLOTA|OPERADOR|CONDUCTOR|BODEGA|AUDITOR)$")
    telefono: Optional[str] = Field(None, max_length=20)
    canal_notificacion: str = Field("PORTAL", pattern=r"^(PORTAL|EMAIL|SMS|NINGUNO)$")


class UsuarioOut(BaseModel):
    usuario_id: str
    nombre: str
    email: str
    rol: str
    estado: str
    creado_en: datetime
    telefono: Optional[str] = None
    canal_notificacion: str = "PORTAL"

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
    volumen_m3: Optional[Decimal] = Field(None, gt=0)
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
    volumen_m3: Optional[Decimal] = None
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
    volumen_m3: Optional[Decimal] = None
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
    volumen_m3: Optional[Decimal] = Field(None, ge=0)
    distrito: Optional[str] = Field(None, max_length=40)
    ventana_inicio: datetime
    ventana_fin: datetime

    @field_validator("ventana_inicio")
    @classmethod
    def inicio_en_utc(cls, v: datetime) -> datetime:
        return lima_a_utc(v)

    @field_validator("ventana_fin")
    @classmethod
    def ventana_fin_posterior(cls, v: datetime, info) -> datetime:
        v = lima_a_utc(v)
        inicio = info.data.get("ventana_inicio")
        if inicio and v <= inicio:
            raise ValueError("ventana_fin debe ser posterior a ventana_inicio")
        return v


class PedidoUpdate(BaseModel):
    direccion: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    peso_kg: Optional[Decimal] = None
    volumen_m3: Optional[Decimal] = None
    distrito: Optional[str] = None
    ventana_inicio: Optional[datetime] = None
    ventana_fin: Optional[datetime] = None
    estado: Optional[str] = None

    @field_validator("ventana_inicio", "ventana_fin")
    @classmethod
    def ventana_en_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        return lima_a_utc(v)


class PedidoOut(BaseModel):
    pedido_id: str
    bodega_id: str
    direccion: str
    latitud: Decimal
    longitud: Decimal
    peso_kg: Decimal
    volumen_m3: Optional[Decimal] = None
    distrito: Optional[str] = None
    ventana_inicio: datetime
    ventana_fin: datetime
    estado: str
    reprogramaciones: int = 0
    entregado_en: Optional[datetime] = None
    creado_en: datetime

    model_config = {"from_attributes": True}

    @field_validator("ventana_inicio", "ventana_fin", "entregado_en", "creado_en")
    @classmethod
    def instante_en_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        return como_utc(v)  # SQLite no guarda la zona horaria: lo leído está en UTC


# ═══════════════════════════════════════════════════════════════════════
#  RUTAS, INDICADORES Y CARBONO (RF-003, RF-004, RF-005, RF-010)
# ═══════════════════════════════════════════════════════════════════════

class OptimizarRequest(BaseModel):
    limite_segundos: float = Field(40.0, ge=1, le=45, description="Tiempo máximo de cálculo; el SLA de RNF-001 es 45 s")


class ParadaOut(BaseModel):
    parada_id: str = ""
    pedido_id: str
    orden: int
    estado: str = "PENDIENTE"
    direccion: str
    distrito: Optional[str] = None
    entregada_en: Optional[datetime] = None
    evidencia_tipo: Optional[str] = None
    motivo: Optional[str] = None
    ventana_inicio: Optional[datetime] = None
    ventana_fin: Optional[datetime] = None
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
    distancia_base_km: float = 0
    co2_base_kg: float = 0
    conductor_id: Optional[str] = None
    conductor_nombre: Optional[str] = None
    iniciada_en: Optional[datetime] = None
    completada_en: Optional[datetime] = None
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
    desde_cache: bool = False
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
    combustible_ahorrado_litros: float = 0.0
    rutas_completadas: int = 0
    co2_compensado_kg: float = 0.0
    arboles_compensados: float = 0.0
    distrito: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════
#  CONDUCTORES, ENTREGAS Y SINCRONIZACIÓN SIN CONEXIÓN (RF-004, RF-008)
# ═══════════════════════════════════════════════════════════════════════

MAX_EVIDENCIA = 400_000  # caracteres de la foto o firma codificada (≈ 300 KB)


class AsignarConductor(BaseModel):
    conductor_id: str


class EntregaIn(BaseModel):
    evidencia_tipo: Optional[str] = Field(None, pattern=r"^(FOTO|FIRMA)$")
    evidencia: Optional[str] = Field(None, max_length=MAX_EVIDENCIA)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    momento: Optional[datetime] = None
    clave_sync: Optional[str] = Field(None, min_length=8, max_length=64)


class ReprogramarIn(BaseModel):
    motivo: str = Field(..., min_length=3, max_length=300)
    momento: Optional[datetime] = None
    clave_sync: Optional[str] = Field(None, min_length=8, max_length=64)


class AccionSync(BaseModel):
    tipo: str = Field(..., pattern=r"^(ENTREGA|REPROGRAMACION)$")
    parada_id: str
    clave_sync: str = Field(..., min_length=8, max_length=64)
    evidencia_tipo: Optional[str] = Field(None, pattern=r"^(FOTO|FIRMA)$")
    evidencia: Optional[str] = Field(None, max_length=MAX_EVIDENCIA)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    motivo: Optional[str] = Field(None, max_length=300)
    momento: Optional[datetime] = None


class SyncIn(BaseModel):
    acciones: list[AccionSync] = Field(..., max_length=200)


class ResultadoSync(BaseModel):
    clave_sync: str
    estado: str  # APLICADA, DUPLICADA, RECHAZADA
    detalle: str = ""


class SyncOut(BaseModel):
    resultados: list[ResultadoSync]
    aplicadas: int
    duplicadas: int
    rechazadas: int


class UbicacionIn(BaseModel):
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)


class UbicacionOut(BaseModel):
    desviado: bool
    desviacion_km: float
    umbral_km: float
    reoptimizada: bool = False
    mensaje: str = ""


class EntregaOut(BaseModel):
    parada_id: str
    estado: str
    ruta_completable: bool
    reoptimizada: bool = False
    mensaje: str = ""


# ═══════════════════════════════════════════════════════════════════════
#  INCIDENCIAS Y RE-OPTIMIZACIÓN (RF-007)
# ═══════════════════════════════════════════════════════════════════════

TIPOS_INCIDENCIA = r"^(VIA_CERRADA|ACCIDENTE|AVERIA|PEDIDO_CANCELADO)$"


class IncidenciaCreate(BaseModel):
    tipo: str = Field(..., pattern=TIPOS_INCIDENCIA)
    descripcion: Optional[str] = Field(None, max_length=300)
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    radio_km: float = Field(0.5, gt=0, le=10)
    pedido_id: Optional[str] = None  # solo para PEDIDO_CANCELADO


class IncidenciaOut(BaseModel):
    incidencia_id: str
    ruta_id: str
    tipo: str
    descripcion: Optional[str] = None
    resultado: Optional[str] = None
    paradas_afectadas: int
    tiempo_ms: float
    creado_en: datetime

    model_config = {"from_attributes": True}


class ReoptimizacionOut(BaseModel):
    incidencia: IncidenciaOut
    tiempo_ms: float
    dentro_del_sla: bool
    ruta_actual: Optional[RutaOut] = None
    nuevas_rutas: list[RutaOut] = []
    pedidos_devueltos: list[SinAsignarOut] = []
    sugerencia: str = ""


# ═══════════════════════════════════════════════════════════════════════
#  NOTIFICACIONES (RF-009)
# ═══════════════════════════════════════════════════════════════════════

class NotificacionOut(BaseModel):
    notificacion_id: str
    pedido_id: Optional[str] = None
    tipo: str
    canal: str
    mensaje: str
    hora_estimada: Optional[datetime] = None
    estado_envio: str
    leida: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════
#  ADMINISTRACIÓN: USUARIOS, CONDUCTORES, PARÁMETROS, ZONAS, PRIVACIDAD
# ═══════════════════════════════════════════════════════════════════════

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    telefono: Optional[str] = Field(None, max_length=20)
    canal_notificacion: Optional[str] = Field(None, pattern=r"^(PORTAL|EMAIL|SMS|NINGUNO)$")
    rol: Optional[str] = Field(None, pattern=r"^(ADMIN_FLOTA|OPERADOR|CONDUCTOR|BODEGA|AUDITOR)$")
    password: Optional[str] = Field(None, min_length=8, max_length=128)


class ConductorCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    licencia: str = Field(..., min_length=5, max_length=20)
    telefono: Optional[str] = Field(None, max_length=20)


class ConductorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    licencia: Optional[str] = Field(None, min_length=5, max_length=20)
    telefono: Optional[str] = Field(None, max_length=20)
    activo: Optional[bool] = None


class ConductorOut(BaseModel):
    conductor_id: str
    usuario_id: str
    nombre: str
    email: str
    licencia: str
    telefono: Optional[str] = None
    activo: bool


class ParametrosIn(BaseModel):
    velocidad_kmh: float = Field(..., ge=5, le=80)
    servicio_min: float = Field(..., ge=0, le=60)
    limite_segundos: float = Field(..., ge=1, le=45)
    algoritmo: str = Field("clarke_wright_2opt", pattern=r"^(clarke_wright_2opt|tabu)$")


class ParametrosOut(ParametrosIn):
    pass


class ZonaCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=120)
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    radio_km: float = Field(..., gt=0, le=30)


class ZonaOut(ZonaCreate):
    zona_id: str
    activa: bool

    model_config = {"from_attributes": True}


class SolicitudPrivacidadOut(BaseModel):
    solicitud_id: str
    usuario_id: str
    estado: str
    solicitada_en: datetime
    plazo_limite: datetime
    atendida_en: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════
#  RESPUESTAS GENÉRICAS
# ═══════════════════════════════════════════════════════════════════════

class MensajeResponse(BaseModel):
    mensaje: str


class PaginatedResponse(BaseModel):
    total: int
    items: list
