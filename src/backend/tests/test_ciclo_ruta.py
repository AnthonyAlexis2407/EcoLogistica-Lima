"""
Pruebas del ciclo de vida de la ruta (RF-004, RF-007, RF-008, RF-009, RF-010, RN-005, RN-007, RN-009, RN-010).

Cada prueba recorre la API real con base de datos en memoria: planificar, asignar conductor, iniciar, entregar con
evidencia, reprogramar, sincronizar sin conexión, registrar incidencias y completar la ruta.
"""

from datetime import timedelta

import pytest

from tests.test_rutas_api import AHORA, _escenario
from tests.utilidades import _login

EVIDENCIA = {"evidencia_tipo": "FIRMA", "evidencia": "data:image/png;base64,iVBORw0KGgo=", "latitud": -12.04, "longitud": -77.0}


async def _crear_conductor(api, admin, email="chofer@test.pe", licencia="Q12345678"):
    res = await api.client.post(
        "/api/admin/conductores",
        json={"nombre": "Chofer Prueba", "email": email, "password": "Chofer2026!", "licencia": licencia, "telefono": "+51900000009"},
        headers=admin,
    )
    assert res.status_code == 201, res.text
    login = await api.client.post("/api/auth/login", json={"email": email, "password": "Chofer2026!"})
    assert login.status_code == 200, login.text
    return res.json()["conductor_id"], {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _ruta_lista(api, pedidos=3, vehiculos=(("ABC-123", 1500),), iniciar=True):
    """Planifica, asigna conductor y (opcionalmente) inicia. Devuelve (admin, operador, chofer, ruta)."""
    admin, operador = await _escenario(api, vehiculos=vehiculos, pedidos=pedidos)
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    ruta_id = plan["rutas"][0]["ruta_id"]
    conductor_id, chofer = await _crear_conductor(api, admin)
    res = await api.client.post(f"/api/rutas/{ruta_id}/conductor", json={"conductor_id": conductor_id}, headers=operador)
    assert res.status_code == 200, res.text
    if iniciar:
        res = await api.client.post(f"/api/rutas/{ruta_id}/iniciar", headers=chofer)
        assert res.status_code == 200, res.text
    ruta = (await api.client.get("/api/conductor/ruta", headers=chofer)).json()
    return admin, operador, chofer, ruta


async def _estado_pedido(api, headers, pedido_id):
    return (await api.client.get(f"/api/pedidos/{pedido_id}", headers=headers)).json()["estado"]


# ── Flujo completo: planificar → entregar → completar → emisión ─────────

@pytest.mark.asyncio
async def test_flujo_completo_de_una_ruta_registra_emision_y_notifica_a_la_bodega(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=3)
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    ruta_id = plan["rutas"][0]["ruta_id"]

    # Sin conductor no se puede iniciar.
    assert (await api.client.post(f"/api/rutas/{ruta_id}/iniciar", headers=operador)).status_code == 409
    conductor_id, chofer = await _crear_conductor(api, admin)
    assert (await api.client.post(
        f"/api/rutas/{ruta_id}/conductor", json={"conductor_id": conductor_id}, headers=operador,
    )).status_code == 200
    assert (await api.client.post(f"/api/rutas/{ruta_id}/iniciar", headers=chofer)).json()["estado"] == "EN_CURSO"

    ruta = (await api.client.get("/api/conductor/ruta", headers=chofer)).json()
    assert ruta["conductor_nombre"] == "Chofer Prueba" and len(ruta["paradas"]) == 3
    # Con paradas pendientes no se puede completar.
    assert (await api.client.post(f"/api/rutas/{ruta_id}/completar", headers=chofer)).status_code == 409

    for parada in ruta["paradas"]:
        res = await api.client.post(f"/api/conductor/paradas/{parada['parada_id']}/entregar", json=EVIDENCIA, headers=chofer)
        assert res.status_code == 200, res.text
    assert res.json()["ruta_completable"] is True

    cierre = await api.client.post(f"/api/rutas/{ruta_id}/completar", headers=chofer)
    assert cierre.status_code == 200 and "árboles" in cierre.json()["mensaje"]

    indicadores = (await api.client.get("/api/indicadores/resumen", headers=admin)).json()
    assert indicadores["rutas_completadas"] == 1 and indicadores["co2_compensado_kg"] >= 0
    assert indicadores["pedidos"]["ENTREGADO"] == 3 and indicadores["combustible_ahorrado_litros"] >= 0

    # RF-009: la bodega recibe asignación, salida en ruta y entrega; RN-010: otra bodega no ve nada.
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    tipos = {n["tipo"] for n in (await api.client.get("/api/notificaciones/", headers=bodega_a)).json()}
    assert {"ASIGNACION", "EN_RUTA", "ENTREGA"} <= tipos
    bodega_b = await _login(api.client, "bodega.b@test.pe")
    assert (await api.client.get("/api/notificaciones/", headers=bodega_b)).json() == []


@pytest.mark.asyncio
async def test_la_notificacion_de_asignacion_incluye_la_hora_estimada_y_se_marca_leida(api):
    await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=1)
    operador = await _login(api.client, "operador@test.pe")
    await api.client.post("/api/rutas/optimizar", headers=operador)
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    res = await api.client.get("/api/notificaciones/", headers=bodega_a)
    aviso = res.json()[0]
    assert aviso["hora_estimada"] and "hora estimada" in aviso["mensaje"].lower() and aviso["leida"] is False
    assert res.headers["x-unread-count"] == "1"
    assert (await api.client.put(f"/api/notificaciones/{aviso['notificacion_id']}/leida", headers=bodega_a)).status_code == 200
    # Un aviso ajeno responde como inexistente.
    bodega_b = await _login(api.client, "bodega.b@test.pe")
    assert (await api.client.put(f"/api/notificaciones/{aviso['notificacion_id']}/leida", headers=bodega_b)).status_code == 404


@pytest.mark.asyncio
async def test_una_bodega_sin_canal_deja_el_aviso_pendiente_de_contacto(api):
    admin = await _login(api.client, "admin@test.pe")
    bodega = await _login(api.client, "bodega.a@test.pe")
    usuario = (await api.client.get("/api/auth/me", headers=bodega)).json()
    assert (await api.client.put(
        f"/api/admin/usuarios/{usuario['usuario_id']}", json={"canal_notificacion": "NINGUNO"}, headers=admin,
    )).status_code == 200
    await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=1)
    operador = await _login(api.client, "operador@test.pe")
    await api.client.post("/api/rutas/optimizar", headers=operador)
    pendientes = (await api.client.get("/api/notificaciones/pendientes-de-contacto", headers=operador)).json()
    assert len(pendientes) == 1 and pendientes[0]["estado_envio"] == "NO_ENTREGADA"
    assert pendientes[0]["mensaje"].startswith("Pendiente de contacto")


# ── Conductor: evidencia (RN-007), reprogramación y sincronización ───────

@pytest.mark.asyncio
async def test_la_entrega_exige_evidencia(api):
    _, _, chofer, ruta = await _ruta_lista(api)
    parada = ruta["paradas"][0]["parada_id"]
    sin = await api.client.post(f"/api/conductor/paradas/{parada}/entregar", json={}, headers=chofer)
    assert sin.status_code == 422 and "evidencia" in sin.json()["detail"].lower()
    solo_tipo = await api.client.post(
        f"/api/conductor/paradas/{parada}/entregar", json={"evidencia_tipo": "FOTO"}, headers=chofer,
    )
    assert solo_tipo.status_code == 422
    demasiado = await api.client.post(
        f"/api/conductor/paradas/{parada}/entregar", json={**EVIDENCIA, "evidencia": "x" * 500_000}, headers=chofer,
    )
    assert demasiado.status_code == 422


@pytest.mark.asyncio
async def test_una_parada_no_se_entrega_dos_veces(api):
    _, _, chofer, ruta = await _ruta_lista(api)
    parada = ruta["paradas"][0]["parada_id"]
    assert (await api.client.post(f"/api/conductor/paradas/{parada}/entregar", json=EVIDENCIA, headers=chofer)).status_code == 200
    assert (await api.client.post(f"/api/conductor/paradas/{parada}/entregar", json=EVIDENCIA, headers=chofer)).status_code == 409


@pytest.mark.asyncio
async def test_reprogramar_devuelve_el_pedido_a_pendiente_y_avisa(api):
    _, operador, chofer, ruta = await _ruta_lista(api)
    parada = ruta["paradas"][0]
    res = await api.client.post(
        f"/api/conductor/paradas/{parada['parada_id']}/reprogramar", json={"motivo": "Cliente ausente"}, headers=chofer,
    )
    assert res.status_code == 200 and res.json()["estado"] == "REPROGRAMADA"
    pedido = (await api.client.get(f"/api/pedidos/{parada['pedido_id']}", headers=operador)).json()
    assert pedido["estado"] == "PENDIENTE" and pedido["reprogramaciones"] == 1
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    assert "REPROGRAMACION" in {n["tipo"] for n in (await api.client.get("/api/notificaciones/", headers=bodega_a)).json()}


@pytest.mark.asyncio
async def test_la_sincronizacion_sin_conexion_es_idempotente(api):
    _, operador, chofer, ruta = await _ruta_lista(api)
    p1, p2 = ruta["paradas"][0], ruta["paradas"][1]
    cola = [
        {"tipo": "ENTREGA", "parada_id": p1["parada_id"], "clave_sync": "clave-offline-0001", **EVIDENCIA},
        {"tipo": "REPROGRAMACION", "parada_id": p2["parada_id"], "clave_sync": "clave-offline-0002", "motivo": "Sin acceso"},
    ]
    primera = (await api.client.post("/api/conductor/sync", json={"acciones": cola}, headers=chofer)).json()
    assert primera["aplicadas"] == 2 and primera["duplicadas"] == 0 and primera["rechazadas"] == 0
    # Reenviar la misma cola (la red falló antes de recibir la respuesta) no repite nada.
    segunda = (await api.client.post("/api/conductor/sync", json={"acciones": cola}, headers=chofer)).json()
    assert segunda["duplicadas"] == 2 and segunda["aplicadas"] == 0
    assert await _estado_pedido(api, operador, p1["pedido_id"]) == "ENTREGADO"
    # Una acción nueva sobre una parada ya resuelta se rechaza sin detener las demás.
    mezcla = [
        {"tipo": "ENTREGA", "parada_id": p1["parada_id"], "clave_sync": "clave-offline-0003", **EVIDENCIA},
        {"tipo": "ENTREGA", "parada_id": ruta["paradas"][2]["parada_id"], "clave_sync": "clave-offline-0004", **EVIDENCIA},
        {"tipo": "ENTREGA", "parada_id": ruta["paradas"][2]["parada_id"], "clave_sync": "clave-offline-0005"},
    ]
    res = (await api.client.post("/api/conductor/sync", json={"acciones": mezcla}, headers=chofer)).json()
    assert [r["estado"] for r in res["resultados"]] == ["RECHAZADA", "APLICADA", "RECHAZADA"]


@pytest.mark.asyncio
async def test_un_conductor_no_opera_las_paradas_de_otro(api):
    admin, operador, chofer, ruta = await _ruta_lista(api)
    _, otro = await _crear_conductor(api, admin, email="otro.chofer@test.pe", licencia="Q87654321")
    parada = ruta["paradas"][0]["parada_id"]
    assert (await api.client.post(f"/api/conductor/paradas/{parada}/entregar", json=EVIDENCIA, headers=otro)).status_code == 404
    assert (await api.client.get("/api/conductor/ruta", headers=otro)).status_code == 404
    ruta_id = ruta["ruta_id"]
    assert (await api.client.post(f"/api/rutas/{ruta_id}/completar", headers=otro)).status_code == 403


@pytest.mark.asyncio
async def test_un_conductor_solo_puede_tener_una_ruta_abierta(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 800), ("DEF-456", 800)), pedidos=2)
    # 2 pedidos de 100 kg se agrupan en una ruta; se fuerzan dos rutas con vehículos pequeños y pedidos pesados.
    for i in range(2):
        await api.client.post("/api/pedidos/", json={
            "bodega_id": api.bodega_a, "direccion": f"Av. Pesada {i}", "latitud": -12.1 - i * 0.05, "longitud": -77.1,
            "peso_kg": 700, "ventana_inicio": AHORA.isoformat(), "ventana_fin": (AHORA + timedelta(hours=8)).isoformat(),
        }, headers=operador)
    rutas = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()["rutas"]
    assert len(rutas) >= 2
    conductor_id, _ = await _crear_conductor(api, admin)
    assert (await api.client.post(
        f"/api/rutas/{rutas[0]['ruta_id']}/conductor", json={"conductor_id": conductor_id}, headers=operador,
    )).status_code == 200
    segundo = await api.client.post(
        f"/api/rutas/{rutas[1]['ruta_id']}/conductor", json={"conductor_id": conductor_id}, headers=operador,
    )
    assert segundo.status_code == 409


# ── Re-optimización (RF-007, RN-005) ─────────────────────────────────────

@pytest.mark.asyncio
async def test_un_retraso_que_rompe_ventanas_dispara_la_reoptimizacion_automatica(api):
    _, operador, chofer, ruta = await _ruta_lista(api)
    primera, resto = ruta["paradas"][0], ruta["paradas"][1:]
    tarde = {**EVIDENCIA, "momento": (AHORA + timedelta(hours=7)).isoformat()}
    res = await api.client.post(f"/api/conductor/paradas/{primera['parada_id']}/entregar", json=tarde, headers=chofer)
    assert res.status_code == 200 and res.json()["reoptimizada"] is True
    # Las ventanas de las demás ya vencieron: vuelven a PENDIENTE para planificarse de nuevo.
    for parada in resto:
        assert await _estado_pedido(api, operador, parada["pedido_id"]) == "PENDIENTE"
    incidencias = (await api.client.get(f"/api/rutas/{ruta['ruta_id']}/incidencias", headers=operador)).json()
    assert incidencias[0]["tipo"] == "RETRASO" and incidencias[0]["tiempo_ms"] < 45000


@pytest.mark.asyncio
async def test_via_cerrada_reordena_y_devuelve_lo_que_queda_dentro_del_area(api):
    _, operador, _, ruta = await _ruta_lista(api, iniciar=False)
    cerrada = ruta["paradas"][1]
    res = await api.client.post(f"/api/rutas/{ruta['ruta_id']}/incidencias", json={
        "tipo": "VIA_CERRADA", "descripcion": "Marcha", "latitud": cerrada["latitud"], "longitud": cerrada["longitud"],
        "radio_km": 0.3,
    }, headers=operador)
    assert res.status_code == 201, res.text
    cuerpo = res.json()
    assert cuerpo["dentro_del_sla"] is True and cuerpo["tiempo_ms"] < 45000
    # El pedido dentro del área vuelve a PENDIENTE; las demás paradas se reordenan rodeando el área cerrada.
    assert [d["pedido_id"] for d in cuerpo["pedidos_devueltos"]] == [cerrada["pedido_id"]]
    assert "zona protegida" in cuerpo["pedidos_devueltos"][0]["motivo"]
    assert await _estado_pedido(api, operador, cerrada["pedido_id"]) == "PENDIENTE"
    vigentes = [p for p in cuerpo["ruta_actual"]["paradas"] if p["estado"] == "PENDIENTE"]
    assert len(vigentes) == 2


@pytest.mark.asyncio
async def test_via_cerrada_exige_ubicacion(api):
    _, operador, _, ruta = await _ruta_lista(api, iniciar=False)
    res = await api.client.post(f"/api/rutas/{ruta['ruta_id']}/incidencias", json={"tipo": "ACCIDENTE"}, headers=operador)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_averia_interrumpe_la_ruta_y_redistribuye_en_otro_vehiculo(api):
    admin, operador, _, ruta = await _ruta_lista(
        api, vehiculos=(("ABC-123", 1500), ("DEF-456", 2000)), iniciar=False,
    )
    res = await api.client.post(
        f"/api/rutas/{ruta['ruta_id']}/incidencias", json={"tipo": "AVERIA", "descripcion": "Motor"}, headers=operador,
    )
    assert res.status_code == 201, res.text
    cuerpo = res.json()
    assert cuerpo["dentro_del_sla"] is True and len(cuerpo["nuevas_rutas"]) == 1
    assert cuerpo["nuevas_rutas"][0]["placa"] != ruta["placa"] and "redistribuyeron" in cuerpo["sugerencia"]
    vehiculos = {v["placa"]: v["estado"] for v in (await api.client.get("/api/vehiculos/", headers=admin)).json()}
    assert vehiculos[ruta["placa"]] == "EN_MANTENIMIENTO"
    abiertas = (await api.client.get("/api/rutas/?estado=INTERRUMPIDA", headers=operador)).json()["rutas"]
    assert [r["ruta_id"] for r in abiertas] == [ruta["ruta_id"]]


@pytest.mark.asyncio
async def test_pedido_cancelado_se_retira_de_la_ruta(api):
    _, operador, _, ruta = await _ruta_lista(api, iniciar=False)
    cancelado = ruta["paradas"][0]["pedido_id"]
    res = await api.client.post(
        f"/api/rutas/{ruta['ruta_id']}/incidencias", json={"tipo": "PEDIDO_CANCELADO", "pedido_id": cancelado}, headers=operador,
    )
    assert res.status_code == 201 and await _estado_pedido(api, operador, cancelado) == "CANCELADO"
    ajeno = await api.client.post(
        f"/api/rutas/{ruta['ruta_id']}/incidencias", json={"tipo": "PEDIDO_CANCELADO", "pedido_id": "no-existe"}, headers=operador,
    )
    assert ajeno.status_code == 404


# ── Desvío de GPS (RF-004) ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_el_desvio_de_gps_se_detecta_y_reoptimiza_desde_la_posicion_actual(api):
    _, operador, chofer, ruta = await _ruta_lista(api)
    primera = ruta["paradas"][0]
    en_ruta = await api.client.post(
        "/api/conductor/ubicacion", json={"latitud": primera["latitud"], "longitud": primera["longitud"]}, headers=chofer,
    )
    assert en_ruta.json()["desviado"] is False and en_ruta.json()["desviacion_km"] < 0.5
    desviado = await api.client.post("/api/conductor/ubicacion", json={"latitud": -12.2, "longitud": -77.2}, headers=chofer)
    assert desviado.json()["desviado"] is True and desviado.json()["reoptimizada"] is True
    incidencias = (await api.client.get(f"/api/rutas/{ruta['ruta_id']}/incidencias", headers=operador)).json()
    assert incidencias[0]["tipo"] == "DESVIO"


# ── Reglas de cierre y cancelación ───────────────────────────────────────

@pytest.mark.asyncio
async def test_sin_factor_de_emision_no_se_puede_cerrar_la_ruta(api):
    from app import database
    from app.models import Vehiculo
    from sqlalchemy import update

    admin, operador, chofer, ruta = await _ruta_lista(api, pedidos=1)
    async with database.AsyncSessionLocal() as sesion:
        await sesion.execute(update(Vehiculo).values(factor_emision_co2=None))
        await sesion.commit()
    await api.client.post(f"/api/conductor/paradas/{ruta['paradas'][0]['parada_id']}/entregar", json=EVIDENCIA, headers=chofer)
    res = await api.client.post(f"/api/rutas/{ruta['ruta_id']}/completar", headers=chofer)
    assert res.status_code == 409 and "factor de emisión" in res.json()["detail"]


@pytest.mark.asyncio
async def test_la_compensacion_solo_cuenta_rutas_completadas(api):
    admin, operador, chofer, ruta = await _ruta_lista(api, pedidos=2)
    antes = (await api.client.get("/api/indicadores/resumen", headers=admin)).json()
    assert antes["rutas_completadas"] == 0 and antes["arboles_compensados"] == 0
    for parada in ruta["paradas"]:
        await api.client.post(f"/api/conductor/paradas/{parada['parada_id']}/entregar", json=EVIDENCIA, headers=chofer)
    await api.client.post(f"/api/rutas/{ruta['ruta_id']}/completar", headers=chofer)
    despues = (await api.client.get("/api/indicadores/resumen", headers=admin)).json()
    assert despues["rutas_completadas"] == 1 and despues["co2_compensado_kg"] >= 0
    # Una ruta completada ya no admite cancelación.
    assert (await api.client.post(f"/api/rutas/{ruta['ruta_id']}/cancelar", headers=operador)).status_code == 409


@pytest.mark.asyncio
async def test_repetir_la_misma_optimizacion_usa_la_cache(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=3)
    primera = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    assert primera["desde_cache"] is False
    for ruta in primera["rutas"]:
        await api.client.post(f"/api/rutas/{ruta['ruta_id']}/cancelar", headers=operador)
    segunda = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    assert segunda["desde_cache"] is True and segunda["distancia_km"] == primera["distancia_km"]
