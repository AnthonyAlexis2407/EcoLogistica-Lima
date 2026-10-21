"""
Pruebas de los routers de vehículos y pedidos — Sprint 3 (calidad de código).

Cubren consulta por ID, conteo, actualización, baja/cancelación, filtros y RBAC,
con la misma base en memoria y `get_db` real que las pruebas de aceptación.

Ejecutar:  cd src/backend && python -m pytest -q --cov=app
"""

import pytest

from tests.test_criterios_aceptacion import _login, _pedido, api  # noqa: F401  (fixture `api`)


async def _crear_vehiculo(api, headers, placa="VEH-001", capacidad=500):
    res = await api.client.post(
        "/api/vehiculos/",
        json={"placa": placa, "capacidad_kg": capacidad, "tipo_combustible": "DIESEL"},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    return res.json()["vehiculo_id"]


async def _crear_pedido(api, headers, bodega_id, peso=10):
    res = await api.client.post("/api/pedidos/", json=_pedido(bodega_id, peso), headers=headers)
    assert res.status_code == 201, res.text
    return res.json()["pedido_id"]


# ── Vehículos ─────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_vehiculo_consulta_por_id_y_404(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    vid = await _crear_vehiculo(api, admin)

    ok = await api.client.get(f"/api/vehiculos/{vid}", headers=operador)
    assert ok.status_code == 200
    assert ok.json()["placa"] == "VEH-001"

    faltante = await api.client.get("/api/vehiculos/no-existe", headers=operador)
    assert faltante.status_code == 404


@pytest.mark.asyncio
async def test_vehiculo_conteo_por_estado(api):
    admin = await _login(api.client, "admin@test.pe")
    vid = await _crear_vehiculo(api, admin, "VEH-001")
    await _crear_vehiculo(api, admin, "VEH-002")
    await api.client.delete(f"/api/vehiculos/{vid}", headers=admin)

    res = await api.client.get("/api/vehiculos/count", headers=admin)
    assert res.status_code == 200
    assert res.json() == {"DISPONIBLE": 1, "FUERA_DE_SERVICIO": 1, "TOTAL": 2}


@pytest.mark.asyncio
async def test_vehiculo_actualizacion_ok_404_y_placa_duplicada(api):
    admin = await _login(api.client, "admin@test.pe")
    vid = await _crear_vehiculo(api, admin, "VEH-001")
    await _crear_vehiculo(api, admin, "VEH-002")

    ok = await api.client.put(f"/api/vehiculos/{vid}", json={"capacidad_kg": 900}, headers=admin)
    assert ok.status_code == 200
    assert float(ok.json()["capacidad_kg"]) == 900

    dup = await api.client.put(f"/api/vehiculos/{vid}", json={"placa": "VEH-002"}, headers=admin)
    assert dup.status_code == 409

    faltante = await api.client.put("/api/vehiculos/no-existe", json={"capacidad_kg": 1}, headers=admin)
    assert faltante.status_code == 404


@pytest.mark.asyncio
async def test_vehiculo_baja_de_inexistente_devuelve_404(api):
    admin = await _login(api.client, "admin@test.pe")
    res = await api.client.delete("/api/vehiculos/no-existe", headers=admin)
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_vehiculo_operador_solo_lectura(api):
    operador = await _login(api.client, "operador@test.pe")
    res = await api.client.post(
        "/api/vehiculos/",
        json={"placa": "OPE-001", "capacidad_kg": 100, "tipo_combustible": "DIESEL"},
        headers=operador,
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_vehiculo_listado_requiere_autenticacion(api):
    res = await api.client.get("/api/vehiculos/")
    assert res.status_code in (401, 403)


# ── Pedidos ───────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_pedido_consulta_por_id_y_404(api):
    operador = await _login(api.client, "operador@test.pe")
    pid = await _crear_pedido(api, operador, api.bodega_a)

    ok = await api.client.get(f"/api/pedidos/{pid}", headers=operador)
    assert ok.status_code == 200
    assert ok.json()["estado"] == "PENDIENTE"

    faltante = await api.client.get("/api/pedidos/no-existe", headers=operador)
    assert faltante.status_code == 404


@pytest.mark.asyncio
async def test_pedido_bodega_solo_ve_el_propio(api):
    operador = await _login(api.client, "operador@test.pe")
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    propio = await _crear_pedido(api, operador, api.bodega_a)
    ajeno = await _crear_pedido(api, operador, api.bodega_b)

    assert (await api.client.get(f"/api/pedidos/{propio}", headers=bodega_a)).status_code == 200
    assert (await api.client.get(f"/api/pedidos/{ajeno}", headers=bodega_a)).status_code == 403


@pytest.mark.asyncio
async def test_pedido_listado_con_filtros_de_estado_y_bodega(api):
    operador = await _login(api.client, "operador@test.pe")
    pid = await _crear_pedido(api, operador, api.bodega_a)
    await _crear_pedido(api, operador, api.bodega_b)
    await api.client.delete(f"/api/pedidos/{pid}", headers=operador)

    cancelados = await api.client.get("/api/pedidos/?estado=cancelado", headers=operador)
    assert [p["pedido_id"] for p in cancelados.json()] == [pid]

    de_b = await api.client.get(f"/api/pedidos/?bodega_id={api.bodega_b}", headers=operador)
    assert {p["bodega_id"] for p in de_b.json()} == {api.bodega_b}


@pytest.mark.asyncio
async def test_pedido_listado_de_usuario_bodega_sin_bodega_es_vacio(api):
    # Un usuario BODEGA recién registrado todavía no tiene bodega asociada.
    await api.client.post(
        "/api/auth/register",
        json={"nombre": "Sin Bodega", "email": "sinbodega@test.pe", "password": "Clave12345", "rol": "BODEGA"},
    )
    login = await api.client.post(
        "/api/auth/login", json={"email": "sinbodega@test.pe", "password": "Clave12345"}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    res = await api.client.get("/api/pedidos/", headers=headers)
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_pedido_conteo_por_estado(api):
    operador = await _login(api.client, "operador@test.pe")
    pid = await _crear_pedido(api, operador, api.bodega_a)
    await _crear_pedido(api, operador, api.bodega_a)
    await api.client.delete(f"/api/pedidos/{pid}", headers=operador)

    res = await api.client.get("/api/pedidos/count", headers=operador)
    assert res.status_code == 200
    assert res.json() == {"PENDIENTE": 1, "CANCELADO": 1, "TOTAL": 2}


@pytest.mark.asyncio
async def test_pedido_actualizacion_ok_y_404(api):
    operador = await _login(api.client, "operador@test.pe")
    pid = await _crear_pedido(api, operador, api.bodega_a)

    ok = await api.client.put(f"/api/pedidos/{pid}", json={"direccion": "Jr. Nuevo 456, Ate"}, headers=operador)
    assert ok.status_code == 200
    assert ok.json()["direccion"] == "Jr. Nuevo 456, Ate"

    faltante = await api.client.put("/api/pedidos/no-existe", json={"direccion": "Sin pedido"}, headers=operador)
    assert faltante.status_code == 404


@pytest.mark.asyncio
async def test_pedido_bodega_no_puede_actualizar(api):
    operador = await _login(api.client, "operador@test.pe")
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    pid = await _crear_pedido(api, operador, api.bodega_a)

    res = await api.client.put(f"/api/pedidos/{pid}", json={"direccion": "Otra dirección"}, headers=bodega_a)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_pedido_cancelacion_logica_y_rechazo_de_doble_cancelacion(api):
    operador = await _login(api.client, "operador@test.pe")
    pid = await _crear_pedido(api, operador, api.bodega_a)

    primera = await api.client.delete(f"/api/pedidos/{pid}", headers=operador)
    assert primera.status_code == 200

    segunda = await api.client.delete(f"/api/pedidos/{pid}", headers=operador)
    assert segunda.status_code == 400

    conservado = await api.client.get(f"/api/pedidos/{pid}", headers=operador)
    assert conservado.json()["estado"] == "CANCELADO"

    faltante = await api.client.delete("/api/pedidos/no-existe", headers=operador)
    assert faltante.status_code == 404


@pytest.mark.asyncio
async def test_pedido_con_bodega_inexistente_se_asocia_a_la_primera_registrada(api):
    operador = await _login(api.client, "operador@test.pe")
    res = await api.client.post("/api/pedidos/", json=_pedido("bodega-que-no-existe", 10), headers=operador)
    assert res.status_code == 201
    assert res.json()["bodega_id"] in {api.bodega_a, api.bodega_b}


@pytest.mark.asyncio
async def test_pedido_con_ventana_invalida_es_rechazado(api):
    operador = await _login(api.client, "operador@test.pe")
    pedido = _pedido(api.bodega_a, 10)
    pedido["ventana_fin"] = pedido["ventana_inicio"]
    res = await api.client.post("/api/pedidos/", json=pedido, headers=operador)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_pedido_de_bodega_sin_bodega_id_se_asocia_a_su_propia_bodega(api):
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    pedido = _pedido(api.bodega_a, 10)
    del pedido["bodega_id"]

    res = await api.client.post("/api/pedidos/", json=pedido, headers=bodega_a)
    assert res.status_code == 201
    assert res.json()["bodega_id"] == api.bodega_a
