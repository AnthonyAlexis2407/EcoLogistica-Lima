"""
Suite de pruebas ofensivas automatizadas (RNF-002): se ataca la API como lo haría un tercero y se comprueba que cada
ataque falla. Cubre las categorías de OWASP Top 10 aplicables: control de acceso roto (A01), fallos criptográficos y de
sesión (A02, A07), inyección (A03), configuración insegura (A05) y registro de eventos (A09).

No sustituye una prueba de penetración externa: es la parte repetible y automática, que corre en cada integración.
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from app.config import settings
from jose import jwt

from tests.test_ciclo_ruta import EVIDENCIA, _crear_conductor, _ruta_lista
from tests.test_rutas_api import _escenario, _pedido
from tests.utilidades import _login


def _b64(datos: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(datos).encode()).rstrip(b"=").decode()


# ── A03: inyección ───────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("carga", ["' OR '1'='1", "'; DROP TABLE usuarios;--", "admin@test.pe' --", "\" OR \"\"=\""])
async def test_inyeccion_sql_en_el_login_no_autentica(api, carga):
    res = await api.client.post("/api/auth/login", json={"email": carga, "password": carga})
    assert res.status_code in (401, 422)
    assert "access_token" not in res.text


@pytest.mark.asyncio
@pytest.mark.parametrize("carga", ["' OR 1=1 --", "%' OR '%'='", "1; DROP TABLE pedidos", "\\"])
async def test_inyeccion_sql_en_los_filtros_no_filtra_filas(api, carga):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=2)
    por_texto = await api.client.get("/api/pedidos/", params={"q": carga}, headers=operador)
    por_estado = await api.client.get("/api/pedidos/", params={"estado": carga}, headers=operador)
    por_distrito = await api.client.get("/api/pedidos/", params={"distrito": carga}, headers=operador)
    for res in (por_texto, por_estado, por_distrito):
        assert res.status_code == 200 and res.json() == []
    # La tabla sigue intacta tras los intentos.
    assert len((await api.client.get("/api/pedidos/", headers=operador)).json()) == 2


@pytest.mark.asyncio
async def test_el_texto_con_script_se_devuelve_como_dato_json_y_no_como_html(api):
    admin = await _login(api.client, "admin@test.pe")
    operador = await _login(api.client, "operador@test.pe")
    await api.client.post("/api/vehiculos/", json={"placa": "ABC-123", "capacidad_kg": 1000, "tipo_combustible": "DIESEL"}, headers=admin)
    xss = "<script>alert(document.cookie)</script>"
    await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 50, direccion=xss), headers=operador)
    res = await api.client.get("/api/pedidos/", headers=operador)
    assert res.headers["content-type"].startswith("application/json")  # el navegador no lo interpreta como HTML
    assert res.json()[0]["direccion"] == xss
    assert res.headers["x-content-type-options"] == "nosniff"


# ── A07: autenticación y sesión ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_un_token_sin_firma_alg_none_se_rechaza(api):
    usuario = (await api.client.get("/api/auth/me", headers=await _login(api.client, "admin@test.pe"))).json()
    falso = f"{_b64({'alg': 'none', 'typ': 'JWT'})}.{_b64({'sub': usuario['usuario_id'], 'rol': 'ADMIN_FLOTA'})}."
    res = await api.client.get("/api/admin/usuarios", headers={"Authorization": f"Bearer {falso}"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_un_token_firmado_con_otra_clave_o_vencido_se_rechaza(api):
    usuario = (await api.client.get("/api/auth/me", headers=await _login(api.client, "admin@test.pe"))).json()
    ajeno = jwt.encode({"sub": usuario["usuario_id"], "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "otra-clave", "HS256")
    vencido = jwt.encode(
        {"sub": usuario["usuario_id"], "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, settings.SECRET_KEY, "HS256",
    )
    for token in (ajeno, vencido, "basura.sin.formato", ""):
        res = await api.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_el_rol_del_token_no_otorga_permisos_el_servidor_consulta_la_base(api):
    bodega = (await api.client.get("/api/auth/me", headers=await _login(api.client, "bodega.a@test.pe"))).json()
    inflado = jwt.encode(
        {"sub": bodega["usuario_id"], "rol": "ADMIN_FLOTA", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.SECRET_KEY, "HS256",
    )
    res = await api.client.get("/api/admin/usuarios", headers={"Authorization": f"Bearer {inflado}"})
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_la_fuerza_bruta_bloquea_la_cuenta(api):
    for _ in range(3):
        await api.client.post("/api/auth/login", json={"email": "operador@test.pe", "password": "incorrecta"})
    bloqueado = await api.client.post("/api/auth/login", json={"email": "operador@test.pe", "password": "Operador2026!"})
    assert bloqueado.status_code == 423


@pytest.mark.asyncio
async def test_el_login_no_revela_si_el_correo_existe(api):
    existente = await api.client.post("/api/auth/login", json={"email": "operador@test.pe", "password": "incorrecta"})
    inexistente = await api.client.post("/api/auth/login", json={"email": "nadie@test.pe", "password": "incorrecta"})
    assert existente.status_code == inexistente.status_code == 401
    assert existente.json()["detail"] == inexistente.json()["detail"]


@pytest.mark.asyncio
async def test_una_cuenta_anonimizada_ya_no_puede_usar_su_token(api):
    admin = await _login(api.client, "admin@test.pe")
    bodega = await _login(api.client, "bodega.b@test.pe")
    solicitud = (await api.client.post("/api/privacidad/solicitudes", headers=bodega)).json()
    await api.client.post(f"/api/privacidad/solicitudes/{solicitud['solicitud_id']}/atender", headers=admin)
    assert (await api.client.get("/api/auth/me", headers=bodega)).status_code == 401


# ── A01: control de acceso ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ningun_rol_inferior_alcanza_los_endpoints_de_administracion(api):
    admin, operador, chofer, ruta = await _ruta_lista(api, iniciar=False)
    bodega = await _login(api.client, "bodega.a@test.pe")
    destinos = [
        ("get", "/api/admin/usuarios"), ("put", "/api/admin/parametros"), ("post", "/api/admin/zonas"),
        ("get", "/api/privacidad/solicitudes"), ("delete", "/api/admin/usuarios/x?confirmar=true"),
    ]
    for cabeceras in (operador, bodega, chofer):
        for metodo, ruta_api in destinos:
            res = await getattr(api.client, metodo)(ruta_api, headers=cabeceras, **({"json": {}} if metodo in ("put", "post") else {}))
            assert res.status_code == 403, (metodo, ruta_api, res.status_code)
    for metodo, ruta_api in destinos:
        res = await getattr(api.client, metodo)(ruta_api, **({"json": {}} if metodo in ("put", "post") else {}))
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_el_conductor_y_la_bodega_no_planifican_ni_cierran_rutas_ajenas(api):
    admin, operador, chofer, ruta = await _ruta_lista(api)
    bodega = await _login(api.client, "bodega.a@test.pe")
    for cabeceras in (chofer, bodega):
        assert (await api.client.post("/api/rutas/optimizar", headers=cabeceras)).status_code == 403
        assert (await api.client.post(f"/api/rutas/{ruta['ruta_id']}/cancelar", headers=cabeceras)).status_code == 403
        assert (await api.client.post(
            f"/api/rutas/{ruta['ruta_id']}/incidencias", json={"tipo": "AVERIA"}, headers=cabeceras,
        )).status_code == 403
    assert (await api.client.get("/api/conductor/ruta", headers=bodega)).status_code == 403


@pytest.mark.asyncio
async def test_una_bodega_no_lee_ni_modifica_pedidos_de_otra(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=1)
    ajeno = (await api.client.get("/api/pedidos/", headers=operador)).json()[0]["pedido_id"]
    bodega_b = await _login(api.client, "bodega.b@test.pe")
    assert (await api.client.get(f"/api/pedidos/{ajeno}", headers=bodega_b)).status_code == 403
    assert (await api.client.get("/api/pedidos/", headers=bodega_b)).json() == []
    assert (await api.client.post("/api/pedidos/", json=_pedido(api.bodega_a, 10), headers=bodega_b)).status_code == 403
    assert (await api.client.put(f"/api/pedidos/{ajeno}", json={"peso_kg": 1}, headers=bodega_b)).status_code == 403


@pytest.mark.asyncio
async def test_el_registro_publico_no_permite_elevar_privilegios(api):
    for rol in ("ADMIN_FLOTA", "OPERADOR", "AUDITOR", "CONDUCTOR"):
        res = await api.client.post("/api/auth/register", json={
            "nombre": "Intruso", "email": f"intruso.{rol.lower()}@test.pe", "password": "Clave12345", "rol": rol,
        })
        assert res.status_code == 403, rol


@pytest.mark.asyncio
async def test_la_actualizacion_de_usuario_ignora_campos_no_permitidos(api):
    admin = await _login(api.client, "admin@test.pe")
    bodega = (await api.client.get("/api/auth/me", headers=await _login(api.client, "bodega.a@test.pe"))).json()
    res = await api.client.put(
        f"/api/admin/usuarios/{bodega['usuario_id']}",
        json={"nombre": "Cambio Legítimo", "estado": "ACTIVO", "login_attempts": 0, "password_hash": "x", "email": "otro@x.pe"},
        headers=admin,
    )
    assert res.status_code == 200 and res.json()["email"] == "bodega.a@test.pe" and res.json()["rol"] == "BODEGA"


@pytest.mark.asyncio
async def test_los_ids_ajenos_de_notificaciones_y_paradas_responden_como_inexistentes(api):
    admin, operador, chofer, ruta = await _ruta_lista(api)
    _, otro = await _crear_conductor(api, admin, email="otro@test.pe", licencia="Q11111111")
    parada = ruta["paradas"][0]["parada_id"]
    assert (await api.client.post(f"/api/conductor/paradas/{parada}/entregar", json=EVIDENCIA, headers=otro)).status_code == 404
    assert (await api.client.post(f"/api/conductor/paradas/{parada}/reprogramar", json={"motivo": "ataque"}, headers=otro)).status_code == 404
    sync = (await api.client.post("/api/conductor/sync", json={"acciones": [
        {"tipo": "ENTREGA", "parada_id": parada, "clave_sync": "ataque-sync-0001", **EVIDENCIA},
    ]}, headers=otro)).json()
    assert sync["rechazadas"] == 1 and sync["aplicadas"] == 0


# ── A05: configuración y cabeceras ───────────────────────────────────────

@pytest.mark.asyncio
async def test_las_respuestas_llevan_cabeceras_de_seguridad_y_no_se_guardan_en_cache(api):
    res = await api.client.post("/api/auth/login", json={"email": "admin@test.pe", "password": "Admin2026!"})
    assert res.headers["x-frame-options"] == "DENY" and res.headers["x-content-type-options"] == "nosniff"
    assert "max-age=31536000" in res.headers["strict-transport-security"]
    assert res.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert res.headers["referrer-policy"] == "no-referrer"
    assert "geolocation=(self)" in res.headers["permissions-policy"] and "microphone=()" in res.headers["permissions-policy"]
    assert res.headers["cache-control"] == "no-store"


@pytest.mark.asyncio
async def test_los_cuerpos_desmesurados_y_los_tipos_invalidos_se_rechazan(api):
    admin, operador = await _escenario(api, vehiculos=(("ABC-123", 1500),), pedidos=1)
    assert (await api.client.post("/api/pedidos/", json={**_pedido(api.bodega_a, 10), "peso_kg": "no-numero"}, headers=operador)).status_code == 422
    assert (await api.client.post("/api/pedidos/", json={**_pedido(api.bodega_a, 10), "latitud": 999}, headers=operador)).status_code == 422
    assert (await api.client.post("/api/pedidos/", json={**_pedido(api.bodega_a, -5)}, headers=operador)).status_code == 422
    assert (await api.client.get("/api/pedidos/", params={"limit": 100000}, headers=operador)).status_code == 422
    assert (await api.client.post("/api/conductor/sync", json={"acciones": [{}] * 500}, headers=operador)).status_code in (403, 422)


@pytest.mark.asyncio
async def test_no_se_exponen_secretos_ni_hashes_en_las_respuestas(api):
    admin = await _login(api.client, "admin@test.pe")
    usuarios = (await api.client.get("/api/admin/usuarios", headers=admin)).text
    assert "password" not in usuarios.lower() and "$2b$" not in usuarios and settings.SECRET_KEY not in usuarios
    login = (await api.client.post("/api/auth/login", json={"email": "admin@test.pe", "password": "Admin2026!"})).text
    assert "$2b$" not in login and "password_hash" not in login


# ── A09: registro de eventos ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_los_intentos_de_acceso_denegado_se_registran_sin_datos_personales(api, caplog):
    import logging

    bodega = await _login(api.client, "bodega.a@test.pe")
    with caplog.at_level(logging.WARNING, logger="ecologistica.security"):
        await api.client.get("/api/admin/usuarios", headers=bodega)
        await api.client.post("/api/auth/login", json={"email": "operador@test.pe", "password": "incorrecta"})
    texto = caplog.text
    assert "Acceso denegado" in texto and "rol=BODEGA" in texto and "login_fallido" in texto
    assert "bodega.a@test.pe" not in texto and "operador@test.pe" not in texto
