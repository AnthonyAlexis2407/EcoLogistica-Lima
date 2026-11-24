"""
Servicios compartidos del dominio: parámetros del algoritmo, zonas protegidas, planificación de rutas, re-optimización
(RF-007), notificaciones (RF-009) y cierre de rutas con su registro de emisiones (RF-010, RN-009).

Los routers solo traducen HTTP; la lógica de negocio vive aquí para poder reutilizarla (por ejemplo, una avería vuelve a
planificar con el mismo código que la planificación inicial).
"""

import asyncio
import logging
import smtplib
import time
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import (
    Bodega,
    Conductor,
    EmisionCO2,
    Incidencia,
    Notificacion,
    Optimizacion,
    ParadaRuta,
    ParametroSistema,
    Pedido,
    RestriccionVehicular,
    Ruta,
    Usuario,
    Vehiculo,
    ZonaProtegida,
)
from app.optimizador import (
    CONSUMO_KM_POR_LITRO,
    Camion,
    Parametros,
    Punto,
    ResultadoOptimizacion,
    Zona,
    arboles_equivalentes,
    optimizar,
)
from app.schemas import (
    IncidenciaOut,
    ParadaOut,
    ReoptimizacionOut,
    RutaOut,
    SinAsignarOut,
    VehiculoExcluidoOut,
)
from app.tiempo import LIMA, ahora, utc

log = logging.getLogger("ecologistica.servicios")
MAX_PEDIDOS_POR_OPTIMIZACION = 1000  # RNF-006
SLA_REOPTIMIZACION_S = 45.0  # RF-007
UMBRAL_DESVIO_KM = 0.5  # RF-004: más de 500 m fuera de la ruta planificada

PARAMETROS_POR_DEFECTO: dict[str, float | str] = {
    "velocidad_kmh": 25.0,
    "servicio_min": 10.0,
    "limite_segundos": settings.OPTIMIZADOR_LIMITE_SEGUNDOS,
    "algoritmo": "clarke_wright_2opt",
}
ALGORITMOS = ("clarke_wright_2opt", "tabu")


def sumar_dias_habiles(desde: datetime, dias: int) -> datetime:
    """Fecha límite de atención de una solicitud (RN-008): `dias` días hábiles (lunes a viernes) después de `desde`."""
    actual: date = desde.date()
    restantes = dias
    while restantes > 0:
        actual += timedelta(days=1)
        if actual.isoweekday() <= 5:
            restantes -= 1
    return datetime.combine(actual, desde.timetz())


# ── Parámetros y zonas ─────────────────────────────────────────────────

async def cargar_parametros_dict(db: AsyncSession) -> dict[str, float | str]:
    valores = dict(PARAMETROS_POR_DEFECTO)
    for fila in (await db.execute(select(ParametroSistema))).scalars().all():
        if fila.clave == "algoritmo" and fila.valor in ALGORITMOS:
            valores["algoritmo"] = fila.valor
        elif fila.clave in valores and fila.clave != "algoritmo":
            valores[fila.clave] = float(fila.valor)
    return valores


async def cargar_parametros(db: AsyncSession) -> tuple[Parametros, float]:
    valores = await cargar_parametros_dict(db)
    parametros = Parametros(float(valores["velocidad_kmh"]), float(valores["servicio_min"]), str(valores["algoritmo"]))
    return parametros, float(valores["limite_segundos"])


async def cargar_zonas(db: AsyncSession) -> tuple[Zona, ...]:
    filas = (await db.execute(select(ZonaProtegida).where(ZonaProtegida.activa.is_(True)))).scalars().all()
    return tuple(Zona(z.nombre, float(z.latitud), float(z.longitud), float(z.radio_km)) for z in filas)


# ── Notificaciones (RF-009, RN-010) ────────────────────────────────────

def _enviar_correo(destino: str, asunto: str, cuerpo: str) -> None:
    mensaje = EmailMessage()
    mensaje["From"] = settings.SMTP_REMITENTE
    mensaje["To"] = destino
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as servidor:
        servidor.starttls()
        if settings.SMTP_USUARIO:
            servidor.login(settings.SMTP_USUARIO, settings.SMTP_CLAVE)
        servidor.send_message(mensaje)


class Notificador:
    """Crea los avisos del portal de la bodega dueña del pedido; nunca avisa a una bodega distinta (RN-010)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._usuarios: dict[str, Usuario | None] = {}

    async def _destinatario(self, bodega_id: str) -> Usuario | None:
        if bodega_id not in self._usuarios:
            bodega = await self.db.get(Bodega, bodega_id)
            self._usuarios[bodega_id] = await self.db.get(Usuario, bodega.usuario_id) if bodega else None
        return self._usuarios[bodega_id]

    async def avisar(self, pedido: Pedido, tipo: str, mensaje: str, hora_estimada: datetime | None = None) -> None:
        usuario = await self._destinatario(pedido.bodega_id)
        if usuario is None:
            return
        canal = usuario.canal_notificacion or "PORTAL"
        estado = "ENVIADA"
        if canal == "NINGUNO":
            # Sin canal de contacto no se puede avisar: queda registrado para que el operador contacte al cliente.
            estado = "NO_ENTREGADA"
            mensaje = f"Pendiente de contacto: {mensaje}"
        elif canal == "EMAIL" and settings.NOTIFICACIONES_MODO == "smtp" and settings.SMTP_HOST:
            try:
                await asyncio.to_thread(_enviar_correo, usuario.email, f"EcoLogística Lima: {tipo}", mensaje)
            except (OSError, smtplib.SMTPException):
                log.warning("notificacion_correo_fallida tipo=%s", tipo)
                estado = "NO_ENTREGADA"
        self.db.add(Notificacion(
            usuario_id=usuario.usuario_id, pedido_id=pedido.pedido_id, tipo=tipo, canal=canal, mensaje=mensaje,
            hora_estimada=hora_estimada, estado_envio=estado,
        ))


# ── Lectura de rutas ───────────────────────────────────────────────────

CON_DETALLE = (
    selectinload(Ruta.paradas).selectinload(ParadaRuta.pedido),
    selectinload(Ruta.vehiculo),
    selectinload(Ruta.conductor).selectinload(Conductor.usuario),
)


async def cargar_rutas(db: AsyncSession, *filtros) -> list[Ruta]:
    resultado = await db.execute(
        select(Ruta).where(*filtros).options(*CON_DETALLE).order_by(Ruta.creado_en.desc(), Ruta.ruta_id)
    )
    return list(resultado.scalars().all())


def ruta_out(ruta: Ruta) -> RutaOut:
    return RutaOut(
        ruta_id=ruta.ruta_id, vehiculo_id=ruta.vehiculo_id, placa=ruta.vehiculo.placa,
        tipo_combustible=ruta.vehiculo.tipo_combustible, capacidad_kg=float(ruta.vehiculo.capacidad_kg),
        estado=ruta.estado, distancia_km=float(ruta.distancia_km), carga_kg=float(ruta.carga_kg),
        co2_kg=float(ruta.co2_kg), duracion_min=float(ruta.duracion_min),
        distancia_base_km=float(ruta.distancia_base_km or 0), co2_base_kg=float(ruta.co2_base_kg or 0),
        conductor_id=ruta.conductor_id,
        conductor_nombre=ruta.conductor.usuario.nombre if ruta.conductor else None,
        iniciada_en=ruta.iniciada_en, completada_en=ruta.completada_en,
        paradas=[
            ParadaOut(
                parada_id=p.parada_id, pedido_id=p.pedido_id, orden=p.orden, estado=p.estado,
                direccion=p.pedido.direccion, distrito=p.pedido.distrito,
                latitud=float(p.pedido.latitud), longitud=float(p.pedido.longitud), peso_kg=float(p.pedido.peso_kg),
                distancia_desde_anterior_km=float(p.distancia_desde_anterior_km), llegada_estimada=p.llegada_estimada,
                espera_min=float(p.espera_min), en_ventana=p.en_ventana, entregada_en=p.entregada_en,
                evidencia_tipo=p.evidencia_tipo, motivo=p.motivo,
                ventana_inicio=p.pedido.ventana_inicio, ventana_fin=p.pedido.ventana_fin,
            )
            for p in sorted(ruta.paradas, key=lambda x: x.orden)
        ],
    )


# ── Planificación (RF-003) ─────────────────────────────────────────────

def _punto(p: Pedido) -> Punto:
    return Punto(
        id=p.pedido_id, latitud=float(p.latitud), longitud=float(p.longitud), peso_kg=float(p.peso_kg),
        ventana_inicio=utc(p.ventana_inicio), ventana_fin=utc(p.ventana_fin),
        volumen_m3=float(p.volumen_m3 or 0),
    )


def _camion(v: Vehiculo) -> Camion:
    return Camion(
        id=v.vehiculo_id, placa=v.placa, capacidad_kg=float(v.capacidad_kg), combustible=v.tipo_combustible,
        factor_co2=float(v.factor_emision_co2) if v.factor_emision_co2 is not None else None,
        volumen_m3=float(v.volumen_m3) if v.volumen_m3 is not None else None,
    )


async def vehiculos_aptos(
    db: AsyncSession, excluir: set[str] | None = None,
) -> tuple[list[Vehiculo], list[VehiculoExcluidoOut]]:
    """Vehículos disponibles sin ruta abierta, sin Pico y Placa vigente (RN-002) y con factor de emisión (RF-010)."""
    ocupados = select(Ruta.vehiculo_id).where(Ruta.estado.in_(("PLANIFICADA", "EN_CURSO")))
    vehiculos = (await db.execute(
        select(Vehiculo).where(Vehiculo.estado == "DISPONIBLE", Vehiculo.vehiculo_id.not_in(ocupados))
    )).scalars().all()
    dia_hoy = datetime.now(LIMA).isoweekday()  # 1 = lunes … 7 = domingo, como en el DDL
    restringidos = set((await db.execute(
        select(RestriccionVehicular.vehiculo_id).where(
            RestriccionVehicular.dia_restringido == dia_hoy, RestriccionVehicular.exonerado.is_(False),
        )
    )).scalars().all())
    excluidos: list[VehiculoExcluidoOut] = []
    aptos: list[Vehiculo] = []
    for v in vehiculos:
        if excluir and v.vehiculo_id in excluir:
            continue
        if v.vehiculo_id in restringidos:
            excluidos.append(VehiculoExcluidoOut(
                placa=v.placa, motivo="Restringido por Pico y Placa hoy, sin exoneración (RN-002)",
            ))
        elif v.factor_emision_co2 is None:
            excluidos.append(VehiculoExcluidoOut(
                placa=v.placa, motivo="Falta el factor de emisión de CO₂ en su ficha técnica",
            ))
        else:
            aptos.append(v)
    return aptos, excluidos


class Planificacion:
    def __init__(self, opt: Optimizacion, plan: ResultadoOptimizacion, excluidos: list[VehiculoExcluidoOut],
                 rutas: list[Ruta]):
        self.opt, self.plan, self.excluidos, self.rutas = opt, plan, excluidos, rutas


async def planificar(
    db: AsyncSession, pedidos: list[Pedido], usuario: Usuario, *, limite: float | None = None,
    es_reoptimizacion: bool = False, excluir_vehiculos: set[str] | None = None, avisar: bool = True,
) -> Planificacion:
    """Planifica `pedidos` con la flota apta, guarda la corrida y sus rutas y avisa a las bodegas (RF-009)."""
    params, limite_defecto = await cargar_parametros(db)
    zonas = await cargar_zonas(db)
    aptos, excluidos = await vehiculos_aptos(db, excluir_vehiculos)

    plan = await asyncio.to_thread(
        optimizar, [_punto(p) for p in pedidos], [_camion(v) for v in aptos],
        (settings.DEPOSITO_LATITUD, settings.DEPOSITO_LONGITUD), limite or limite_defecto, None, zonas, params, True,
    )

    por_id = {p.pedido_id: p for p in pedidos}
    opt = Optimizacion(
        creado_por=usuario.usuario_id, algoritmo=plan.algoritmo,
        pedidos_planificados=sum(len(r.paradas) for r in plan.rutas), pedidos_sin_asignar=len(plan.sin_asignar),
        distancia_km=plan.distancia_total_km, distancia_base_km=plan.distancia_base_km,
        co2_kg=plan.co2_total_kg, co2_base_kg=plan.co2_base_kg, tiempo_ms=plan.tiempo_ms,
        limite_alcanzado=plan.limite_alcanzado, es_reoptimizacion=es_reoptimizacion, desde_cache=plan.desde_cache,
    )
    db.add(opt)
    await db.flush()

    notificador = Notificador(db) if avisar else None
    for r in plan.rutas:
        ruta = Ruta(
            optimizacion_id=opt.optimizacion_id, vehiculo_id=r.camion_id, estado="PLANIFICADA",
            distancia_km=r.distancia_km, distancia_base_km=r.distancia_base_km, carga_kg=r.carga_kg,
            co2_kg=r.co2_kg, co2_base_kg=r.co2_base_kg, duracion_min=r.duracion_min,
        )
        db.add(ruta)
        await db.flush()
        for parada in r.paradas:
            db.add(ParadaRuta(
                ruta_id=ruta.ruta_id, pedido_id=parada.punto_id, orden=parada.orden,
                distancia_desde_anterior_km=parada.distancia_desde_anterior_km,
                llegada_estimada=parada.llegada, espera_min=parada.espera_min, en_ventana=parada.en_ventana,
            ))
            pedido = por_id[parada.punto_id]
            pedido.estado = "ASIGNADO"
            if notificador and parada.llegada:
                await notificador.avisar(
                    pedido, "ASIGNACION",
                    f"Su pedido fue asignado a una ruta. Hora estimada de llegada: {parada.llegada.astimezone(LIMA):%H:%M}.",
                    parada.llegada,
                )
    await db.flush()
    rutas = await cargar_rutas(db, Ruta.optimizacion_id == opt.optimizacion_id)
    return Planificacion(opt, plan, excluidos, rutas)


# ── Re-optimización dinámica (RF-007, RN-005) ──────────────────────────

def _posicion_actual(ruta: Ruta, deposito: tuple[float, float]) -> tuple[float, float]:
    """Última entrega confirmada de la ruta (o el depósito si todavía no hubo ninguna)."""
    hechas = [p for p in ruta.paradas if p.estado == "ENTREGADA" and p.latitud_entrega is not None]
    if hechas:
        ultima = max(hechas, key=lambda p: p.entregada_en or datetime.min.replace(tzinfo=timezone.utc))
        return float(ultima.latitud_entrega), float(ultima.longitud_entrega)
    entregadas = [p for p in ruta.paradas if p.estado == "ENTREGADA"]
    if entregadas:
        ultima = max(entregadas, key=lambda p: p.orden)
        return float(ultima.pedido.latitud), float(ultima.pedido.longitud)
    return deposito


async def reoptimizar_ruta(
    db: AsyncSession, ruta: Ruta, usuario: Usuario, *, tipo: str, descripcion: str | None = None,
    latitud: float | None = None, longitud: float | None = None, radio_km: float = 0.5,
    pedido_id: str | None = None, momento: datetime | None = None, posicion: tuple[float, float] | None = None,
) -> ReoptimizacionOut:
    """Recalcula lo que le falta a una ruta ante una incidencia o un retraso. Mide su tiempo frente al SLA de 45 s."""
    inicio = time.perf_counter()
    momento = utc(momento) or ahora()
    deposito = (settings.DEPOSITO_LATITUD, settings.DEPOSITO_LONGITUD)
    pendientes = [p for p in ruta.paradas if p.estado == "PENDIENTE"]
    devueltos: list[SinAsignarOut] = []
    nuevas_rutas: list[Ruta] = []
    sugerencia = ""

    incidencia = Incidencia(
        ruta_id=ruta.ruta_id, tipo=tipo, descripcion=descripcion, latitud=latitud, longitud=longitud,
        radio_km=radio_km if latitud is not None else None, creado_por=usuario.usuario_id,
    )
    db.add(incidencia)

    if tipo == "PEDIDO_CANCELADO":
        objetivo = next((p for p in pendientes if p.pedido_id == pedido_id), None)
        if objetivo is None:
            raise LookupError("El pedido no está pendiente en esta ruta")
        objetivo.estado = "RETIRADA"
        objetivo.motivo = "Pedido cancelado"
        objetivo.pedido.estado = "CANCELADO"
        pendientes = [p for p in pendientes if p is not objetivo]

    if tipo == "AVERIA":
        ruta.estado = "INTERRUMPIDA"
        ruta.vehiculo.estado = "EN_MANTENIMIENTO"
        for p in pendientes:
            p.estado = "RETIRADA"
            p.motivo = "Avería del vehículo"
            p.pedido.estado = "PENDIENTE"
        if pendientes:
            nuevo = await planificar(
                db, [p.pedido for p in pendientes], usuario, es_reoptimizacion=True,
                excluir_vehiculos={ruta.vehiculo_id},
            )
            nuevas_rutas = nuevo.rutas
            devueltos = [SinAsignarOut(pedido_id=pid, motivo=motivo) for pid, motivo in nuevo.plan.sin_asignar]
            placas = ", ".join(r.vehiculo.placa for r in nuevas_rutas) or "ninguno"
            sugerencia = (
                f"Se redistribuyeron {len(pendientes) - len(devueltos)} pedido(s) en {len(nuevas_rutas)} ruta(s) "
                f"nuevas con los vehículos: {placas}. Revise y asigne conductor."
            )
        else:
            sugerencia = "La ruta no tenía pedidos pendientes que redistribuir."
        incidencia.paradas_afectadas = len(pendientes)
    elif pendientes:
        # Mismo vehículo: se reordena lo que falta desde la posición actual evitando el área afectada.
        zonas = await cargar_zonas(db)
        if latitud is not None and longitud is not None:
            zonas = (*zonas, Zona("Incidencia", latitud, longitud, radio_km))
        params, limite = await cargar_parametros(db)
        origen = posicion or _posicion_actual(ruta, deposito)
        plan = await asyncio.to_thread(
            optimizar, [_punto(p.pedido) for p in pendientes], [_camion(ruta.vehiculo)], origen, limite, momento,
            zonas, params,
        )
        por_pedido = {p.pedido_id: p for p in pendientes}
        siguiente = max((p.orden for p in ruta.paradas if p.estado != "PENDIENTE"), default=0) + 1
        for rp in plan.rutas:
            for ppl in rp.paradas:
                parada = por_pedido.pop(ppl.punto_id)
                parada.orden = siguiente + ppl.orden - 1
                parada.distancia_desde_anterior_km = ppl.distancia_desde_anterior_km
                parada.llegada_estimada = ppl.llegada
                parada.espera_min = ppl.espera_min
                parada.en_ventana = ppl.en_ventana
        for pid, motivo in plan.sin_asignar:
            parada = por_pedido.pop(pid, None)
            if parada is None:
                continue
            parada.estado = "RETIRADA"
            parada.motivo = motivo
            parada.pedido.estado = "PENDIENTE"
            devueltos.append(SinAsignarOut(pedido_id=pid, motivo=motivo))
        recorrido = sum(float(p.distancia_desde_anterior_km) for p in ruta.paradas if p.estado == "ENTREGADA")
        ruta.distancia_km = round(recorrido + plan.distancia_total_km, 3)
        ruta.co2_kg = round(float(ruta.distancia_km) * _camion(ruta.vehiculo).kg_co2_por_km(), 3)
        incidencia.paradas_afectadas = len(pendientes)
        sugerencia = (
            f"Se reordenaron {len(pendientes) - len(devueltos)} parada(s) pendientes"
            + (f" y {len(devueltos)} volvieron a PENDIENTE por no ser viables." if devueltos else ".")
        )

    await db.flush()
    transcurrido = time.perf_counter() - inicio
    incidencia.tiempo_ms = round(transcurrido * 1000.0, 1)
    incidencia.resultado = sugerencia or "Sin paradas pendientes que recalcular."
    await db.flush()
    await db.refresh(incidencia)
    rutas = await cargar_rutas(db, Ruta.ruta_id == ruta.ruta_id)
    return ReoptimizacionOut(
        incidencia=IncidenciaOut.model_validate(incidencia), tiempo_ms=round(transcurrido * 1000.0, 1),
        dentro_del_sla=transcurrido <= SLA_REOPTIMIZACION_S, ruta_actual=ruta_out(rutas[0]) if rutas else None,
        nuevas_rutas=[ruta_out(r) for r in nuevas_rutas], pedidos_devueltos=devueltos, sugerencia=incidencia.resultado,
    )


# ── Cierre de ruta y emisiones (RF-010, RN-009) ────────────────────────

def parada_resuelta(parada: ParadaRuta) -> bool:
    return parada.estado in ("ENTREGADA", "REPROGRAMADA", "RETIRADA")


async def completar_ruta(db: AsyncSession, ruta: Ruta) -> EmisionCO2:
    """Cierra la ruta y registra su emisión y la compensación en árboles. Sin factor de emisión no se puede cerrar."""
    if ruta.vehiculo.factor_emision_co2 is None:
        raise ValueError("El vehículo no tiene factor de emisión de CO₂: complete su ficha técnica antes de cerrar la ruta")
    ruta.estado = "COMPLETADA"
    ruta.completada_en = ahora()
    evitado = max(0.0, float(ruta.co2_base_kg or 0) - float(ruta.co2_kg))
    emision = EmisionCO2(
        ruta_id=ruta.ruta_id, kg_co2_emitido=float(ruta.co2_kg), kg_co2_evitado=round(evitado, 4),
        arboles_equivalentes=arboles_equivalentes(evitado),
    )
    db.add(emision)
    await db.flush()
    return emision


def litros_ahorrados(distancia_base_km: float, distancia_km: float, combustible: str) -> float:
    """Combustible que se dejó de consumir frente a la línea base (RF-005); los eléctricos no consumen."""
    consumo = CONSUMO_KM_POR_LITRO.get(combustible, CONSUMO_KM_POR_LITRO["DIESEL"])
    return max(0.0, distancia_base_km - distancia_km) / consumo if consumo > 0 else 0.0
