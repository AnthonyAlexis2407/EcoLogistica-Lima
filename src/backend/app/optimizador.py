"""
Motor de optimización de rutas (RF-003, RF-007, EN-001, RNF-001, RNF-009).

Resuelve el problema de rutas de vehículos con capacidad y ventanas horarias (CVRPTW) para la última milla de Lima:

1. **Construcción** con el algoritmo de ahorros de Clarke y Wright (1964): parte de un viaje por pedido y fusiona rutas
   mientras el ahorro de distancia sea positivo y la ruta resultante cumpla TODAS las restricciones duras.
2. **Mejora local** con 2-opt dentro de cada ruta, con un límite de tiempo (por defecto 40 s, por debajo del SLA de 45 s).
   Un cambio solo se acepta si reduce la distancia y la ruta sigue cumpliendo las restricciones duras.
3. **Asignación** de cada ruta al vehículo disponible de menor capacidad que la admita, a igualdad el de menor emisión.
4. **Evaluación**: kilómetros, horas de llegada (con espera si se llega antes de la ventana) y emisiones de CO₂ frente a
   una línea base sin optimizar (un viaje de ida y vuelta por pedido).

Restricciones duras:
- Capacidad de peso y de volumen del vehículo (RN-004).
- Ventana horaria de cada pedido: no se llega después de que cierre; si se llega antes, se espera (RF-003).
- Zonas protegidas (RN-003): ninguna ruta atraviesa una zona; un tramo que la cruzaría se rodea (tangentes y arco, con su
  distancia real) y un destino dentro de una zona no se asigna.

Rendimiento (RNF-009): la matriz de distancias y los planes idénticos se guardan en una caché acotada, de modo que repetir
una consulta no vuelve a consumir CPU.

Alcance declarado: la distancia es en línea recta (haversine) y no por la red vial. El módulo es Python puro y no depende
de FastAPI ni de la base de datos, de modo que se prueba de forma aislada.
"""

from __future__ import annotations

import copy
import math
import time
from collections import OrderedDict
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone

RADIO_TIERRA_KM = 6371.0088
VELOCIDAD_KMH = 25.0  # velocidad media urbana supuesta para Lima (parametrizable, ver `Parametros`)
SERVICIO_MIN = 10.0  # minutos de descarga por parada (parametrizable)
LIMITE_SEGUNDOS_POR_DEFECTO = 40.0  # SLA de RNF-001: 45 s
PROHIBIDO = 1.0e6  # "distancia" de un tramo que cruza una zona protegida: ninguna ruta lo usa

# Rendimiento supuesto (km por litro) y factor de emisión (kg de CO₂ por litro) por combustible.
# Fuente de los factores: los de referencia del seed del proyecto (Documento 11); son supuestos del proyecto.
CONSUMO_KM_POR_LITRO = {"DIESEL": 7.0, "GASOLINA": 8.0, "GLP": 7.5, "HIBRIDO": 14.0, "ELECTRICO": 0.0}
FACTOR_CO2_KG_POR_LITRO = {"DIESEL": 2.68, "GASOLINA": 2.31, "GLP": 1.51, "HIBRIDO": 1.10, "ELECTRICO": 0.0}

# Un árbol maduro absorbe en promedio 21,77 kg de CO₂ al año (equivalencia usada para comunicar la compensación, RF-010).
KG_CO2_POR_ARBOL_AL_ANIO = 21.77


@dataclass(frozen=True)
class Parametros:
    """Parámetros del algoritmo que el administrador puede ajustar (RF-001 del módulo de administración)."""

    velocidad_kmh: float = VELOCIDAD_KMH
    servicio_min: float = SERVICIO_MIN
    # "clarke_wright_2opt" (por defecto) o "tabu": suma una búsqueda tabú entre rutas (ver algoritmos_alternativos.py).
    algoritmo: str = "clarke_wright_2opt"


@dataclass(frozen=True)
class Zona:
    """Zona protegida circular (RN-003): reserva ecológica o área natural protegida."""

    nombre: str
    latitud: float
    longitud: float
    radio_km: float


@dataclass(frozen=True)
class Punto:
    """Una entrega: ubicación, peso, volumen y ventana horaria opcional."""

    id: str
    latitud: float
    longitud: float
    peso_kg: float
    ventana_inicio: datetime | None = None
    ventana_fin: datetime | None = None
    volumen_m3: float = 0.0


@dataclass(frozen=True)
class Camion:
    """Un vehículo disponible."""

    id: str
    placa: str
    capacidad_kg: float
    combustible: str = "DIESEL"
    factor_co2: float | None = None  # kg de CO₂ por litro; si falta se usa el de la tabla
    volumen_m3: float | None = None  # None: sin límite de volumen registrado

    def kg_co2_por_km(self) -> float:
        """Emisión por kilómetro recorrido (0 para vehículos eléctricos)."""
        consumo = CONSUMO_KM_POR_LITRO.get(self.combustible, CONSUMO_KM_POR_LITRO["DIESEL"])
        if consumo <= 0:
            return 0.0
        factor = self.factor_co2 if self.factor_co2 is not None else FACTOR_CO2_KG_POR_LITRO.get(self.combustible, 2.68)
        return factor / consumo

    @property
    def volumen_max(self) -> float:
        return math.inf if self.volumen_m3 is None else self.volumen_m3


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
    volumen_m3: float = 0.0
    distancia_base_km: float = 0.0  # un viaje de ida y vuelta por pedido de esta ruta
    co2_base_kg: float = 0.0


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
    desde_cache: bool = False

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


def como_utc(valor: datetime | None) -> datetime | None:
    """Fechas sin zona horaria (las devuelve SQLite) se interpretan como UTC; las demás se dejan igual."""
    if valor is None or valor.tzinfo is not None:
        return valor
    return valor.replace(tzinfo=timezone.utc)


# ──────────────────────────────────────────────────────────────────────────
#  Zonas protegidas (RN-003)
# ──────────────────────────────────────────────────────────────────────────

def _proyectar(zona: Zona, lat: float, lon: float) -> tuple[float, float]:
    """Coordenadas planas (km) respecto al centro de la zona; suficiente para distancias urbanas."""
    x = math.radians(lon - zona.longitud) * RADIO_TIERRA_KM * math.cos(math.radians(zona.latitud))
    y = math.radians(lat - zona.latitud) * RADIO_TIERRA_KM
    return x, y


def _segmento_toca_zona(ax: float, ay: float, bx: float, by: float, radio: float) -> bool:
    """¿El segmento AB (con el centro de la zona en el origen) entra al círculo de ese radio?"""
    if (ax < -radio and bx < -radio) or (ax > radio and bx > radio) or (ay < -radio and by < -radio) \
            or (ay > radio and by > radio):
        return False
    dx, dy = bx - ax, by - ay
    largo2 = dx * dx + dy * dy
    t = 0.0 if largo2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / largo2))
    cx, cy = ax + t * dx, ay + t * dy
    return cx * cx + cy * cy < radio * radio


def _rodeo_km(radio: float, a: tuple[float, float], b: tuple[float, float]) -> float:
    """
    Largo del camino más corto de A a B rodeando un círculo de `radio` centrado en el origen (A y B fuera del círculo):
    tangente desde A, arco sobre la circunferencia y tangente hasta B.
    """
    da, db = math.hypot(*a), math.hypot(*b)
    theta = math.acos(max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (da * db))))
    alfa, beta = math.acos(min(1.0, radio / da)), math.acos(min(1.0, radio / db))
    arco = max(0.0, theta - alfa - beta)
    return math.sqrt(max(0.0, da * da - radio * radio)) + math.sqrt(max(0.0, db * db - radio * radio)) + radio * arco


def zona_que_contiene(zonas: tuple[Zona, ...] | list[Zona], lat: float, lon: float) -> Zona | None:
    for z in zonas:
        if distancia_km(z.latitud, z.longitud, lat, lon) < z.radio_km:
            return z
    return None


def zona_que_cruza(zonas: tuple[Zona, ...] | list[Zona], a: tuple[float, float], b: tuple[float, float]) -> Zona | None:
    for z in zonas:
        ax, ay = _proyectar(z, *a)
        bx, by = _proyectar(z, *b)
        if _segmento_toca_zona(ax, ay, bx, by, z.radio_km):
            return z
    return None


# ──────────────────────────────────────────────────────────────────────────
#  Matriz de distancias con caché (RNF-009)
# ──────────────────────────────────────────────────────────────────────────

_MATRICES: OrderedDict = OrderedDict()
_MAX_MATRICES = 6
_PLANES: OrderedDict = OrderedDict()
_MAX_PLANES = 24
estadisticas_cache = {"matriz_aciertos": 0, "matriz_fallos": 0, "plan_aciertos": 0, "plan_fallos": 0}


def vaciar_cache() -> None:
    """Descarta las cachés (pruebas y cambios de parámetros del administrador)."""
    _MATRICES.clear()
    _PLANES.clear()
    for k in estadisticas_cache:
        estadisticas_cache[k] = 0


def _matriz(deposito: tuple[float, float], puntos: list[Punto], zonas: tuple[Zona, ...] = ()) -> list[list[float]]:
    """
    Matriz de distancias; el índice 0 es el depósito y 1..n los puntos. Un tramo recto que atraviesa una zona protegida se
    reemplaza por el rodeo más corto alrededor de ella (RN-003); un punto dentro de una zona vale `PROHIBIDO`.
    """
    coords = [deposito] + [(p.latitud, p.longitud) for p in puntos]
    clave = (tuple(coords), zonas)
    if clave in _MATRICES:
        _MATRICES.move_to_end(clave)
        estadisticas_cache["matriz_aciertos"] += 1
        return _MATRICES[clave]
    estadisticas_cache["matriz_fallos"] += 1
    n = len(coords)
    m = [[0.0] * n for _ in range(n)]
    proyectadas = [[_proyectar(z, lat, lon) for lat, lon in coords] for z in zonas]
    for i in range(n):
        lat_i, lon_i = coords[i]
        fila = m[i]
        for j in range(i + 1, n):
            d = distancia_km(lat_i, lon_i, coords[j][0], coords[j][1])
            for z, proy in zip(zonas, proyectadas, strict=True):
                if not _segmento_toca_zona(proy[i][0], proy[i][1], proy[j][0], proy[j][1], z.radio_km):
                    continue
                if math.hypot(*proy[i]) < z.radio_km or math.hypot(*proy[j]) < z.radio_km:
                    d = PROHIBIDO
                    break
                d = max(d, _rodeo_km(z.radio_km, proy[i], proy[j]))
            fila[j] = d
            m[j][i] = d
    _MATRICES[clave] = m
    while len(_MATRICES) > _MAX_MATRICES:
        _MATRICES.popitem(last=False)
    return m


# ──────────────────────────────────────────────────────────────────────────
#  Problema: restricciones duras
# ──────────────────────────────────────────────────────────────────────────

class _Problema:
    """Datos numéricos del problema y comprobación de factibilidad de una ruta (ventanas, tramos prohibidos)."""

    def __init__(
        self, m: list[list[float]], puntos: list[Punto], referencia: datetime | None, params: Parametros,
        hay_zonas: bool = False,
    ):
        self.m = m
        self.pesos = [p.peso_kg for p in puntos]
        self.volumenes = [p.volumen_m3 for p in puntos]
        self.min_por_km = 60.0 / params.velocidad_kmh
        self.servicio = params.servicio_min
        n = len(puntos)
        self.abre = [0.0] * (n + 1)
        self.cierra = [math.inf] * (n + 1)
        self.hay_ventanas = False
        self.hay_prohibidos = hay_zonas
        if referencia is not None:
            for i, p in enumerate(puntos, start=1):
                if p.ventana_inicio is not None:
                    self.abre[i] = max(0.0, (p.ventana_inicio - referencia).total_seconds() / 60.0)
                if p.ventana_fin is not None:
                    self.cierra[i] = (p.ventana_fin - referencia).total_seconds() / 60.0
                    self.hay_ventanas = True

    @property
    def con_restricciones(self) -> bool:
        return self.hay_ventanas or self.hay_prohibidos

    def factible(self, ruta: list[int]) -> bool:
        """La ruta no usa tramos prohibidos y llega a cada parada antes de que cierre su ventana."""
        m, k, serv = self.m, self.min_por_km, self.servicio
        t = 0.0
        ant = 0
        for idx in ruta:
            d = m[ant][idx]
            if d >= PROHIBIDO:
                return False
            t += d * k
            if t > self.cierra[idx]:
                return False
            if t < self.abre[idx]:
                t = self.abre[idx]
            t += serv
            ant = idx
        return m[ant][0] < PROHIBIDO


# ──────────────────────────────────────────────────────────────────────────
#  Construcción: ahorros de Clarke y Wright
# ──────────────────────────────────────────────────────────────────────────

def _ahorros(m: list[list[float]], indices: list[int]) -> list[tuple[float, int, int]]:
    lista = [
        (m[0][i] + m[0][j] - m[i][j], i, j)
        for pos, i in enumerate(indices) for j in indices[pos + 1:]
    ]
    lista = [a for a in lista if a[0] > 1e-9]
    lista.sort(key=lambda a: a[0], reverse=True)
    return lista


def _clarke_wright(
    prob: _Problema, indices: list[int], capacidad: float, capacidad_vol: float, vence: float,
) -> tuple[list[list[int]], bool]:
    """Rutas (listas de índices 1..n) construidas solo con los puntos de `indices`. Devuelve si se agotó el tiempo."""
    pesos, vols = prob.pesos, prob.volumenes
    ruta_de = {i: [i] for i in indices}  # índice -> lista compartida (ruta)
    carga = {id(r): (pesos[i - 1], vols[i - 1]) for i, r in ruta_de.items()}
    agotado = False
    for contador, (_, i, j) in enumerate(_ahorros(prob.m, indices)):
        if contador % 2000 == 0 and time.perf_counter() > vence:
            agotado = True
            break
        ri, rj = ruta_de[i], ruta_de[j]
        if ri is rj:
            continue
        peso = carga[id(ri)][0] + carga[id(rj)][0]
        volumen = carga[id(ri)][1] + carga[id(rj)][1]
        if peso > capacidad or volumen > capacidad_vol:
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
        if prob.con_restricciones and not prob.factible(nueva):
            continue
        carga.pop(id(ri), None)
        carga.pop(id(rj), None)
        carga[id(nueva)] = (peso, volumen)
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


def _dos_opt(prob: _Problema, ruta: list[int], vence: float) -> tuple[list[int], bool]:
    """Invierte tramos mientras reduzcan la distancia y mantengan la factibilidad; se detiene al llegar al límite."""
    m = prob.m
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
                    candidata = mejor[:i] + mejor[i:j + 1][::-1] + mejor[j + 1:]
                    if prob.con_restricciones and not prob.factible(candidata):
                        continue
                    mejor = candidata
                    mejoro = True
    return mejor, False


# ──────────────────────────────────────────────────────────────────────────
#  Evaluación y asignación
# ──────────────────────────────────────────────────────────────────────────

def _evaluar(
    prob: _Problema, ruta: list[int], puntos: list[Punto], camion: Camion, inicio_jornada: datetime | None,
) -> RutaPlan:
    """Calcula kilómetros, llegadas (con espera), cumplimiento de ventanas y CO₂ de una ruta ya ordenada."""
    m = prob.m
    reloj = 0.0  # minutos desde el inicio de la jornada
    anterior = 0
    paradas: list[ParadaPlan] = []
    carga = 0.0
    volumen = 0.0
    for orden, idx in enumerate(ruta, start=1):
        punto = puntos[idx - 1]
        tramo = m[anterior][idx]
        reloj += tramo * prob.min_por_km
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
        reloj += prob.servicio
        carga += punto.peso_kg
        volumen += punto.volumen_m3
        anterior = idx
    km = _largo(m, ruta)
    reloj += m[anterior][0] * prob.min_por_km
    base_km = sum(2 * m[0][idx] for idx in ruta)
    return RutaPlan(
        camion_id=camion.id, paradas=paradas, distancia_km=round(km, 3), carga_kg=round(carga, 2),
        co2_kg=round(km * camion.kg_co2_por_km(), 3), duracion_min=round(reloj, 1), volumen_m3=round(volumen, 2),
        distancia_base_km=round(base_km, 3), co2_base_kg=round(base_km * camion.kg_co2_por_km(), 3),
    )


def _asignar(
    rutas: list[list[int]], pesos: list[float], vols: list[float], camiones: list[Camion],
) -> tuple[list[tuple[list[int], Camion]], list[list[int]], list[Camion]]:
    """Cada ruta, de mayor a menor carga, recibe el camión libre más pequeño que la admita (peso y volumen)."""
    libres = sorted(camiones, key=lambda c: (c.capacidad_kg, c.volumen_max, c.kg_co2_por_km()))
    asignadas: list[tuple[list[int], Camion]] = []
    sobrantes: list[list[int]] = []
    for ruta in sorted(rutas, key=lambda r: -sum(pesos[i - 1] for i in r)):
        carga = sum(pesos[i - 1] for i in ruta)
        volumen = sum(vols[i - 1] for i in ruta)
        elegido = next((c for c in libres if c.capacidad_kg >= carga and c.volumen_max >= volumen), None)
        if elegido is None:
            sobrantes.append(ruta)
            continue
        libres.remove(elegido)
        asignadas.append((ruta, elegido))
    return asignadas, sobrantes, libres


def _normalizar(puntos: list[Punto]) -> list[Punto]:
    return [
        replace(p, ventana_inicio=como_utc(p.ventana_inicio), ventana_fin=como_utc(p.ventana_fin)) for p in puntos
    ]


def optimizar(
    puntos: list[Punto],
    camiones: list[Camion],
    deposito: tuple[float, float] = (-12.0464, -77.0428),
    limite_segundos: float = LIMITE_SEGUNDOS_POR_DEFECTO,
    inicio_jornada: datetime | None = None,
    zonas: tuple[Zona, ...] | list[Zona] = (),
    parametros: Parametros | None = None,
    usar_cache: bool = False,
) -> ResultadoOptimizacion:
    """Planifica las rutas. Los pedidos que no caben o no se pueden servir quedan en `sin_asignar` con su motivo."""
    inicio = time.perf_counter()
    params = parametros or Parametros()
    zonas = tuple(zonas)
    inicio_jornada = como_utc(inicio_jornada)
    puntos = _normalizar(puntos)

    clave = None
    if usar_cache:
        clave = (tuple(puntos), tuple(camiones), tuple(deposito), zonas, params, inicio_jornada)
        if clave in _PLANES:
            _PLANES.move_to_end(clave)
            estadisticas_cache["plan_aciertos"] += 1
            copia = copy.deepcopy(_PLANES[clave])
            copia.desde_cache = True
            copia.tiempo_ms = round((time.perf_counter() - inicio) * 1000.0, 1)
            return copia
        estadisticas_cache["plan_fallos"] += 1

    resultado = _planificar(puntos, camiones, deposito, limite_segundos, inicio_jornada, zonas, params, inicio)
    if clave is not None and not resultado.limite_alcanzado:
        _PLANES[clave] = copy.deepcopy(resultado)
        while len(_PLANES) > _MAX_PLANES:
            _PLANES.popitem(last=False)
    return resultado


def _planificar(
    puntos: list[Punto], camiones: list[Camion], deposito: tuple[float, float], limite_segundos: float,
    inicio_jornada: datetime | None, zonas: tuple[Zona, ...], params: Parametros, inicio: float,
) -> ResultadoOptimizacion:
    vence = inicio + max(0.1, limite_segundos)
    resultado = ResultadoOptimizacion()
    if not puntos:
        return resultado
    if not camiones:
        resultado.sin_asignar = [(p.id, "No hay vehículos disponibles") for p in puntos]
        return resultado

    capacidad_max = max(c.capacidad_kg for c in camiones)
    volumen_max = max(c.volumen_max for c in camiones)
    cabe: list[Punto] = []
    for p in puntos:
        if p.peso_kg > capacidad_max:
            motivo = f"El peso ({p.peso_kg:g} kg) excede la mayor capacidad de la flota ({capacidad_max:g} kg)"
        elif p.volumen_m3 > volumen_max:
            motivo = f"El volumen ({p.volumen_m3:g} m³) excede el mayor volumen de la flota ({volumen_max:g} m³)"
        elif (zona := zona_que_contiene(zonas, p.latitud, p.longitud)) is not None:
            motivo = f"El destino está dentro de la zona protegida «{zona.nombre}» (RN-003)"
        else:
            cabe.append(p)
            continue
        resultado.sin_asignar.append((p.id, motivo))
    if not cabe:
        return resultado

    # Ventanas horarias matemáticamente incompatibles: ni yendo directo desde el depósito se llega a tiempo.
    # Se informan como no asignables en lugar de generar una ruta inválida (RF-003, ruta infeliz).
    referencia = inicio_jornada or min((p.ventana_inicio for p in cabe if p.ventana_inicio), default=None)
    if referencia is not None:
        viables = []
        for p in cabe:
            if p.ventana_fin is not None:
                directo = distancia_km(deposito[0], deposito[1], p.latitud, p.longitud) / params.velocidad_kmh * 60.0
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

    m = _matriz(deposito, cabe, zonas)
    prob = _Problema(m, cabe, referencia, params, hay_zonas=bool(zonas))
    pesos, vols = prob.pesos, prob.volumenes

    # Se construye con la mayor capacidad libre y se asigna; lo que no cabe en los vehículos restantes se vuelve a
    # planificar con la capacidad que queda, hasta cubrir todo o quedarse sin vehículos.
    pendientes = list(range(1, len(cabe) + 1))
    libres = list(camiones)
    asignadas: list[tuple[list[int], Camion]] = []
    agotado = False
    while pendientes and libres:
        capacidad = max(c.capacidad_kg for c in libres)
        capacidad_vol = max(c.volumen_max for c in libres)
        elegibles = [i for i in pendientes if pesos[i - 1] <= capacidad and vols[i - 1] <= capacidad_vol]
        if not elegibles:
            break
        rutas, tiempo_cw = _clarke_wright(prob, elegibles, capacidad, capacidad_vol, vence)
        mejoradas: list[list[int]] = []
        for ruta in rutas:
            mejor, tiempo_agotado = _dos_opt(prob, ruta, vence)
            agotado = agotado or tiempo_cw or tiempo_agotado
            mejoradas.append(mejor)
        if params.algoritmo == "tabu":
            from app.algoritmos_alternativos import busqueda_tabu  # import diferido: el módulo depende de este

            mejoradas = busqueda_tabu(prob, mejoradas, capacidad, capacidad_vol, vence)
        nuevas, _sobrantes, libres = _asignar(mejoradas, pesos, vols, libres)
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
        resultado.rutas.append(_evaluar(prob, ruta, cabe, camion, inicio_jornada or referencia))
    resultado.rutas.sort(key=lambda r: -r.carga_kg)

    resultado.distancia_total_km = round(sum(r.distancia_km for r in resultado.rutas), 3)
    resultado.co2_total_kg = round(sum(r.co2_kg for r in resultado.rutas), 3)

    # Línea base: un viaje de ida y vuelta por cada pedido atendido, con la emisión media de los vehículos usados.
    atendidos = {pid.punto_id for r in resultado.rutas for pid in r.paradas}
    indice = {p.id: i + 1 for i, p in enumerate(cabe)}
    usados_c = [c for _, c in asignadas] or camiones
    emision_media = sum(c.kg_co2_por_km() for c in usados_c) / len(usados_c)
    resultado.distancia_base_km = round(sum(2 * m[0][indice[pid]] for pid in atendidos), 3)
    resultado.co2_base_kg = round(resultado.distancia_base_km * emision_media, 3)

    resultado.limite_alcanzado = agotado
    if params.algoritmo == "tabu":
        resultado.algoritmo = "Clarke-Wright + 2-opt + Búsqueda tabú"
    resultado.tiempo_ms = round((time.perf_counter() - inicio) * 1000.0, 1)
    return resultado
