"""
Pruebas de rendimiento y sostenibilidad (Informe Green IT): paginación de 12, ETag/304,
compresión, cabeceras de caché y servicio del frontend compilado.
"""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.rendimiento import CACHE_INMUTABLE, CACHE_REVALIDAR, montar_frontend

from .test_criterios_aceptacion import _login, _pedido, api  # noqa: F401  (fixture `api` y ayudantes)


async def _flota(cliente, cabeceras, cantidad, prefijo="PG"):
    for i in range(cantidad):
        res = await cliente.post(
            "/api/vehiculos/",
            json={"placa": f"{prefijo}-{i:03d}", "capacidad_kg": 500 + i, "tipo_combustible": "DIESEL" if i % 2 else "GLP"},
            headers=cabeceras,
        )
        assert res.status_code == 201


# ── Paginación (optimización 2) ───────────────────────────────────────
@pytest.mark.asyncio
async def test_listado_de_vehiculos_pagina_de_12_y_informa_el_total(api):
    admin = await _login(api.client, "admin@test.pe")
    await _flota(api.client, admin, 30)

    primera = await api.client.get("/api/vehiculos/", headers=admin)
    assert len(primera.json()) == 12
    assert primera.headers["x-total-count"] == "30"

    tercera = await api.client.get("/api/vehiculos/?page=3", headers=admin)
    assert len(tercera.json()) == 6
    placas = [v["placa"] for v in primera.json()] + [v["placa"] for v in tercera.json()]
    assert len(set(placas)) == 18


@pytest.mark.asyncio
async def test_listado_de_vehiculos_filtra_por_busqueda_y_estado(api):
    admin = await _login(api.client, "admin@test.pe")
    await _flota(api.client, admin, 10)

    por_placa = await api.client.get("/api/vehiculos/?q=pg-00", headers=admin)
    assert por_placa.headers["x-total-count"] == "10"
    por_combustible = await api.client.get("/api/vehiculos/?q=glp", headers=admin)
    assert por_combustible.headers["x-total-count"] == "5"
    sin_resultados = await api.client.get("/api/vehiculos/?estado=EN_MANTENIMIENTO", headers=admin)
    assert sin_resultados.json() == []
    assert sin_resultados.headers["x-total-count"] == "0"


@pytest.mark.asyncio
async def test_la_busqueda_trata_los_comodines_como_texto(api):
    admin = await _login(api.client, "admin@test.pe")
    await _flota(api.client, admin, 3)
    res = await api.client.get("/api/vehiculos/?q=%25", headers=admin)  # "%" literal
    assert res.json() == []


@pytest.mark.asyncio
async def test_limite_de_pagina_fuera_de_rango_se_rechaza(api):
    admin = await _login(api.client, "admin@test.pe")
    assert (await api.client.get("/api/vehiculos/?limit=51", headers=admin)).status_code == 422
    assert (await api.client.get("/api/vehiculos/?page=0", headers=admin)).status_code == 422


@pytest.mark.asyncio
async def test_listado_de_pedidos_pagina_busca_y_conserva_el_aislamiento_por_bodega(api):
    admin = await _login(api.client, "admin@test.pe")
    bodega_a = await _login(api.client, "bodega.a@test.pe")
    await api.client.post("/api/vehiculos/", json={"placa": "PED-001", "capacidad_kg": 900, "tipo_combustible": "GLP"}, headers=admin)
    for i in range(14):
        cuerpo = _pedido(api.bodega_a, 10 + i)
        cuerpo["direccion"] = f"Jr. Los Pinos {i}, El Agustino" if i % 2 else f"Av. Lima {i}, Ate"
        assert (await api.client.post("/api/pedidos/", json=cuerpo, headers=bodega_a)).status_code == 201

    pagina = await api.client.get("/api/pedidos/", headers=bodega_a)
    assert len(pagina.json()) == 12
    assert pagina.headers["x-total-count"] == "14"
    busqueda = await api.client.get("/api/pedidos/?q=pinos", headers=bodega_a)
    assert busqueda.headers["x-total-count"] == "7"
    de_otra_bodega = await _login(api.client, "bodega.b@test.pe")
    ajenos = await api.client.get("/api/pedidos/", headers=de_otra_bodega)
    assert ajenos.json() == [] and ajenos.headers["x-total-count"] == "0"


@pytest.mark.asyncio
async def test_bodega_sin_registro_recibe_lista_vacia_con_total_cero(api):
    nueva = await api.client.post(
        "/api/auth/register",
        json={"nombre": "Sin Bodega", "email": "sinbodega@test.pe", "password": "Clave12345", "rol": "BODEGA"},
    )
    assert nueva.status_code == 201
    login = await api.client.post("/api/auth/login", json={"email": "sinbodega@test.pe", "password": "Clave12345"})
    res = await api.client.get("/api/pedidos/", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert res.json() == [] and res.headers["x-total-count"] == "0"


# ── Caché con ETag (optimización 7) ───────────────────────────────────
@pytest.mark.asyncio
async def test_get_de_la_api_lleva_etag_y_responde_304_si_no_cambio(api):
    admin = await _login(api.client, "admin@test.pe")
    await _flota(api.client, admin, 3)

    primera = await api.client.get("/api/vehiculos/", headers=admin)
    etag = primera.headers["etag"]
    assert primera.headers["cache-control"] == "private, no-cache"

    igual = await api.client.get("/api/vehiculos/", headers={**admin, "If-None-Match": etag})
    assert igual.status_code == 304
    assert igual.content == b""
    assert igual.headers["etag"] == etag
    assert igual.headers["x-total-count"] == "3"

    await _flota(api.client, admin, 1, prefijo="EXT")
    cambiada = await api.client.get("/api/vehiculos/", headers={**admin, "If-None-Match": etag})
    assert cambiada.status_code == 200
    assert cambiada.headers["etag"] != etag


@pytest.mark.asyncio
async def test_etag_debil_y_lista_de_etags_tambien_validan(api):
    admin = await _login(api.client, "admin@test.pe")
    etag = (await api.client.get("/api/vehiculos/", headers=admin)).headers["etag"]
    res = await api.client.get("/api/vehiculos/", headers={**admin, "If-None-Match": f'"otro", W/{etag}'})
    assert res.status_code == 304


@pytest.mark.asyncio
async def test_sesion_y_estado_no_se_guardan_en_cache(api):
    login = await api.client.post("/api/auth/login", json={"email": "operador@test.pe", "password": "Operador2026!"})
    assert login.headers["cache-control"] == "no-store"
    assert "etag" not in login.headers
    salud = await api.client.get("/api/health")
    assert salud.headers["cache-control"] == "no-store"
    assert salud.headers["x-content-type-options"] == "nosniff"


# ── Compresión (optimización 8) ───────────────────────────────────────
@pytest.mark.asyncio
async def test_respuestas_grandes_se_comprimen_con_gzip_o_brotli(api):
    admin = await _login(api.client, "admin@test.pe")
    await _flota(api.client, admin, 12)

    sin = await api.client.get("/api/vehiculos/", headers={**admin, "Accept-Encoding": "identity"})
    assert "content-encoding" not in sin.headers

    comprimida = await api.client.get("/api/vehiculos/", headers={**admin, "Accept-Encoding": "gzip"})
    assert comprimida.headers["content-encoding"] == "gzip"
    # httpx entrega el cuerpo ya descomprimido: el ahorro se ve en Content-Length (bytes por la red).
    assert int(comprimida.headers["content-length"]) < len(sin.content)
    assert comprimida.content == sin.content

    brotli = await api.client.get("/api/vehiculos/", headers={**admin, "Accept-Encoding": "br"})
    assert brotli.headers["content-encoding"] == "br"


# ── Frontend compilado (optimizaciones 7 y 8) ─────────────────────────
@pytest.fixture
def frontend(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>EcoLogística</title>", encoding="utf-8")
    (dist / "assets" / "index-abc123.js").write_text("console.log('ok')", encoding="utf-8")
    (dist / "robots.txt").write_text("User-agent: *", encoding="utf-8")
    (tmp_path / "secreto.txt").write_text("no se debe exponer", encoding="utf-8")
    app = FastAPI()
    assert montar_frontend(app, dist) is True
    return app


@pytest.mark.asyncio
async def test_frontend_assets_con_cache_inmutable_e_index_con_revalidacion(frontend):
    async with AsyncClient(transport=ASGITransport(app=frontend), base_url="http://t") as c:
        asset = await c.get("/assets/index-abc123.js")
        assert asset.status_code == 200 and asset.headers["cache-control"] == CACHE_INMUTABLE
        indice = await c.get("/")
        assert indice.headers["cache-control"] == CACHE_REVALIDAR
        assert "default-src 'self'" in indice.headers["content-security-policy"]
        assert (await c.get("/robots.txt")).headers["cache-control"] == CACHE_REVALIDAR


@pytest.mark.asyncio
async def test_frontend_rutas_de_la_spa_devuelven_index_y_la_api_inexistente_404(frontend):
    async with AsyncClient(transport=ASGITransport(app=frontend), base_url="http://t") as c:
        assert "EcoLogística" in (await c.get("/vehiculos")).text
        api = await c.get("/api/no-existe")
        assert api.status_code == 404 and api.json() == {"detail": "Not Found"}
        assert (await c.post("/vehiculos")).status_code == 404


@pytest.mark.asyncio
async def test_frontend_no_expone_archivos_fuera_de_dist(frontend):
    async with AsyncClient(transport=ASGITransport(app=frontend), base_url="http://t") as c:
        assert "no se debe exponer" not in (await c.get("/..%2Fsecreto.txt")).text
        assert "no se debe exponer" not in (await c.get("/%2e%2e/secreto.txt")).text


def test_montar_frontend_sin_dist_no_registra_rutas(tmp_path):
    assert montar_frontend(FastAPI(), tmp_path / "no-existe") is False
