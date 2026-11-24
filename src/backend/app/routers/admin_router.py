"""
Router de Administración — gestión de usuarios y conductores (RF-008), parámetros del algoritmo, zonas protegidas
(RN-003) y solicitudes de privacidad (RN-008, RNF-008).

RBAC: solo ADMIN_FLOTA, salvo registrar una solicitud de privacidad propia, que puede hacer cualquier usuario autenticado.
La eliminación física exige confirmación explícita y se rechaza si la cuenta tiene historial: en ese caso corresponde
anonimizarla.
"""

import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user, hash_password, require_roles
from app.database import get_db
from app.models import (
    Bodega,
    Conductor,
    Notificacion,
    ParadaRuta,
    ParametroSistema,
    Pedido,
    Ruta,
    SolicitudPrivacidad,
    Usuario,
    ZonaProtegida,
)
from app.optimizador import vaciar_cache
from app.schemas import (
    ConductorCreate,
    ConductorOut,
    ConductorUpdate,
    MensajeResponse,
    ParametrosIn,
    ParametrosOut,
    SolicitudPrivacidadOut,
    UsuarioOut,
    UsuarioUpdate,
    ZonaCreate,
    ZonaOut,
)
from app.servicios import ahora, cargar_parametros_dict, sumar_dias_habiles

router = APIRouter(prefix="/api/admin", tags=["Administración"])
router_privacidad = APIRouter(prefix="/api/privacidad", tags=["Privacidad (RN-008)"])
_ADMIN = require_roles("ADMIN_FLOTA")
PLAZO_DIAS_HABILES = 5  # RNF-008


# ── Usuarios ───────────────────────────────────────────────────────────

@router.get("/usuarios", response_model=list[UsuarioOut])
async def listar_usuarios(db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN)):
    filas = await db.execute(select(Usuario).order_by(Usuario.creado_en, Usuario.usuario_id))
    return filas.scalars().all()


@router.put("/usuarios/{usuario_id}", response_model=UsuarioOut)
async def actualizar_usuario(
    usuario_id: str, payload: UsuarioUpdate, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN),
):
    objetivo = await db.get(Usuario, usuario_id)
    if objetivo is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    datos = payload.model_dump(exclude_unset=True)
    if "rol" in datos and objetivo.usuario_id == user.usuario_id and datos["rol"] != user.rol:
        raise HTTPException(status_code=409, detail="No puede cambiar su propio rol")
    clave = datos.pop("password", None)
    for campo, valor in datos.items():
        setattr(objetivo, campo, valor)
    if clave:
        objetivo.password_hash = hash_password(clave)
        objetivo.login_attempts = 0
        objetivo.locked_until = None
    await db.flush()
    return objetivo


@router.delete("/usuarios/{usuario_id}", response_model=MensajeResponse)
async def eliminar_usuario(
    usuario_id: str,
    confirmar: bool = Query(False, description="Debe ser true: la eliminación física no se puede deshacer"),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(_ADMIN),
):
    """Eliminación física, solo para cuentas sin historial (se confirma con `confirmar=true`)."""
    if not confirmar:
        raise HTTPException(status_code=400, detail="Confirme la eliminación definitiva con confirmar=true")
    objetivo = await db.get(Usuario, usuario_id)
    if objetivo is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if objetivo.usuario_id == user.usuario_id:
        raise HTTPException(status_code=409, detail="No puede eliminar su propia cuenta")
    conductor = (await db.execute(select(Conductor).where(Conductor.usuario_id == usuario_id))).scalar_one_or_none()
    bodega = (await db.execute(select(Bodega).where(Bodega.usuario_id == usuario_id))).scalar_one_or_none()
    historial = False
    if conductor is not None:
        rutas_previas = await db.execute(select(Ruta.ruta_id).where(Ruta.conductor_id == conductor.conductor_id))
        historial = rutas_previas.first() is not None
    if bodega is not None:
        pedidos_previos = await db.execute(select(Pedido.pedido_id).where(Pedido.bodega_id == bodega.bodega_id))
        historial = historial or pedidos_previos.first() is not None
    if historial:
        raise HTTPException(
            status_code=409,
            detail="La cuenta tiene historial de rutas o pedidos: use la anonimización en lugar de eliminarla",
        )
    await db.execute(delete(Notificacion).where(Notificacion.usuario_id == usuario_id))
    await db.execute(delete(SolicitudPrivacidad).where(SolicitudPrivacidad.usuario_id == usuario_id))
    if conductor is not None:
        await db.delete(conductor)
    if bodega is not None:
        await db.delete(bodega)
    await db.delete(objetivo)
    await db.flush()
    return MensajeResponse(mensaje="Usuario eliminado definitivamente")


# ── Conductores ────────────────────────────────────────────────────────

def _conductor_out(c: Conductor) -> ConductorOut:
    return ConductorOut(
        conductor_id=c.conductor_id, usuario_id=c.usuario_id, nombre=c.usuario.nombre, email=c.usuario.email,
        licencia=c.licencia, telefono=c.telefono, activo=c.activo,
    )


async def _conductores(db: AsyncSession, *filtros) -> list[Conductor]:
    filas = await db.execute(
        select(Conductor).where(*filtros).options(selectinload(Conductor.usuario)).order_by(Conductor.conductor_id)
    )
    return list(filas.scalars().all())


@router.get("/conductores", response_model=list[ConductorOut])
async def listar_conductores(
    db: AsyncSession = Depends(get_db), user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    return [_conductor_out(c) for c in await _conductores(db)]


@router.post("/conductores", response_model=ConductorOut, status_code=status.HTTP_201_CREATED)
async def crear_conductor(
    payload: ConductorCreate, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN),
):
    """Crea la cuenta de acceso (rol CONDUCTOR) y su ficha de conductor en un solo paso."""
    if (await db.execute(select(Usuario.usuario_id).where(Usuario.email == payload.email))).first():
        raise HTTPException(status_code=409, detail="Ya existe un usuario con este correo electrónico")
    if (await db.execute(select(Conductor.conductor_id).where(Conductor.licencia == payload.licencia))).first():
        raise HTTPException(status_code=409, detail="Ya existe un conductor con esta licencia")
    usuario = Usuario(
        nombre=payload.nombre, email=payload.email, telefono=payload.telefono, rol="CONDUCTOR",
        password_hash=hash_password(payload.password),
    )
    db.add(usuario)
    await db.flush()
    conductor = Conductor(usuario_id=usuario.usuario_id, licencia=payload.licencia, telefono=payload.telefono)
    db.add(conductor)
    await db.flush()
    return _conductor_out((await _conductores(db, Conductor.conductor_id == conductor.conductor_id))[0])


@router.put("/conductores/{conductor_id}", response_model=ConductorOut)
async def actualizar_conductor(
    conductor_id: str, payload: ConductorUpdate, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN),
):
    encontrados = await _conductores(db, Conductor.conductor_id == conductor_id)
    if not encontrados:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    conductor = encontrados[0]
    datos = payload.model_dump(exclude_unset=True)
    if "nombre" in datos:
        conductor.usuario.nombre = datos.pop("nombre")
    if datos.get("activo") is False:
        abierta = (await db.execute(
            select(Ruta.ruta_id).where(
                Ruta.conductor_id == conductor_id, Ruta.estado.in_(("PLANIFICADA", "EN_CURSO")),
            )
        )).first()
        if abierta:
            raise HTTPException(status_code=409, detail="El conductor tiene una ruta abierta")
    for campo, valor in datos.items():
        setattr(conductor, campo, valor)
    await db.flush()
    return _conductor_out(conductor)


@router.delete("/conductores/{conductor_id}", response_model=MensajeResponse)
async def desactivar_conductor(
    conductor_id: str, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN),
):
    """Baja lógica: el conductor deja de poder recibir rutas, pero se conserva su historial."""
    await actualizar_conductor(conductor_id, ConductorUpdate(activo=False), db, user)
    return MensajeResponse(mensaje="Conductor desactivado")


# ── Parámetros del algoritmo ───────────────────────────────────────────

@router.get("/parametros", response_model=ParametrosOut)
async def obtener_parametros(db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN)):
    return ParametrosOut(**await cargar_parametros_dict(db))


@router.put("/parametros", response_model=ParametrosOut)
async def guardar_parametros(
    payload: ParametrosIn, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN),
):
    """Los parámetros se aplican desde la siguiente optimización; se descarta la caché de planes previos."""
    for clave, valor in payload.model_dump().items():
        fila = await db.get(ParametroSistema, clave)
        if fila is None:
            db.add(ParametroSistema(clave=clave, valor=str(valor)))
        else:
            fila.valor = str(valor)
    await db.flush()
    vaciar_cache()
    return ParametrosOut(**payload.model_dump())


# ── Zonas protegidas (RN-003) ──────────────────────────────────────────

@router.get("/zonas", response_model=list[ZonaOut])
async def listar_zonas(
    db: AsyncSession = Depends(get_db), user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    return (await db.execute(select(ZonaProtegida).order_by(ZonaProtegida.nombre))).scalars().all()


@router.post("/zonas", response_model=ZonaOut, status_code=status.HTTP_201_CREATED)
async def crear_zona(payload: ZonaCreate, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN)):
    if (await db.execute(select(ZonaProtegida.zona_id).where(ZonaProtegida.nombre == payload.nombre))).first():
        raise HTTPException(status_code=409, detail="Ya existe una zona con ese nombre")
    zona = ZonaProtegida(**payload.model_dump())
    db.add(zona)
    await db.flush()
    return zona


@router.delete("/zonas/{zona_id}", response_model=MensajeResponse)
async def eliminar_zona(zona_id: str, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN)):
    zona = await db.get(ZonaProtegida, zona_id)
    if zona is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    await db.delete(zona)
    await db.flush()
    return MensajeResponse(mensaje="Zona eliminada")


# ── Privacidad: eliminación o anonimización (RN-008, RNF-008) ───────────

@router_privacidad.post("/solicitudes", response_model=SolicitudPrivacidadOut, status_code=status.HTTP_201_CREATED)
async def solicitar_baja(db: AsyncSession = Depends(get_db), user: Usuario = Depends(get_current_user)):
    """El titular pide la eliminación o anonimización de sus datos; se atiende en 5 días hábiles como máximo."""
    previa = (await db.execute(
        select(SolicitudPrivacidad).where(
            SolicitudPrivacidad.usuario_id == user.usuario_id, SolicitudPrivacidad.estado == "PENDIENTE",
        )
    )).scalars().first()
    if previa:
        return previa
    ahora_ = ahora()
    solicitud = SolicitudPrivacidad(
        usuario_id=user.usuario_id, solicitada_en=ahora_, plazo_limite=sumar_dias_habiles(ahora_, PLAZO_DIAS_HABILES),
    )
    db.add(solicitud)
    await db.flush()
    return solicitud


@router_privacidad.get("/solicitudes", response_model=list[SolicitudPrivacidadOut])
async def listar_solicitudes(db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN)):
    filas = await db.execute(select(SolicitudPrivacidad).order_by(SolicitudPrivacidad.solicitada_en.desc()))
    return filas.scalars().all()


async def anonimizar_usuario(db: AsyncSession, usuario: Usuario) -> None:
    """Elimina los datos personales y de geolocalización de la cuenta, conservando los totales para los reportes."""
    usuario.nombre = "Usuario anonimizado"
    usuario.email = f"anonimo-{usuario.usuario_id}@anonimizado.invalid"
    usuario.telefono = None
    usuario.canal_notificacion = "NINGUNO"
    usuario.estado = "ANONIMIZADO"
    usuario.password_hash = hash_password(secrets.token_urlsafe(24))  # nadie conoce esta clave: la cuenta queda cerrada

    conductor = (await db.execute(select(Conductor).where(Conductor.usuario_id == usuario.usuario_id))).scalar_one_or_none()
    if conductor is not None:
        conductor.licencia = f"ANON-{conductor.conductor_id[:12]}"
        conductor.telefono = None
        conductor.activo = False
        for parada in (await db.execute(
            select(ParadaRuta).join(Ruta, Ruta.ruta_id == ParadaRuta.ruta_id)
            .where(Ruta.conductor_id == conductor.conductor_id)
        )).scalars():
            parada.latitud_entrega = None
            parada.longitud_entrega = None

    bodega = (await db.execute(select(Bodega).where(Bodega.usuario_id == usuario.usuario_id))).scalar_one_or_none()
    if bodega is not None:
        bodega.razon_social = "Bodega anonimizada"
        bodega.direccion_referencial = "Dato anonimizado"
        bodega.latitud = 0
        bodega.longitud = 0
        for pedido in (await db.execute(select(Pedido).where(Pedido.bodega_id == bodega.bodega_id))).scalars():
            if pedido.estado in ("PENDIENTE", "ASIGNADO"):
                pedido.estado = "CANCELADO"  # no se puede entregar a una dirección que ya no se conserva
            pedido.direccion = "Dato anonimizado"
            pedido.latitud = 0
            pedido.longitud = 0
        for parada in (await db.execute(
            select(ParadaRuta).join(Pedido, Pedido.pedido_id == ParadaRuta.pedido_id)
            .where(Pedido.bodega_id == bodega.bodega_id)
        )).scalars():
            parada.evidencia = None
            parada.latitud_entrega = None
            parada.longitud_entrega = None
    await db.execute(delete(Notificacion).where(Notificacion.usuario_id == usuario.usuario_id))


@router_privacidad.post("/solicitudes/{solicitud_id}/atender", response_model=SolicitudPrivacidadOut)
async def atender_solicitud(
    solicitud_id: str, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_ADMIN),
):
    solicitud = await db.get(SolicitudPrivacidad, solicitud_id)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.estado == "ATENDIDA":
        raise HTTPException(status_code=409, detail="La solicitud ya fue atendida")
    titular = await db.get(Usuario, solicitud.usuario_id)
    if titular is None:
        raise HTTPException(status_code=404, detail="El titular ya no existe")
    if titular.usuario_id == user.usuario_id:
        raise HTTPException(status_code=409, detail="Otra persona administradora debe atender su propia solicitud")
    await anonimizar_usuario(db, titular)
    solicitud.estado = "ATENDIDA"
    solicitud.atendida_en = ahora()
    solicitud.atendida_por = user.usuario_id
    await db.flush()
    return solicitud

