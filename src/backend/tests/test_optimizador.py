"""
Pruebas del motor de rutas (RF-003, EN-001, RNF-001, RNF-006) y del cálculo de CO₂ (RF-010).

El motor es Python puro: estas pruebas no usan base de datos ni red.
"""

import random
import time
from datetime import datetime, timedelta, timezone

import pytest
from app.optimizador import (
    Camion,
    Punto,
    arboles_equivalentes,
    distancia_km,
    optimizar,
)

LIMA = (-12.0464, -77.0428)


def _puntos(n, semilla=7, peso=(20.0, 300.0)):
    azar = random.Random(semilla)
    return [
        Punto(f"p{i}", LIMA[0] + azar.uniform(-0.12, 0.12), LIMA[1] + azar.uniform(-0.12, 0.12), azar.uniform(*peso))
        for i in range(n)
    ]


FLOTA = [
    Camion("v1", "ABC-123", 1500, "DIESEL"),
    Camion("v2", "DEF-456", 2000, "GASOLINA"),
    Camion("v3", "GHI-789", 800, "GLP"),
    Camion("v4", "JKL-012", 3000, "DIESEL"),
    Camion("v5", "MNO-345", 1200, "HIBRIDO"),
    Camion("v6", "PQR-678", 2500, "ELECTRICO"),
]


def _capacidad(camion_id):
    return next(c.capacidad_kg for c in FLOTA if c.id == camion_id)


# ── Distancia y CO₂ ──────────────────────────────────────────────────────

def test_distancia_haversine_conocida():
    # Lima centro a Miraflores: unos 8 km en línea recta.
    d = distancia_km(-12.0464, -77.0428, -12.1211, -77.0297)
    assert 8.0 < d < 9.5
    assert distancia_km(-12.0, -77.0, -12.0, -77.0) == pytest.approx(0.0, abs=1e-9)


def test_emision_por_km_segun_combustible():
    assert Camion("a", "A", 1000, "ELECTRICO").kg_co2_por_km() == 0.0
    diesel = Camion("a", "A", 1000, "DIESEL").kg_co2_por_km()
    assert diesel == pytest.approx(2.68 / 7.0)
    # Un factor propio del vehículo prevalece sobre la tabla.
    assert Camion("a", "A", 1000, "DIESEL", factor_co2=3.5).kg_co2_por_km() == pytest.approx(3.5 / 7.0)
    assert Camion("a", "A", 1000, "HIBRIDO").kg_co2_por_km() < diesel


def test_arboles_equivalentes():
    assert arboles_equivalentes(21.77) == pytest.approx(1.0)
    assert arboles_equivalentes(0) == 0


# ── Casos límite ─────────────────────────────────────────────────────────

def test_sin_pedidos_devuelve_resultado_vacio():
    r = optimizar([], FLOTA)
    assert r.rutas == [] and r.sin_asignar == []
    assert r.ahorro_km_pct == 0.0 and r.ahorro_co2_pct == 0.0


def test_sin_vehiculos_deja_todo_sin_asignar_con_motivo():
    r = optimizar(_puntos(3), [])
    assert len(r.sin_asignar) == 3
    assert all("vehículos" in motivo for _, motivo in r.sin_asignar)


def test_pedido_mas_pesado_que_toda_la_flota_se_informa():
    r = optimizar([Punto("x", -12.05, -77.03, 5000.0)], FLOTA)
    assert r.rutas == []
    assert r.sin_asignar[0][0] == "x" and "excede" in r.sin_asignar[0][1]


def test_un_solo_pedido_forma_una_ruta():
    r = optimizar([Punto("x", -12.05, -77.03, 100.0)], FLOTA)
    assert len(r.rutas) == 1 and len(r.rutas[0].paradas) == 1
    assert r.rutas[0].camion_id == "v3"  # el vehículo más pequeño que admite la carga (800 kg)


# ── Propiedades del plan ─────────────────────────────────────────────────

def test_cada_pedido_aparece_una_sola_vez_y_se_respeta_la_capacidad():
    pedidos = _puntos(80, semilla=3)
    r = optimizar(pedidos, FLOTA)
    ids = [p.punto_id for ruta in r.rutas for p in ruta.paradas] + [pid for pid, _ in r.sin_asignar]
    assert sorted(ids) == sorted(p.id for p in pedidos)
    for ruta in r.rutas:
        assert ruta.carga_kg <= _capacidad(ruta.camion_id) + 1e-6
    assert len({ruta.camion_id for ruta in r.rutas}) == len(r.rutas)  # un vehículo, una ruta


def test_el_orden_de_las_paradas_es_consecutivo_y_las_llegadas_crecen():
    r = optimizar(_puntos(30), FLOTA)
    for ruta in r.rutas:
        assert [p.orden for p in ruta.paradas] == list(range(1, len(ruta.paradas) + 1))
        llegadas = [p.llegada_min for p in ruta.paradas]
        assert llegadas == sorted(llegadas)


def test_flota_heterogenea_cubre_todos_los_pedidos_si_hay_capacidad():
    # 50 pedidos (~8.000 kg) con 10.800 kg de flota: antes de la mejora quedaban pedidos sin asignar.
    r = optimizar(_puntos(50), FLOTA)
    assert r.sin_asignar == []


def test_optimizar_reduce_kilometros_y_co2_frente_a_la_linea_base():
    r = optimizar(_puntos(60), FLOTA)
    assert r.distancia_total_km < r.distancia_base_km
    assert r.ahorro_km_pct > 30
    assert r.co2_total_kg < r.co2_base_kg and r.ahorro_co2_pct > 30
    assert r.co2_evitado_kg == pytest.approx(r.co2_base_kg - r.co2_total_kg)


def test_vehiculos_electricos_no_emiten():
    solo_electrico = [Camion("e1", "ELE-001", 3000, "ELECTRICO")]
    r = optimizar(_puntos(10, peso=(10, 100)), solo_electrico)
    assert r.co2_total_kg == 0.0 and r.co2_base_kg == 0.0 and r.ahorro_co2_pct == 0.0


def test_resultado_determinista():
    a = optimizar(_puntos(40), FLOTA)
    b = optimizar(_puntos(40), FLOTA)
    assert [(r.camion_id, [p.punto_id for p in r.paradas]) for r in a.rutas] == \
           [(r.camion_id, [p.punto_id for p in r.paradas]) for r in b.rutas]


# ── Ventanas horarias ────────────────────────────────────────────────────

def test_si_se_llega_antes_de_la_ventana_se_espera():
    inicio = datetime(2026, 11, 24, 8, 0, tzinfo=timezone.utc)
    cerca = Punto("a", -12.0470, -77.0430, 50.0, inicio + timedelta(hours=2), inicio + timedelta(hours=3))
    r = optimizar([cerca], [Camion("v", "V-1", 1000, "DIESEL")], inicio_jornada=inicio)
    parada = r.rutas[0].paradas[0]
    assert parada.espera_min > 100 and parada.en_ventana is True
    assert parada.llegada == inicio + timedelta(hours=2)


def test_ventana_matematicamente_incompatible_se_informa_y_no_genera_ruta_invalida():
    # RF-003, ruta infeliz: a ~12 km del depósito (unos 29 min) no se llega en la ventana de un minuto.
    inicio = datetime(2026, 11, 24, 8, 0, tzinfo=timezone.utc)
    lejos = Punto("b", -12.1500, -77.1000, 50.0, inicio, inicio + timedelta(minutes=1))
    posible = Punto("c", -12.0470, -77.0430, 50.0, inicio, inicio + timedelta(hours=2))
    r = optimizar([lejos, posible], [Camion("v", "V-1", 1000, "DIESEL")], inicio_jornada=inicio)
    assert [pid for pid, _ in r.sin_asignar] == ["b"]
    assert "Ventana horaria incompatible" in r.sin_asignar[0][1]
    assert [p.punto_id for ruta in r.rutas for p in ruta.paradas] == ["c"]


def _par_con_holgura_minima():
    # Dos pedidos cercanos entre sí y lejos del depósito, ambos con una holgura de un minuto sobre su llegada directa.
    inicio = datetime(2026, 11, 24, 8, 0, tzinfo=timezone.utc)
    p1_lat, p1_lon, p2_lat, p2_lon = -12.10, -77.00, -12.10, -76.99
    directo1 = distancia_km(LIMA[0], LIMA[1], p1_lat, p1_lon) / 25.0 * 60.0
    directo2 = distancia_km(LIMA[0], LIMA[1], p2_lat, p2_lon) / 25.0 * 60.0
    a = Punto("a", p1_lat, p1_lon, 10.0, inicio, inicio + timedelta(minutes=directo1 + 1))
    b = Punto("b", p2_lat, p2_lon, 10.0, inicio, inicio + timedelta(minutes=directo2 + 1))
    return inicio, a, b


def test_ventana_dura_no_junta_en_una_ruta_pedidos_que_harian_llegar_tarde():
    # En un mismo recorrido el segundo llegaría tarde (servicio de 10 min del primero): se separan en dos vehículos.
    inicio, a, b = _par_con_holgura_minima()
    flota = [Camion("v1", "V-1", 1000, "DIESEL"), Camion("v2", "V-2", 1000, "DIESEL")]
    r = optimizar([a, b], flota, inicio_jornada=inicio)
    assert len(r.rutas) == 2 and all(len(x.paradas) == 1 for x in r.rutas)
    assert all(p.en_ventana is True for x in r.rutas for p in x.paradas)


def test_ventana_dura_con_un_solo_vehiculo_deja_el_pedido_sin_asignar():
    inicio, a, b = _par_con_holgura_minima()
    r = optimizar([a, b], [Camion("v", "V-1", 1000, "DIESEL")], inicio_jornada=inicio)
    assert len(r.rutas) == 1 and len(r.rutas[0].paradas) == 1
    assert len(r.sin_asignar) == 1 and "vehículos" in r.sin_asignar[0][1]


def test_pedido_sin_ventana_no_tiene_indicador_de_ventana():
    r = optimizar([Punto("a", -12.05, -77.03, 10.0)], [Camion("v", "V-1", 1000)])
    assert r.rutas[0].paradas[0].en_ventana is None


# ── Rendimiento: RNF-001 (45 s) y RNF-006 (1.000 pedidos por día) ────────

def test_cincuenta_pedidos_dentro_del_sla_de_45_segundos():
    inicio = time.perf_counter()
    r = optimizar(_puntos(50), FLOTA, limite_segundos=40)
    assert time.perf_counter() - inicio < 45
    assert r.tiempo_ms < 45000 and r.limite_alcanzado is False


def test_mil_pedidos_se_planifican_dentro_del_sla():
    flota_grande = FLOTA * 40
    inicio = time.perf_counter()
    r = optimizar(_puntos(1000, peso=(20.0, 150.0)), flota_grande, limite_segundos=40)
    assert time.perf_counter() - inicio < 45
    assert len(r.sin_asignar) == 0


def test_el_limite_de_tiempo_se_respeta_y_se_informa():
    r = optimizar(_puntos(400), FLOTA * 20, limite_segundos=0.1)
    assert r.tiempo_ms < 5000  # corta pronto aunque no termine de mejorar
    # Con el límite mínimo el plan sigue siendo válido: cada pedido en una sola ruta o sin asignar.
    ids = [p.punto_id for ruta in r.rutas for p in ruta.paradas] + [pid for pid, _ in r.sin_asignar]
    assert len(ids) == len(set(ids)) == 400


# ── Zonas protegidas (RN-003), volumen (RN-004) y caché (RNF-009) ─────────

from app.optimizador import Zona, vaciar_cache, estadisticas_cache  # noqa: E402,I001

ZONA = Zona("Reserva de prueba", -12.0464, -77.0100, 1.0)


def test_destino_dentro_de_zona_protegida_no_se_asigna():
    dentro = Punto("z", -12.0464, -77.0100, 10.0)
    fuera = Punto("f", -12.0500, -77.0600, 10.0)
    r = optimizar([dentro, fuera], FLOTA, zonas=[ZONA])
    assert [pid for pid, _ in r.sin_asignar] == ["z"] and "zona protegida" in r.sin_asignar[0][1]
    assert [p.punto_id for ruta in r.rutas for p in ruta.paradas] == ["f"]


def test_destino_detras_de_la_zona_se_alcanza_rodeandola():
    # El depósito está al oeste de la zona y el destino al este: la línea recta atraviesa la reserva.
    detras = Punto("d", -12.0464, -76.9800, 10.0)
    con_zona = optimizar([detras], FLOTA, zonas=[ZONA])
    sin_zona = optimizar([detras], FLOTA)
    assert con_zona.sin_asignar == [] and len(con_zona.rutas) == 1
    assert con_zona.rutas[0].distancia_km > sin_zona.rutas[0].distancia_km * 1.02  # el rodeo cuesta kilómetros
    assert con_zona.rutas[0].distancia_km < sin_zona.rutas[0].distancia_km * 1.5  # pero no es desproporcionado


def test_con_zona_protegida_todas_las_rutas_son_mas_largas_o_iguales_y_ningun_destino_queda_dentro():
    zona = Zona("Centro", -12.0464, -77.0428 + 0.05, 2.0)
    pedidos = _puntos(60)
    con = optimizar(pedidos, FLOTA, zonas=[zona])
    sin = optimizar(pedidos, FLOTA)
    atendidos = {p.punto_id for ruta in con.rutas for p in ruta.paradas}
    por_id = {p.id: p for p in pedidos}
    assert all(distancia_km(zona.latitud, zona.longitud, por_id[i].latitud, por_id[i].longitud) >= zona.radio_km for i in atendidos)
    adentro = {pid for pid, motivo in con.sin_asignar if "dentro de la zona protegida" in motivo}
    assert len(atendidos) + len(con.sin_asignar) == 60
    if not adentro:
        assert con.distancia_total_km >= sin.distancia_total_km - 1e-6


def test_el_volumen_es_restriccion_dura():
    pedidos = [Punto(f"v{i}", -12.05 - i * 0.001, -77.03, 10.0, volumen_m3=6.0) for i in range(3)]
    camion = Camion("c1", "VOL-001", 1000, "DIESEL", volumen_m3=10.0)
    r = optimizar(pedidos, [camion, Camion("c2", "VOL-002", 1000, "DIESEL", volumen_m3=10.0)])
    assert all(ruta.volumen_m3 <= 10.0 for ruta in r.rutas)
    assert len(r.rutas) == 2 and len(r.sin_asignar) == 1  # 3 pedidos de 6 m³ no caben en dos camiones de 10 m³


def test_pedido_con_mas_volumen_que_toda_la_flota_se_informa():
    gigante = Punto("g", -12.05, -77.03, 10.0, volumen_m3=50.0)
    r = optimizar([gigante], [Camion("c", "VOL-003", 1000, "DIESEL", volumen_m3=10.0)])
    assert "volumen" in r.sin_asignar[0][1]


def test_la_cache_de_planes_evita_recalcular_y_ahorra_cpu():
    vaciar_cache()
    pedidos = _puntos(120)
    primero = optimizar(pedidos, FLOTA * 4, usar_cache=True)
    segundo = optimizar(pedidos, FLOTA * 4, usar_cache=True)
    assert not primero.desde_cache and segundo.desde_cache
    assert segundo.tiempo_ms <= primero.tiempo_ms * 0.7  # RNF-009: al menos 30 % menos de CPU
    assert [r.camion_id for r in segundo.rutas] == [r.camion_id for r in primero.rutas]
    assert estadisticas_cache["plan_aciertos"] == 1


def test_la_cache_de_matriz_se_reutiliza_con_otros_camiones():
    vaciar_cache()
    pedidos = _puntos(40)
    optimizar(pedidos, FLOTA)
    optimizar(pedidos, FLOTA[:3] * 2)
    assert estadisticas_cache["matriz_aciertos"] >= 1
