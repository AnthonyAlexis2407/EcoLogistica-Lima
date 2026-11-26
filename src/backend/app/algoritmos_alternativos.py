"""
Metaheurísticas alternativas del motor de rutas (EN-001, RNF-005).

El motor base (Clarke-Wright + 2-opt, en `optimizador.py`) es el que se usa por defecto. Este módulo agrega dos
alternativas que se pueden activar desde los parámetros del algoritmo sin tocar los módulos de pedidos, flota o dashboard,
que es lo que pide RNF-005:

- **Búsqueda tabú** (`busqueda_tabu`): mejora entre rutas moviendo un pedido de una ruta a otra, con memoria de movimientos
  prohibidos para no volver atrás y criterio de aspiración (se acepta un movimiento prohibido si mejora el mejor resultado).
- **Algoritmo genético** (`algoritmo_genetico`): evoluciona rutas gigantes (un recorrido con todos los pedidos) que se
  dividen en rutas por capacidad. Se incluye para el estudio comparativo (`scripts/spike_algoritmos.py`).

Ambas respetan las mismas restricciones duras que el motor base (capacidad de peso y volumen, ventanas horarias y zonas)
mediante `_Problema.factible`, y el mismo límite de tiempo.
"""

from __future__ import annotations

import random
import time

from app.optimizador import _largo, _Problema


def _costo_total(m: list[list[float]], rutas: list[list[int]]) -> float:
    return sum(_largo(m, r) for r in rutas if r)


def busqueda_tabu(
    prob: _Problema, rutas: list[list[int]], capacidad: float, capacidad_vol: float, vence: float,
    tenure: int = 10, max_iteraciones: int = 300,
) -> list[list[int]]:
    """Mejora entre rutas: reubica un pedido en otra ruta mientras haya movimientos que reduzcan la distancia."""
    m, pesos, vols = prob.m, prob.pesos, prob.volumenes
    actual = [list(r) for r in rutas if r]
    cargas = [sum(pesos[i - 1] for i in r) for r in actual]
    volumenes = [sum(vols[i - 1] for i in r) for r in actual]
    costo = _costo_total(m, actual)
    mejor, mejor_costo = [list(r) for r in actual], costo
    prohibido: dict[int, int] = {}

    for iteracion in range(max_iteraciones):
        if time.perf_counter() > vence:
            break
        elegido: tuple[float, int, int, int, int] | None = None  # (delta, ruta origen, posición, ruta destino, posición)
        for a, ra in enumerate(actual):
            for i, c in enumerate(ra):
                previo = ra[i - 1] if i > 0 else 0
                siguiente = ra[i + 1] if i < len(ra) - 1 else 0
                ahorro = m[previo][c] + m[c][siguiente] - m[previo][siguiente]
                for b, rb in enumerate(actual):
                    if a == b or cargas[b] + pesos[c - 1] > capacidad or volumenes[b] + vols[c - 1] > capacidad_vol:
                        continue
                    for j in range(len(rb) + 1):
                        p = rb[j - 1] if j > 0 else 0
                        s = rb[j] if j < len(rb) else 0
                        delta = m[p][c] + m[c][s] - m[p][s] - ahorro
                        nuevo_costo = costo + delta
                        es_tabu = prohibido.get(c, -1) > iteracion
                        if es_tabu and nuevo_costo >= mejor_costo - 1e-9:
                            continue  # sin aspiración, el movimiento está prohibido
                        if elegido is None or delta < elegido[0]:
                            if prob.con_restricciones and not prob.factible(rb[:j] + [c] + rb[j:]):
                                continue
                            elegido = (delta, a, i, b, j)
        if elegido is None:
            break
        delta, a, i, b, j = elegido
        c = actual[a].pop(i)
        actual[b].insert(j, c)
        cargas[a] -= pesos[c - 1]
        cargas[b] += pesos[c - 1]
        volumenes[a] -= vols[c - 1]
        volumenes[b] += vols[c - 1]
        costo += delta
        prohibido[c] = iteracion + tenure
        if not actual[a]:  # una ruta vacía se elimina
            del actual[a], cargas[a], volumenes[a]
        if costo < mejor_costo - 1e-9:
            mejor, mejor_costo = [list(r) for r in actual], costo
    return mejor


def _dividir(prob: _Problema, recorrido: list[int], capacidad: float, capacidad_vol: float) -> list[list[int]]:
    """Parte un recorrido gigante en rutas: se cierra la ruta cuando el siguiente pedido ya no cabe o la haría inviable."""
    rutas: list[list[int]] = []
    ruta: list[int] = []
    peso = volumen = 0.0
    for c in recorrido:
        cabe = peso + prob.pesos[c - 1] <= capacidad and volumen + prob.volumenes[c - 1] <= capacidad_vol
        if cabe and prob.con_restricciones:
            cabe = prob.factible([*ruta, c])
        if ruta and not cabe:
            rutas.append(ruta)
            ruta, peso, volumen = [], 0.0, 0.0
        ruta.append(c)
        peso += prob.pesos[c - 1]
        volumen += prob.volumenes[c - 1]
    if ruta:
        rutas.append(ruta)
    return rutas


def algoritmo_genetico(
    prob: _Problema, indices: list[int], capacidad: float, capacidad_vol: float, vence: float,
    poblacion: int = 24, generaciones: int = 200, semilla: int = 7,
) -> list[list[int]]:
    """Evoluciona recorridos gigantes (cruce por orden y mutación por inversión) y devuelve las rutas del mejor."""
    azar = random.Random(semilla)  # nosec B311 - no es criptografía: semilla fija para resultados reproducibles
    m = prob.m

    def aptitud(recorrido: list[int]) -> float:
        return _costo_total(m, _dividir(prob, recorrido, capacidad, capacidad_vol))

    # Población inicial: un recorrido «de barrido» por ángulo (agrupa pedidos cercanos) y variaciones al azar.
    base = sorted(indices, key=lambda i: (m[0][i], i))
    individuos = [base] + [azar.sample(indices, len(indices)) for _ in range(poblacion - 1)]
    puntajes = [aptitud(x) for x in individuos]

    def torneo() -> list[int]:
        a, b = azar.randrange(len(individuos)), azar.randrange(len(individuos))
        return individuos[a] if puntajes[a] <= puntajes[b] else individuos[b]

    for _ in range(generaciones):
        if time.perf_counter() > vence:
            break
        padre, madre = torneo(), torneo()
        n = len(padre)
        i, j = sorted(azar.sample(range(n), 2)) if n > 1 else (0, 0)
        trozo = padre[i:j + 1]
        en_trozo = set(trozo)
        hijo = [g for g in madre if g not in en_trozo]
        hijo = hijo[:i] + trozo + hijo[i:]
        if azar.random() < 0.3 and n > 2:  # mutación: invertir un tramo
            x, y = sorted(azar.sample(range(n), 2))
            hijo[x:y + 1] = reversed(hijo[x:y + 1])
        puntaje = aptitud(hijo)
        peor = max(range(len(individuos)), key=lambda k: puntajes[k])
        if puntaje < puntajes[peor]:
            individuos[peor], puntajes[peor] = hijo, puntaje

    mejor = individuos[min(range(len(individuos)), key=lambda k: puntajes[k])]
    return _dividir(prob, mejor, capacidad, capacidad_vol)
