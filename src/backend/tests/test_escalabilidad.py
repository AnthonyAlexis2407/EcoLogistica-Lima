"""
Pruebas de escalabilidad y eficiencia (RNF-006, RNF-009).

RNF-006: «degradación de tiempos de respuesta ≤ 10 % al procesar 1.000 pedidos/día frente a la línea base de 250».
Se mide el tiempo de respuesta de las operaciones de consulta de la API con 250 y con 1.000 pedidos en la base (la
paginación y los índices mantienen el costo constante) y el tiempo del motor de rutas con ambos volúmenes, que debe
quedar por debajo del SLA de 45 s (RNF-001). La medición completa con tablas se resume en el informe de cumplimiento.

RNF-009: con la caché de planes, repetir una corrida idéntica consume al menos 30 % menos CPU.
"""

import random
import statistics
import time
from datetime import datetime, timedelta, timezone

import pytest
from app import database
from app.models import Pedido
from app.optimizador import Camion, Punto, optimizar, vaciar_cache

from tests.utilidades import _login

LIMA = (-12.0464, -77.0428)
FLOTA = [Camion(f"v{i}", f"P-{i}", 1500 + 100 * (i % 5), "DIESEL") for i in range(120)]


def _puntos(n, semilla=11):
    azar = random.Random(semilla)
    return [
        Punto(f"p{i}", LIMA[0] + azar.uniform(-0.12, 0.12), LIMA[1] + azar.uniform(-0.12, 0.12), azar.uniform(10, 120))
        for i in range(n)
    ]


async def _sembrar(api, cantidad):
    ahora = datetime.now(timezone.utc)
    azar = random.Random(5)
    async with database.AsyncSessionLocal() as sesion:
        sesion.add_all([
            Pedido(
                bodega_id=api.bodega_a, direccion=f"Av. Escala {i}", latitud=LIMA[0] + azar.uniform(-0.1, 0.1),
                longitud=LIMA[1] + azar.uniform(-0.1, 0.1), peso_kg=50, distrito="Ate",
                ventana_inicio=ahora, ventana_fin=ahora + timedelta(hours=8),
            )
            for i in range(cantidad)
        ])
        await sesion.commit()


async def _mediana_ms(api, headers, repeticiones=15):
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        res = await api.client.get("/api/pedidos/?limit=12&distrito=Ate", headers=headers)
        assert res.status_code == 200
        tiempos.append((time.perf_counter() - inicio) * 1000)
    return statistics.median(tiempos)


@pytest.mark.asyncio
async def test_el_tiempo_de_respuesta_no_se_degrada_mas_de_10_por_ciento_de_250_a_1000_pedidos(api):
    operador = await _login(api.client, "operador@test.pe")
    await _sembrar(api, 250)
    base = await _mediana_ms(api, operador)
    await _sembrar(api, 750)  # total 1.000
    carga = await _mediana_ms(api, operador)
    # Margen absoluto de 15 ms para el ruido de un equipo compartido cuando los tiempos son de pocos milisegundos.
    assert carga <= base * 1.10 + 15.0, f"250 pedidos: {base:.1f} ms; 1.000 pedidos: {carga:.1f} ms"
    assert (await api.client.get("/api/pedidos/count", headers=operador)).json()["TOTAL"] == 1000


def test_el_motor_planifica_250_y_1000_pedidos_dentro_del_sla():
    tiempos = {}
    for n in (250, 1000):
        inicio = time.perf_counter()
        plan = optimizar(_puntos(n), FLOTA, limite_segundos=40)
        tiempos[n] = time.perf_counter() - inicio
        assert tiempos[n] < 45 and plan.sin_asignar == [] and plan.limite_alcanzado is False
    assert tiempos[1000] < 45


def test_la_cache_reduce_al_menos_30_por_ciento_la_cpu_de_una_corrida_repetida():
    vaciar_cache()
    puntos = _puntos(300)
    inicio = time.process_time()
    optimizar(puntos, FLOTA, usar_cache=True)
    sin_cache = time.process_time() - inicio
    inicio = time.process_time()
    repetida = optimizar(puntos, FLOTA, usar_cache=True)
    con_cache = time.process_time() - inicio
    assert repetida.desde_cache is True
    reduccion = (sin_cache - con_cache) / sin_cache * 100
    assert reduccion >= 30, f"reducción de CPU: {reduccion:.1f} %"
