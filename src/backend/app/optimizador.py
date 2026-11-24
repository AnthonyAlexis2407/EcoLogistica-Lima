"""
Motor de optimización de rutas (RF-003, EN-001, RNF-001).

Resuelve una versión del problema de rutas de vehículos con capacidad (CVRP) para la última milla de Lima:

1. **Construcción** con el algoritmo de ahorros de Clarke y Wright (1964): parte de un viaje por pedido y fusiona
   rutas mientras el ahorro de distancia sea positivo y no se exceda la capacidad.
2. **Mejora local** con 2-opt dentro de cada ruta, con un límite de tiempo (por defecto 40 s, por debajo del SLA de 45 s).
3. **Asignación** de cada ruta al vehículo disponible de menor capacidad que la admita, a igualdad el de menor emisión.
4. **Evaluación**: kilómetros, horas de llegada (con espera si se llega antes de la ventana), cumplimiento de ventanas y
   emisiones de CO₂ frente a una línea base sin optimizar (un viaje de ida y vuelta por pedido).

Alcance del MVP (declarado en el informe de cumplimiento): las ventanas horarias se EVALÚAN y se informan, pero no son
una restricción dura de la búsqueda; la distancia es en línea recta (haversine) y no por la red vial.

El módulo es Python puro y no depende de FastAPI ni de la base de datos, de modo que se prueba de forma aislada.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

RADIO_TIERRA_KM = 6371.0088
VELOCIDAD_KMH = 25.0  # velocidad media urbana supuesta para Lima
SERVICIO_MIN = 10.0  # minutos de descarga por parada
LIMITE_SEGUNDOS_POR_DEFECTO = 40.0  # SLA de RNF-001: 45 s

# Rendimiento supuesto (km por litro) y factor de emisión (kg de CO₂ por litro) por combustible.
# Fuente de los factores: los de referencia del seed del proyecto (Documento 11); son supuestos del MVP.
CONSUMO_KM_POR_LITRO = {"DIESEL": 7.0, "GASOLINA": 8.0, "GLP": 7.5, "HIBRIDO": 14.0, "ELECTRICO": 0.0}
FACTOR_CO2_KG_POR_LITRO = {"DIESEL": 2.68, "GASOLINA": 2.31, "GLP": 1.51, "HIBRIDO": 1.10, "ELECTRICO": 0.0}

# Un árbol maduro absorbe en promedio 21,77 kg de CO₂ al año (equivalencia usada para comunicar la compensación, RF-010).
KG_CO2_POR_ARBOL_AL_ANIO = 21.77


@dataclass(frozen=True)
class Punto:
    """Una entrega: ubicación, peso y ventana horaria opcional."""

    id: str
    latitud: float
    longitud: float
    peso_kg: float
    ventana_inicio: datetime | None = None
    ventana_fin: datetime | None = None


@dataclass(frozen=True)
class Camion:
    """Un vehículo disponible."""

    id: str
    placa: str
    capacidad_kg: float
    combustible: str = "DIESEL"
    factor_co2: float | None = None  # kg de CO₂ por litro; si falta se usa el de la tabla

    def kg_co2_por_km(self) -> float:
        """Emisión por kilómetro recorrido (0 para vehículos eléctricos)."""
        consumo = CONSUMO_KM_POR_LITRO.get(self.combustible, CONSUMO_KM_POR_LITRO["DIESEL"])
        if consumo <= 0:
            return 0.0
        factor = self.factor_co2 if self.factor_co2 is not None else FACTOR_CO2_KG_POR_LITRO.get(self.combustible, 2.68)
        return factor / consumo


@dataclass
class ParadaPlan:
    punto_id: str
    orden: int
    distancia_desde_anterior_km: float
    llegada_min: float  # minutos desde el inicio de la jornada
    espera_min: float = 0.0
    llegada: datetime | None = None
    en_ventana: bool | None = None  # None si el pedido no tiene ventana


@dataclass
class RutaPlan:
    camion_id: str
    paradas: list[ParadaPlan]
    distancia_km: float
    carga_kg: float
    co2_kg: float
    duracion_min: float


@dataclass
class ResultadoOptimizacion:
    rutas: list[RutaPlan] = field(default_factory=list)
    sin_asignar: list[tuple[str, str]] = field(default_factory=list)  # (pedido_id, motivo)
    distancia_total_km: float = 0.0
    co2_total_kg: float = 0.0
    distancia_base_km: float = 0.0
    co2_base_kg: float = 0.0
    tiempo_ms: float = 0.0
    limite_alcanzado: bool = False
    algoritmo: str = "Clarke-Wright + 2-opt"

    @property
    def ahorro_km_pct(self) -> float:
        return _porcentaje_ahorro(self.distancia_base_km, self.distancia_total_km)

    @property
    def ahorro_co2_pct(self) -> float:
        return _porcentaje_ahorro(self.co2_base_kg, self.co2_total_kg)

    @property
    def co2_evitado_kg(self) -> float:
        return max(0.0, self.co2_base_kg - self.co2_total_kg)


def _porcentaje_ahorro(base: float, real: float) -> float:
    return round((base - real) / base * 100.0, 1) if base > 0 else 0.0


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia de círculo máximo (fórmula de haversine) en kilómetros."""
    f1, f2 = math.radians(lat1), math.radians(lat2)
    df, dl = f2 - f1, math.radians(lon2 - lon1)
    a = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * RADIO_TIERRA_KM * math.asin(min(1.0, math.sqrt(a)))


def arboles_equivalentes(co2_kg: float) -> float:
    """Árboles que absorberían ese CO₂ durante un año (comunicación de la compensación, RF-010)."""
    return round(co2_kg / KG_CO2_POR_ARBOL_AL_ANIO, 2)


# ──────────────────────────────────────────────────────────────────────────
#  Construcción: ahorros de Clarke y Wright
# ──────────────────────────────────────────────────────────────────────────

def _matriz(deposito: tuple[float, float], puntos: list[Punto]) -> list[list[float]]:
    """Matriz de distancias; el índice 0 es el depósito y 1..n los puntos."""
    coords = [deposito] + [(p.latitud, p.longitud) for p in puntos]
    n = len(coords)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        lat_i, lon_i = coords[i]
        fila = m[i]
        for j in range(i + 1, n):
            d = distancia_km(lat_i, lon_i, coords[j][0], coords[j][1])
            fila[j] = d
            m[j][i] = d
    return m


def _ahorros(m: list[list[float]], indices: list[int]) -> list[tuple[float, int, int]]:
    lista = [
        (m[0][i] + m[0][j] - m[i][j], i, j)
        for pos, i in enumerate(indices) for j in indices[pos + 1:]
    ]
    lista = [a for a in lista if a[0] > 1e-9]
    lista.sort(key=lambda a: a[0], reverse=True)
    return lista


def _clarke_wright(
    m: list[list[float]], pesos: list[float], indices: list[int], capacidad: float, vence: float,
) -> tuple[list[list[int]], bool]:
    """Rutas (listas de índices 1..n) construidas solo con los puntos de `indices`. Devuelve si se agotó el tiempo."""
    ruta_de = {i: [i] for i in indices}  # índice -> lista compartida (ruta)
    carga = {id(r): pesos[i - 1] for i, r in ruta_de.items()}
    agotado = False
    for contador, (_, i, j) in enumerate(_ahorros(m, indices)):
        if contador % 2000 == 0 and time.perf_counter() > vence:
            agotado = True
            break
        ri, rj = ruta_de[i], ruta_de[j]
        if ri is rj or carga[id(ri)] + carga[id(rj)] > capacidad:
            continue
        # Solo se unen por los extremos de cada ruta.
        if ri[-1] == i and rj[0] == j:
            nueva = ri + rj
        elif ri[0] == i and rj[-1] == j:
            nueva = rj + ri
        elif ri[0] == i and rj[0] == j:
            nueva = ri[::-1] + rj
        elif ri[-1] == i and rj[-1] == j:
            nueva = ri + rj[::-1]
        else:
            continue
        total = carga[id(ri)] + carga[id(rj)]
        carga.pop(id(ri), None)
        carga.pop(id(rj), None)
        carga[id(nueva)] = total
        for k in nueva:
            ruta_de[k] = nueva
    unicas: dict[int, list[int]] = {}
    for r in ruta_de.values():
        unicas[id(r)] = r
    return list(unicas.values()), agotado


# ──────────────────────────────────────────────────────────────────────────
#  Mejora: 2-opt dentro de cada ruta
# ──────────────────────────────────────────────────────────────────────────

def _largo(m: list[list[float]], ruta: list[int]) -> float:
    total = m[0][ruta[0]] + m[ruta[-1]][0]
    for a, b in zip(ruta, ruta[1:], strict=False):
        total += m[a][b]
    return total


def _dos_opt(m: list[list[float]], ruta: list[int], vence: float) -> tuple[list[int], bool]:
    """Invierte tramos mientras reduzcan la distancia; se detiene al llegar al límite de tiempo."""
    n = len(ruta)
    if n < 3:
        return ruta, False
    mejor = list(ruta)
    mejoro = True
    while mejoro:
        mejoro = False
        for i in range(n - 1):
            if time.perf_counter() > vence:
                return mejor, True
            for j in range(i + 1, n):
                antes_i = mejor[i - 1] if i > 0 else 0
                despues_j = mejor[j + 1] if j < n - 1 else 0
                actual = m[antes_i][mejor[i]] + m[mejor[j]][despues_j]
                nuevo = m[antes_i][mejor[j]] + m[mejor[i]][despues_j]
                if nuevo < actual - 1e-9:
                    mejor[i:j + 1] = reversed(mejor[i:j + 1])
                    mejoro = True
    return mejor, False


# ──────────────────────────────────────────────────────────────────────────
#  Evaluación y asignación
# ──────────────────────────────────────────────────────────────────────────

def _evaluar(
    m: list[list[float]], ruta: list[int], puntos: list[Punto], camion: Camion,
    inicio_jornada: datetime | None,
) -> RutaPlan:
    """Calcula kilómetros, llegadas (con espera), cumplimiento de ventanas y CO₂ de una ruta ya ordenada."""
    if inicio_jornada is None:
        inicios = [puntos[i - 1].ventana_inicio for i in ruta if puntos[i - 1].ventana_inicio]
        inicio_jornada = min(inicios) if inicios else None
    reloj = 0.0  # minutos desde el inicio de la jornada
    anterior = 0
    paradas: list[ParadaPlan] = []
    carga = 0.0
    for orden, idx in enumerate(ruta, start=1):
        punto = puntos[idx - 1]
        tramo = m[anterior][idx]
        reloj += tramo / VELOCIDAD_KMH * 60.0
        espera = 0.0
        llegada = inicio_jornada + timedelta(minutes=reloj) if inicio_jornada else None
        en_ventana: bool | None = None
        if llegada and punto.ventana_inicio and punto.ventana_fin:
            if llegada < punto.ventana_inicio:
                espera = (punto.ventana_inicio - llegada).total_seconds() / 60.0
                reloj += espera
                llegada = punto.ventana_inicio
            en_ventana = llegada <= punto.ventana_fin
        paradas.append(ParadaPlan(
            punto_id=punto.id, orden=orden, distancia_desde_anterior_km=round(tramo, 3),
            llegada_min=round(reloj, 1), espera_min=round(espera, 1), llegada=llegada, en_ventana=en_ventana,
        ))
        reloj += SERVICIO_MIN
        carga += punto.peso_kg
        anterior = idx
    km = _largo(m, ruta)
    reloj += m[anterior][0] / VELOCIDAD_KMH * 60.0
    return RutaPlan(
        camion_id=camion.id, paradas=paradas, distancia_km=round(km, 3), carga_kg=round(carga, 2),
        co2_kg=round(km * camion.kg_co2_por_km(), 3), duracion_min=round(reloj, 1),
    )


def _asignar(
    rutas: list[list[int]], pesos: list[float], camiones: list[Camion],
) -> tuple[list[tuple[list[int], Camion]], list[list[int]], list[Camion]]:
    """Cada ruta, de mayor a menor carga, recibe el camión libre más pequeño que la admita."""
    libres = sorted(camiones, key=lambda c: (c.capacidad_kg, c.kg_co2_por_km()))
    asignadas: list[tuple[list[int], Camion]] = []
    sobrantes: list[list[int]] = []
    for ruta in sorted(rutas, key=lambda r: -sum(pesos[i - 1] for i in r)):
        carga = sum(pesos[i - 1] for i in ruta)
        elegido = next((c for c in libres if c.capacidad_kg >= carga), None)
        if elegido is None:
            sobrantes.append(ruta)
            continue
        libres.remove(elegido)
        asignadas.append((ruta, elegido))
    return asignadas, sobrantes, libres


def optimizar(
    puntos: list[Punto],
    camiones: list[Camion],
    deposito: tuple[float, float] = (-12.0464, -77.0428),
    limite_segundos: float = LIMITE_SEGUNDOS_POR_DEFECTO,
    inicio_jornada: datetime | None = None,
) -> ResultadoOptimizacion:
    """Planifica las rutas del día. Los pedidos que no caben en ningún vehículo quedan en `sin_asignar` con su motivo."""
    inicio = time.perf_counter()
    vence = inicio + max(0.1, limite_segundos)
    resultado = ResultadoOptimizacion()
    if not puntos:
        return resultado
    if not camiones:
        resultado.sin_asignar = [(p.id, "No hay vehículos disponibles") for p in puntos]
        return resultado

    capacidad_max = max(c.capacidad_kg for c in camiones)
    cabe = [p for p in puntos if p.peso_kg <= capacidad_max]
    resultado.sin_asignar = [
        (p.id, f"El peso ({p.peso_kg:g} kg) excede la mayor capacidad de la flota ({capacidad_max:g} kg)")
        for p in puntos if p.peso_kg > capacidad_max
    ]
    if not cabe:
        return resultado

    # Ventanas horarias matemáticamente incompatibles: ni yendo directo desde el depósito se llega a tiempo.
    # Se informan como no asignables en lugar de generar una ruta inválida (RF-003, ruta infeliz).
    referencia = inicio_jornada or min((p.ventana_inicio for p in cabe if p.ventana_inicio), default=None)
    if referencia is not None:
        viables = []
        for p in cabe:
            if p.ventana_fin is not None:
                directo = distancia_km(deposito[0], deposito[1], p.latitud, p.longitud) / VELOCIDAD_KMH * 60.0
                llegada = referencia + timedelta(minutes=directo)
                if p.ventana_inicio is not None and llegada < p.ventana_inicio:
                    llegada = p.ventana_inicio
                if llegada > p.ventana_fin:
                    motivo = (
                        f"Ventana horaria incompatible: llegaría a las {llegada:%H:%M} "
                        f"y la ventana cierra a las {p.ventana_fin:%H:%M}"
                    )
                    resultado.sin_asignar.append((p.id, motivo))
                    continue
            viables.append(p)
        cabe = viables
        if not cabe:
            return resultado

    m = _matriz(deposito, cabe)
    pesos = [p.peso_kg for p in cabe]

    # Se construye con la mayor capacidad libre y se asigna; lo que no cabe en los vehículos restantes se vuelve a
    # planificar con la capacidad que queda, hasta cubrir todo o quedarse sin vehículos.
    pendientes = list(range(1, len(cabe) + 1))
    libres = list(camiones)
    asignadas: list[tuple[list[int], Camion]] = []
    agotado = False
    while pendientes and libres:
        capacidad = max(c.capacidad_kg for c in libres)
        elegibles = [i for i in pendientes if pesos[i - 1] <= capacidad]
        if not elegibles:
            break
        rutas, tiempo_cw = _clarke_wright(m, pesos, elegibles, capacidad, vence)
        mejoradas: list[list[int]] = []
        for ruta in rutas:
            mejor, tiempo_agotado = _dos_opt(m, ruta, vence)
            agotado = agotado or tiempo_cw or tiempo_agotado
            mejoradas.append(mejor)
        nuevas, sobrantes, libres = _asignar(mejoradas, pesos, libres)
        if not nuevas:
            break
        asignadas.extend(nuevas)
        usados = {i for ruta, _ in nuevas for i in ruta}
        pendientes = [i for i in pendientes if i not in usados]

    for idx in pendientes:
        motivo = (
            "No hay más vehículos disponibles para cubrir todas las rutas"
            if not libres else
            f"El peso ({pesos[idx - 1]:g} kg) excede la capacidad de los vehículos que quedan libres"
        )
        resultado.sin_asignar.append((cabe[idx - 1].id, motivo))

    for ruta, camion in asignadas:
        resultado.rutas.append(_evaluar(m, ruta, cabe, camion, inicio_jornada))
    resultado.rutas.sort(key=lambda r: -r.carga_kg)

    resultado.distancia_total_km = round(sum(r.distancia_km for r in resultado.rutas), 3)
    resultado.co2_total_kg = round(sum(r.co2_kg for r in resultado.rutas), 3)

    # Línea base: un viaje de ida y vuelta por cada pedido atendido, con la emisión media de los vehículos usados.
    atendidos = {pid.punto_id for r in resultado.rutas for pid in r.paradas}
    indice = {p.id: i + 1 for i, p in enumerate(cabe)}
    usados = [c for _, c in asignadas] or camiones
    emision_media = sum(c.kg_co2_por_km() for c in usados) / len(usados)
    resultado.distancia_base_km = round(sum(2 * m[0][indice[pid]] for pid in atendidos), 3)
    resultado.co2_base_kg = round(resultado.distancia_base_km * emision_media, 3)

    resultado.limite_alcanzado = agotado
    resultado.tiempo_ms = round((time.perf_counter() - inicio) * 1000.0, 1)
    return resultado
