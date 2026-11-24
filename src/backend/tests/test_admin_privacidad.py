"""
Pruebas de administración (RF-008), privacidad y cifrado (RNF-008, RN-008), reportes (RF-006), filtros del dashboard
(RF-005), zonas protegidas (RN-003) y disponibilidad (RNF-003).
"""

import io
import zipfile
from datetime import datetime, timezone

import pytest
from app import database
from app.cifrado import cifrar, descifrar, esta_cifrado
from app.models import Pedido
from sqlalchemy import text

from tests.test_ciclo_ruta import EVIDENCIA, _crear_conductor, _ruta_lista
from tests.test_rutas_api import _auditor, _escenario, _pedido, _vehiculo
from tests.utilidades import _login

# ── Cifrado en reposo (RNF-008) ──────────────────────────────────────────

def test_cifrado_es_reversible_determinista_y_lleva_prefijo():
    valor = cifrar("Av. Los Álamos 123")
    assert esta_cifrado(valor) and valor.startswith("enc1:") and "Álamos" not in valor
    assert descifrar(valor) == "Av. Los Álamos 123"
    assert cifrar("Av. Los Álamos 123") == valor  # determinista: permite igualdad y unicidad
    assert descifrar("dato sin cifrar") == "dato sin cifrar"  # dato anterior al cifrado
    assert not esta_cifrado(None) and not esta_cifrado("texto")


@pytest.mark.asyncio
async def test_los_datos_personales_se_guardan_cifrados_en_la_base(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=1)
    await _crear_conductor(api, admin)
    async with database.AsyncSessionLocal() as sesion:
        usuarios = (await sesion.execute(text("SELECT nombre, email, telefono FROM usuarios"))).all()
        assert usuarios and all(esta_cifrado(u[0]) and esta_cifrado(u[1]) for u in usuarios)
        assert any(u[2] and esta_cifrado(u[2]) for u in usuarios)
        conductor = (await sesion.execute(text("SELECT licencia, telefono FROM conductores"))).one()
        assert esta_cifrado(conductor[0]) and esta_cifrado(conductor[1])
        pedido = (await sesion.execute(text("SELECT direccion, latitud, longitud FROM pedidos"))).one()
        assert all(esta_cifrado(c) for c in pedido)
        bodega = (await sesion.execute(text("SELECT direccion_referencial, latitud, longitud FROM bodegas"))).first()
        assert all(esta_cifrado(c) for c in bodega)
    # Por la API los datos se leen en claro y el inicio de sesión por correo sigue funcionando.
    assert (await _login(api.client, "admin@test.pe"))
    pedidos = (await api.client.get("/api/pedidos/", headers=operador)).json()
    assert pedidos[0]["direccion"].startswith("Av. Prueba") and float(pedidos[0]["latitud"]) < 0


@pytest.mark.asyncio
async def test_la_busqueda_por_direccion_funciona_sobre_datos_cifrados(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=3)
    res = await api.client.get("/api/pedidos/?q=prueba 1", headers=operador)
    assert res.status_code == 200 and res.headers["x-total-count"] == "1"
    assert res.json()[0]["direccion"] == "Av. Prueba 1 100"


# ── Usuarios y conductores (administración) ──────────────────────────────

@pytest.mark.asyncio
async def test_crud_de_conductores_y_baja_logica(api):
    admin = await _login(api.client, "admin@test.pe")
    conductor_id, _ = await _crear_conductor(api, admin)
    repetido = await api.client.post("/api/admin/conductores", json={
        "nombre": "Otro", "email": "otro@test.pe", "password": "Clave12345", "licencia": "Q12345678",
    }, headers=admin)
    assert repetido.status_code == 409
    editado = await api.client.put(
        f"/api/admin/conductores/{conductor_id}", json={"telefono": "+51911111111", "nombre": "Chofer Renombrado"}, headers=admin,
    )
    assert editado.status_code == 200 and editado.json()["nombre"] == "Chofer Renombrado"
    assert (await api.client.delete(f"/api/admin/conductores/{conductor_id}", headers=admin)).status_code == 200
    lista = (await api.client.get("/api/admin/conductores", headers=admin)).json()
    assert lista[0]["activo"] is False
    operador = await _login(api.client, "operador@test.pe")
    assert (await api.client.get("/api/admin/conductores", headers=operador)).status_code == 200  # el operador asigna rutas
    assert (await api.client.delete(f"/api/admin/conductores/{conductor_id}", headers=operador)).status_code == 403


@pytest.mark.asyncio
async def test_no_se_desactiva_un_conductor_con_ruta_abierta(api):
    admin, _, _, ruta = await _ruta_lista(api, iniciar=False)
    lista = (await api.client.get("/api/admin/conductores", headers=admin)).json()
    res = await api.client.delete(f"/api/admin/conductores/{lista[0]['conductor_id']}", headers=admin)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_eliminacion_fisica_exige_confirmacion_y_se_rechaza_con_historial(api):
    admin = await _login(api.client, "admin@test.pe")
    nuevo = (await api.client.post("/api/auth/register", json={
        "nombre": "Auditor Temporal", "email": "temporal@test.pe", "password": "Clave12345", "rol": "AUDITOR",
    }, headers=admin)).json()
    assert (await api.client.delete(f"/api/admin/usuarios/{nuevo['usuario_id']}", headers=admin)).status_code == 400
    assert (await api.client.delete(
        f"/api/admin/usuarios/{nuevo['usuario_id']}?confirmar=true", headers=admin,
    )).status_code == 200
    assert (await api.client.delete(
        f"/api/admin/usuarios/{nuevo['usuario_id']}?confirmar=true", headers=admin,
    )).status_code == 404
    propio = (await api.client.get("/api/auth/me", headers=admin)).json()["usuario_id"]
    assert (await api.client.delete(f"/api/admin/usuarios/{propio}?confirmar=true", headers=admin)).status_code == 409
    # Una bodega con pedidos conserva su historial: corresponde anonimizar.
    operador = await _login(api.client, "operador@test.pe")
    await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 50), headers=operador)
    bodega = (await api.client.get("/api/auth/me", headers=await _login(api.client, "bodega.a@test.pe"))).json()
    res = await api.client.delete(f"/api/admin/usuarios/{bodega['usuario_id']}?confirmar=true", headers=admin)
    assert res.status_code == 409 and "anonimiza" in res.json()["detail"]


@pytest.mark.asyncio
async def test_el_administrador_no_puede_cambiarse_el_propio_rol(api):
    admin = await _login(api.client, "admin@test.pe")
    yo = (await api.client.get("/api/auth/me", headers=admin)).json()["usuario_id"]
    assert (await api.client.put(f"/api/admin/usuarios/{yo}", json={"rol": "AUDITOR"}, headers=admin)).status_code == 409
    res = await api.client.put(f"/api/admin/usuarios/{yo}", json={"nombre": "Nombre Nuevo", "password": "NuevaClave123"}, headers=admin)
    assert res.status_code == 200 and res.json()["nombre"] == "Nombre Nuevo"
    assert (await api.client.post(
        "/api/auth/login", json={"email": "admin@test.pe", "password": "NuevaClave123"},
    )).status_code == 200


# ── Parámetros del algoritmo y zonas protegidas ──────────────────────────

@pytest.mark.asyncio
async def test_parametros_del_algoritmo_se_guardan_y_cambian_el_resultado(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=3)
    por_defecto = (await api.client.get("/api/admin/parametros", headers=admin)).json()
    assert por_defecto["velocidad_kmh"] == 25 and por_defecto["servicio_min"] == 10
    rapido = {"velocidad_kmh": 60, "servicio_min": 2, "limite_segundos": 30}
    assert (await api.client.put("/api/admin/parametros", json=rapido, headers=admin)).status_code == 200
    assert (await api.client.get("/api/admin/parametros", headers=admin)).json() == {**rapido, "algoritmo": "clarke_wright_2opt"}
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    assert plan["rutas"][0]["duracion_min"] < 120
    assert plan["algoritmo"] == "Clarke-Wright + 2-opt"
    fuera = await api.client.put("/api/admin/parametros", json={**rapido, "velocidad_kmh": 500}, headers=admin)
    assert fuera.status_code == 422
    assert (await api.client.put("/api/admin/parametros", json=rapido, headers=operador)).status_code == 403


@pytest.mark.asyncio
async def test_una_zona_protegida_deja_sin_asignar_los_destinos_dentro_de_la_reserva(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await _vehiculo(api, admin, "ABC-123", 1500)
    zona = await api.client.post(
        "/api/admin/zonas", json={"nombre": "Reserva de prueba", "latitud": -12.04, "longitud": -77.0, "radio_km": 1.0}, headers=admin,
    )
    assert zona.status_code == 201
    assert (await api.client.post(
        "/api/admin/zonas", json={"nombre": "Reserva de prueba", "latitud": 0, "longitud": 0, "radio_km": 1}, headers=admin,
    )).status_code == 409
    dentro = _pedido(api.bodega_a, 50, lat=-12.04, lng=-77.0, direccion="Dentro de la reserva")
    fuera = _pedido(api.bodega_a, 50, lat=-12.06, lng=-77.04, direccion="Fuera de la reserva")
    for p in (dentro, fuera):
        assert (await api.client.post("/api/pedidos/", json=p, headers=operador)).status_code == 201
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    assert plan["pedidos_planificados"] == 1 and "dentro de la zona protegida" in plan["sin_asignar"][0]["motivo"]
    zonas = (await api.client.get("/api/admin/zonas", headers=operador)).json()
    assert (await api.client.delete(f"/api/admin/zonas/{zonas[0]['zona_id']}", headers=admin)).status_code == 200
    assert (await api.client.delete(f"/api/admin/zonas/{zonas[0]['zona_id']}", headers=admin)).status_code == 404


# ── Privacidad: anonimización en 5 días hábiles (RN-008) ──────────────────

@pytest.mark.asyncio
async def test_solicitud_de_privacidad_anonimiza_los_datos_del_titular(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=2)
    bodega = await _login(api.client, "bodega.a@test.pe")
    solicitud = (await api.client.post("/api/privacidad/solicitudes", headers=bodega)).json()
    repetida = (await api.client.post("/api/privacidad/solicitudes", headers=bodega)).json()
    assert repetida["solicitud_id"] == solicitud["solicitud_id"]  # no se duplica una solicitud pendiente
    plazo = datetime.fromisoformat(solicitud["plazo_limite"])
    inicio = datetime.fromisoformat(solicitud["solicitada_en"])
    assert (plazo.date() - inicio.date()).days >= 5 and plazo.isoweekday() <= 5  # 5 días hábiles

    assert (await api.client.get("/api/privacidad/solicitudes", headers=bodega)).status_code == 403
    pendientes = (await api.client.get("/api/privacidad/solicitudes", headers=admin)).json()
    assert pendientes[0]["estado"] == "PENDIENTE"
    atendida = await api.client.post(f"/api/privacidad/solicitudes/{solicitud['solicitud_id']}/atender", headers=admin)
    assert atendida.status_code == 200 and atendida.json()["estado"] == "ATENDIDA"
    assert (await api.client.post(
        f"/api/privacidad/solicitudes/{solicitud['solicitud_id']}/atender", headers=admin,
    )).status_code == 409

    # La cuenta queda cerrada y sus datos sin información personal ni geolocalización.
    assert (await api.client.post(
        "/api/auth/login", json={"email": "bodega.a@test.pe", "password": "BodegaA2026!"},
    )).status_code == 401
    async with database.AsyncSessionLocal() as sesion:
        filas = (await sesion.execute(
            text("SELECT direccion FROM pedidos")
        )).scalars().all()
        assert all(descifrar(d) == "Dato anonimizado" for d in filas)
        estados = (await sesion.execute(text("SELECT estado FROM pedidos"))).scalars().all()
        assert set(estados) == {"CANCELADO"}
    usuarios = (await api.client.get("/api/admin/usuarios", headers=admin)).json()
    anonimo = next(u for u in usuarios if u["estado"] == "ANONIMIZADO")
    assert anonimo["nombre"] == "Usuario anonimizado" and anonimo["email"].endswith("@anonimizado.invalid")


@pytest.mark.asyncio
async def test_el_administrador_no_atiende_su_propia_solicitud(api):
    admin = await _login(api.client, "admin@test.pe")
    solicitud = (await api.client.post("/api/privacidad/solicitudes", headers=admin)).json()
    res = await api.client.post(f"/api/privacidad/solicitudes/{solicitud['solicitud_id']}/atender", headers=admin)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_anonimizar_a_un_conductor_borra_licencia_y_ubicaciones_de_entrega(api):
    admin, operador, chofer, ruta = await _ruta_lista(api, pedidos=1)
    await api.client.post(f"/api/conductor/paradas/{ruta['paradas'][0]['parada_id']}/entregar", json=EVIDENCIA, headers=chofer)
    solicitud = (await api.client.post("/api/privacidad/solicitudes", headers=chofer)).json()
    assert (await api.client.post(
        f"/api/privacidad/solicitudes/{solicitud['solicitud_id']}/atender", headers=admin,
    )).status_code == 200
    async with database.AsyncSessionLocal() as sesion:
        licencia = (await sesion.execute(text("SELECT licencia FROM conductores"))).scalar_one()
        assert descifrar(licencia).startswith("ANON-")
        parada = (await sesion.execute(text("SELECT latitud_entrega, longitud_entrega FROM ruta_paradas"))).one()
        assert parada == (None, None)


# ── Reportes en Excel y PDF, sin datos personales para el auditor ─────────

@pytest.mark.asyncio
async def test_los_reportes_se_exportan_en_excel_y_pdf(api):
    admin, operador = await _escenario(api, pedidos=3)
    await api.client.post("/api/rutas/optimizar", headers=operador)
    for reporte in ("pedidos", "rutas", "ambiental"):
        xlsx = await api.client.get(f"/api/reportes/{reporte}.xlsx", headers=admin)
        assert xlsx.status_code == 200 and "spreadsheetml" in xlsx.headers["content-type"]
        libro = zipfile.ZipFile(io.BytesIO(xlsx.content))
        hoja = libro.read("xl/worksheets/sheet1.xml").decode("utf-8")
        assert libro.testzip() is None and "<row r=\"2\">" in hoja
        pdf = await api.client.get(f"/api/reportes/{reporte}.pdf", headers=admin)
        assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-1.4") and pdf.content.rstrip().endswith(b"%%EOF")
    assert (await api.client.get("/api/reportes/inexistente.pdf", headers=admin)).status_code == 422
    assert (await api.client.get("/api/reportes/pedidos.docx", headers=admin)).status_code == 422


@pytest.mark.asyncio
async def test_el_xlsx_neutraliza_formulas(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await _vehiculo(api, admin, "ABC-123", 1500)
    await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 50, direccion="=CMD|' /C calc'!A0"), headers=operador)
    xlsx = await api.client.get("/api/reportes/pedidos.xlsx", headers=admin)
    hoja = zipfile.ZipFile(io.BytesIO(xlsx.content)).read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert "'=CMD" in hoja and ">=CMD" not in hoja


@pytest.mark.asyncio
async def test_el_auditor_recibe_los_reportes_sin_datos_personales_ni_geolocalizacion(api):
    admin, operador = await _escenario(api, pedidos=3)
    await api.client.post("/api/rutas/optimizar", headers=operador)
    auditor = await _auditor(api, admin)
    for reporte in ("pedidos", "rutas"):
        cuerpo = (await api.client.get(f"/api/reportes/{reporte}.csv", headers=auditor)).content.decode("utf-8")
        encabezado = cuerpo.lstrip("﻿").split("\r\n")[0]
        assert "direccion" not in encabezado and "latitud" not in encabezado and "longitud" not in encabezado
        assert "distrito" in encabezado and "Av. Prueba" not in cuerpo
    completo = (await api.client.get("/api/reportes/pedidos.csv", headers=admin)).content.decode("utf-8")
    assert "direccion" in completo and "Av. Prueba" in completo
    pdf = (await api.client.get("/api/reportes/pedidos.pdf", headers=auditor)).content
    assert b"Av. Prueba" not in pdf and b"Sin datos personales" in pdf


# ── Filtros del dashboard por distrito y fechas (RF-005) ──────────────────

@pytest.mark.asyncio
async def test_el_dashboard_se_filtra_por_distrito_y_fecha(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await _vehiculo(api, admin, "ABC-123", 1500)
    for i, distrito in enumerate(("Ate", "Ate", "Santa Anita")):
        cuerpo = {**_pedido(api.bodega_a, 50, direccion=f"Calle {i} 10"), "distrito": distrito}
        assert (await api.client.post("/api/pedidos/", json=cuerpo, headers=operador)).status_code == 201
    await api.client.post("/api/rutas/optimizar", headers=operador)
    todos = (await api.client.get("/api/indicadores/resumen", headers=admin)).json()
    ate = (await api.client.get("/api/indicadores/resumen?distrito=Ate", headers=admin)).json()
    anita = (await api.client.get("/api/indicadores/resumen?distrito=Santa Anita", headers=admin)).json()
    assert todos["pedidos"]["TOTAL"] == 3 and ate["pedidos"]["TOTAL"] == 2 and anita["pedidos"]["TOTAL"] == 1
    assert ate["distrito"] == "Ate" and ate["combustible_ahorrado_litros"] >= 0
    futuro = (await api.client.get("/api/indicadores/resumen?desde=2099-01-01T00:00:00", headers=admin)).json()
    assert futuro["pedidos"]["TOTAL"] == 0 and futuro["rutas_activas"] == 0
    lista = (await api.client.get("/api/pedidos/?distrito=Ate", headers=operador)).json()
    assert len(lista) == 2
    rutas_ate = (await api.client.get("/api/reportes/rutas.csv?distrito=Ate", headers=admin)).content.decode("utf-8")
    assert len(rutas_ate.lstrip("﻿").strip().split("\r\n")) == 1 + 2
    distritos = (await api.client.get("/api/indicadores/distritos", headers=admin)).json()
    assert distritos[:4] == ["San Juan de Lurigancho", "El Agustino", "Santa Anita", "Ate"]


@pytest.mark.asyncio
async def test_el_distrito_se_asigna_por_cercania_si_no_se_indica(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await _vehiculo(api, admin, "ABC-123", 1500)
    res = await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 50, lat=-12.044, lng=-76.971), headers=operador)
    assert res.json()["distrito"] == "Santa Anita"


# ── Volumen del pedido (RN-004) y disponibilidad (RNF-003) ────────────────

@pytest.mark.asyncio
async def test_un_pedido_con_mas_volumen_que_la_flota_se_rechaza(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await api.client.post(
        "/api/vehiculos/", json={"placa": "VOL-001", "capacidad_kg": 1000, "volumen_m3": 10, "tipo_combustible": "DIESEL",
                                 "factor_emision_co2": 2.68}, headers=admin,
    )
    res = await api.client.post("/api/pedidos/", json={**_pedido(api.bodega_a, 50), "volumen_m3": 40}, headers=operador)
    assert res.status_code == 422 and "volumen" in res.json()["detail"]
    assert (await api.client.post(
        "/api/pedidos/", json={**_pedido(api.bodega_a, 50), "volumen_m3": 5}, headers=operador,
    )).status_code == 201


@pytest.mark.asyncio
async def test_health_ready_comprueba_la_base_de_datos(api, monkeypatch):
    res = await api.client.get("/api/health/ready")
    assert res.status_code == 200 and res.json()["db"] == "ok"
    from app import main

    class MotorCaido:
        def connect(self):
            raise ConnectionError("base de datos fuera de línea")

    monkeypatch.setattr(main, "engine", MotorCaido())
    caido = await api.client.get("/api/health/ready")
    assert caido.status_code == 503 and caido.json()["db"] == "error"


@pytest.mark.asyncio
async def test_pedidos_creados_directamente_en_la_base_conservan_tipos(api):
    async with database.AsyncSessionLocal() as sesion:
        sesion.add(Pedido(
            bodega_id=api.bodega_a, direccion="Dirección directa", latitud=-12.05, longitud=-77.04, peso_kg=10,
            ventana_inicio=datetime.now(timezone.utc), ventana_fin=datetime.now(timezone.utc),
        ))
        await sesion.commit()
        leido = (await sesion.execute(text("SELECT 1"))).scalar_one()
    assert leido == 1


@pytest.mark.asyncio
async def test_el_administrador_cambia_el_algoritmo_a_busqueda_tabu_sin_tocar_otros_modulos(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500), ("DEF-456", 2000)), pedidos=6)
    parametros = {"velocidad_kmh": 25, "servicio_min": 10, "limite_segundos": 20, "algoritmo": "tabu"}
    assert (await api.client.put("/api/admin/parametros", json=parametros, headers=admin)).status_code == 200
    plan = (await api.client.post("/api/rutas/optimizar", headers=operador)).json()
    assert plan["algoritmo"] == "Clarke-Wright + 2-opt + Búsqueda tabú"
    assert plan["pedidos_planificados"] == 6 and plan["distancia_km"] <= plan["distancia_base_km"]
    invalido = await api.client.put("/api/admin/parametros", json={**parametros, "algoritmo": "magico"}, headers=admin)
    assert invalido.status_code == 422
