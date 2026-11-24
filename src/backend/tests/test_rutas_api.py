"""
Pruebas de integración de la API de rutas, indicadores, CO₂ y reportes (RF-003, RF-004, RF-005, RF-006, RF-010).

Usan la base real en memoria y los roles reales del fixture `api` (ADMIN_FLOTA, OPERADOR, BODEGA); el rol AUDITOR
se crea por la propia API, como lo haría un administrador.
"""

from datetime import datetime, timedelta, timezone

import pytest
from app.routers.reportes_router import texto_seguro

from tests.utilidades import _login

AHORA = datetime.now(timezone.utc)


def _pedido(bodega_id, peso_kg, lat=-12.04, lng=-77.00, direccion="Jr. Los Pinos 123, El Agustino"):
    return {
        "bodega_id": bodega_id, "direccion": direccion, "latitud": lat, "longitud": lng, "peso_kg": peso_kg,
        "ventana_inicio": AHORA.isoformat(), "ventana_fin": (AHORA + timedelta(hours=6)).isoformat(),
    }


async def _vehiculo(api, admin, placa, capacidad, combustible="DIESEL"):
    res = await api.client.post(
        "/api/vehiculos/", json={"placa": placa, "capacidad_kg": capacidad, "tipo_combustible": combustible}, headers=admin,
    )
    assert res.status_code == 201, res.text
    return res.json()["vehiculo_id"]


async def _pedidos(api, operador, cantidad, peso=100.0):
    ids = []
    for i in range(cantidad):
        res = await api.client.post(
            "/api/pedidos/",
            json=_pedido(api.bodega_a, peso, lat=-12.04 - i * 0.01, lng=-77.00 - i * 0.01, direccion=f"Av. Prueba {i} 100"),
            headers=operador,
        )
        assert res.status_code == 201, res.text
        ids.append(res.json()["pedido_id"])
    return ids


async def _auditor(api, admin):
    res = await api.client.post(
        "/api/auth/register",
        json={"nombre": "Auditor", "email": "auditor@test.pe", "password": "Clave12345", "rol": "AUDITOR"},
        headers=admin,
    )
    assert res.status_code == 201, res.text
    login = await api.client.post("/api/auth/login", json={"email": "auditor@test.pe", "password": "Clave12345"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _escenario(api, vehiculos=(("ABC-123", 1500), ("DEF-456", 2000)), pedidos=4):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    for placa, capacidad in vehiculos:
        await _vehiculo(api, admin, placa, capacidad)
    await _pedidos(api, operador, pedidos)
    return admin, operador


# ── Optimizar (RF-003) ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_optimizar_sin_pedidos_pendientes_responde_409(api):
    operador = await _login(api.client, "operador@test.pe")
    res = await api.client.post("/api/rutas/optimizar", headers=operador)
    assert res.status_code == 409
    assert "pendientes" in res.json()["detail"]


@pytest.mark.asyncio
async def test_optimizar_planifica_los_pedidos_y_los_marca_asignados(api):
    admin, operador = await _escenario(api)
    res = await api.client.post("/api/rutas/optimizar", json={"limite_segundos": 5}, headers=operador)
    assert res.status_code == 201, res.text
    plan = res.json()
    assert plan["pedidos_planificados"] == 4 and plan["pedidos_sin_asignar"] == 0 and plan["sin_asignar"] == []
    assert plan["algoritmo"] == "Clarke-Wright + 2-opt"
    assert plan["tiempo_ms"] < 45000 and plan["limite_alcanzado"] is False
    assert sum(len(r["paradas"]) for r in plan["rutas"]) == 4
    assert plan["distancia_km"] <= plan["distancia_base_km"]
    assert plan["co2_evitado_kg"] >= 0 and plan["arboles_equivalentes"] >= 0
    for ruta in plan["rutas"]:
        assert ruta["estado"] == "PLANIFICADA" and ruta["carga_kg"] <= ruta["capacidad_kg"]
        assert [p["orden"] for p in ruta["paradas"]] == list(range(1, len(ruta["paradas"]) + 1))

    asignados = await api.client.get("/api/pedidos/?estado=ASIGNADO", headers=operador)
    assert asignados.headers["X-Total-Count"] == "4"

    # Con todos los pedidos asignados no hay nada más que planificar.
    otra = await api.client.post("/api/rutas/optimizar", headers=operador)
    assert otra.status_code == 409


@pytest.mark.asyncio
async def test_listar_rutas_entrega_el_deposito_y_las_paradas_para_el_mapa(api):
    admin, operador = await _escenario(api)
    await api.client.post("/api/rutas/optimizar", headers=operador)
    res = await api.client.get("/api/rutas/", headers=operador)
    assert res.status_code == 200
    datos = res.json()
    assert datos["deposito"] == {"latitud": -12.0464, "longitud": -77.0428}
    assert len(datos["rutas"]) >= 1
    parada = datos["rutas"][0]["paradas"][0]
    assert {"latitud", "longitud", "direccion", "orden", "pedido_id"} <= parada.keys()


@pytest.mark.asyncio
async def test_pedido_sin_vehiculo_libre_se_informa_con_su_motivo(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1000),), pedidos=0)
    for i in range(3):
        res = await api.client.post(
            "/api/pedidos/", json=_pedido(api.bodega_a, 700.0, lat=-12.05 - i * 0.02, direccion=f"Calle Pesada {i} 5"),
            headers=operador,
        )
        assert res.status_code == 201
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    assert len(plan["rutas"]) == 1 and plan["pedidos_planificados"] == 1
    assert plan["pedidos_sin_asignar"] == 2
    assert all("vehículos" in item["motivo"] for item in plan["sin_asignar"])
    pendientes = await api.client.get("/api/pedidos/?estado=PENDIENTE", headers=operador)
    assert pendientes.headers["X-Total-Count"] == "2"


@pytest.mark.asyncio
async def test_optimizar_sin_vehiculos_disponibles_deja_todo_sin_asignar(api):
    operador = await _login(api.client, "operador@test.pe")
    admin = await _login(api.client, "admin@test.pe")
    await _vehiculo(api, admin, "ABC-123", 1500)
    await _pedidos(api, operador, 2)
    # Se retira el único vehículo de la flota disponible.
    flota = (await api.client.get("/api/vehiculos/", headers=admin)).json()
    await api.client.delete(f"/api/vehiculos/{flota[0]['vehiculo_id']}", headers=admin)
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    assert plan["rutas"] == [] and plan["pedidos_sin_asignar"] == 2


@pytest.mark.asyncio
async def test_roles_sin_permiso_no_pueden_optimizar_ni_ver_rutas(api):
    await _escenario(api)
    bodega = await _login(api.client, "bodega.a@test.pe")
    assert (await api.client.post("/api/rutas/optimizar", headers=bodega)).status_code == 403
    assert (await api.client.get("/api/rutas/", headers=bodega)).status_code == 403
    assert (await api.client.post("/api/rutas/optimizar")).status_code == 401


@pytest.mark.asyncio
async def test_el_auditor_consulta_pero_no_optimiza(api):
    admin, operador = await _escenario(api)
    auditor = await _auditor(api, admin)
    assert (await api.client.post("/api/rutas/optimizar", headers=auditor)).status_code == 403
    await api.client.post("/api/rutas/optimizar", headers=operador)
    assert (await api.client.get("/api/rutas/", headers=auditor)).status_code == 200
    assert (await api.client.get("/api/indicadores/resumen", headers=auditor)).status_code == 200


@pytest.mark.asyncio
async def test_limite_de_calculo_fuera_de_rango_se_rechaza(api):
    operador = await _login(api.client, "operador@test.pe")
    assert (await api.client.post("/api/rutas/optimizar", json={"limite_segundos": 60}, headers=operador)).status_code == 422
    assert (await api.client.post("/api/rutas/optimizar", json={"limite_segundos": 0}, headers=operador)).status_code == 422


# ── Cancelar una ruta ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cancelar_ruta_libera_el_vehiculo_y_devuelve_los_pedidos(api):
    admin, operador = await _escenario(api)
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    ruta = plan["rutas"][0]

    res = await api.client.post(f"/api/rutas/{ruta['ruta_id']}/cancelar", headers=operador)
    assert res.status_code == 200 and "vuelven a PENDIENTE" in res.json()["mensaje"]
    pendientes = await api.client.get("/api/pedidos/?estado=PENDIENTE", headers=operador)
    assert int(pendientes.headers["X-Total-Count"]) == len(ruta["paradas"])

    assert (await api.client.post(f"/api/rutas/{ruta['ruta_id']}/cancelar", headers=operador)).status_code == 400
    assert (await api.client.post("/api/rutas/no-existe/cancelar", headers=operador)).status_code == 404

    # Los pedidos liberados y el vehículo libre se pueden planificar de nuevo.
    nuevo = await api.client.post("/api/rutas/optimizar", headers=operador)
    assert nuevo.status_code == 201 and nuevo.json()["pedidos_planificados"] == len(ruta["paradas"])


# ── Indicadores (RF-005) y carbono (RF-010) ──────────────────────────────

@pytest.mark.asyncio
async def test_indicadores_sin_actividad_estan_en_cero(api):
    admin = await _login(api.client, "admin@test.pe")
    res = await api.client.get("/api/indicadores/resumen", headers=admin)
    assert res.status_code == 200
    datos = res.json()
    assert datos["rutas_activas"] == 0 and datos["optimizaciones"] == 0
    assert datos["co2_evitado_kg"] == 0 and datos["arboles_equivalentes"] == 0
    assert datos["pedidos_en_ventana_pct"] is None
    assert datos["vehiculos"]["TOTAL"] == 0 and datos["pedidos"]["TOTAL"] == 0


@pytest.mark.asyncio
async def test_indicadores_reflejan_la_flota_los_pedidos_y_el_co2_evitado(api):
    admin, operador = await _escenario(api)
    await api.client.post("/api/rutas/optimizar", headers=operador)
    datos = (await api.client.get("/api/indicadores/resumen", headers=admin)).json()
    assert datos["vehiculos"]["DISPONIBLE"] == 2 and datos["vehiculos"]["TOTAL"] == 2
    assert datos["pedidos"]["ASIGNADO"] == 4 and datos["pedidos"]["TOTAL"] == 4
    assert datos["rutas_activas"] >= 1 and datos["optimizaciones"] == 1
    assert datos["distancia_planificada_km"] > 0 and datos["co2_planificado_kg"] > 0
    assert datos["co2_evitado_kg"] >= 0 and datos["ahorro_co2_pct"] >= 0 and datos["ahorro_km_pct"] > 0
    assert datos["pedidos_en_ventana_pct"] is not None and 0 <= datos["pedidos_en_ventana_pct"] <= 100
    bodega = await _login(api.client, "bodega.a@test.pe")
    assert (await api.client.get("/api/indicadores/resumen", headers=bodega)).status_code == 403


# ── Reportes exportables (RF-006) ────────────────────────────────────────

@pytest.mark.asyncio
async def test_reporte_de_pedidos_es_csv_con_bom_y_encabezados(api):
    admin, operador = await _escenario(api, pedidos=3)
    res = await api.client.get("/api/reportes/pedidos.csv", headers=admin)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    assert 'filename="pedidos.csv"' in res.headers["content-disposition"]
    cuerpo = res.content.decode("utf-8")
    assert cuerpo.startswith("﻿")
    filas = cuerpo.lstrip("﻿").strip().split("\r\n")
    assert filas[0].startswith("pedido_id,direccion,latitud,longitud,peso_kg")
    assert len(filas) == 1 + 3


@pytest.mark.asyncio
async def test_csv_neutraliza_formulas_pero_no_altera_los_numeros(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await _vehiculo(api, admin, "ABC-123", 1500)
    res = await api.client.post(
        "/api/pedidos/", json=_pedido(api.bodega_a, 50.0, direccion="=HYPERLINK(\"http://x\",\"clic\")"), headers=operador,
    )
    assert res.status_code == 201
    cuerpo = (await api.client.get("/api/reportes/pedidos.csv", headers=admin)).content.decode("utf-8")
    assert "'=HYPERLINK" in cuerpo and ",=HYPERLINK" not in cuerpo
    assert ",-12.04," in cuerpo  # la latitud negativa no se prefija


def test_texto_seguro_prefija_solo_los_caracteres_peligrosos():
    assert texto_seguro("=SUMA(A1)") == "'=SUMA(A1)"
    assert texto_seguro("+cmd") == "'+cmd" and texto_seguro("-1") == "'-1" and texto_seguro("@x") == "'@x"
    assert texto_seguro("Av. Lima") == "Av. Lima"
    assert texto_seguro(None) == ""


@pytest.mark.asyncio
async def test_reportes_de_rutas_y_ambiental_incluyen_el_plan(api):
    admin, operador = await _escenario(api)
    await api.client.post("/api/rutas/optimizar", headers=operador)

    rutas = (await api.client.get("/api/reportes/rutas.csv", headers=operador)).content.decode("utf-8")
    lineas = rutas.lstrip("﻿").strip().split("\r\n")
    assert lineas[0].startswith("ruta_id,placa,combustible,estado_ruta,orden,pedido_id")
    assert len(lineas) == 1 + 4  # una fila por parada
    assert "PLANIFICADA" in rutas

    ambiental = (await api.client.get("/api/reportes/ambiental.csv", headers=admin)).content.decode("utf-8")
    lineas = ambiental.lstrip("﻿").strip().split("\r\n")
    assert lineas[0].startswith("optimizacion_id,fecha,algoritmo,pedidos_planificados")
    assert len(lineas) == 2 and "Clarke-Wright + 2-opt" in lineas[1]


@pytest.mark.asyncio
async def test_los_reportes_exigen_un_rol_autorizado(api):
    bodega = await _login(api.client, "bodega.a@test.pe")
    for ruta in ("pedidos", "rutas", "ambiental"):
        assert (await api.client.get(f"/api/reportes/{ruta}.csv", headers=bodega)).status_code == 403
        assert (await api.client.get(f"/api/reportes/{ruta}.csv")).status_code == 401
