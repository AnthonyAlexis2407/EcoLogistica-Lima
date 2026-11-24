"""
Estudio comparativo de algoritmos de rutas (spike EN-001).

Compara, con las mismas instancias, el costo (kilómetros totales) y el tiempo de cuatro enfoques:

1. Clarke-Wright + 2-opt  (el motor base del producto)
2. Clarke-Wright + 2-opt + búsqueda tabú  (alternativa activable desde los parámetros)
3. Algoritmo genético  (rutas gigantes + división por capacidad)
4. Google OR-Tools (búsqueda local guiada), si está instalado: `pip install ortools`. Se usa SOLO en este estudio como
   referencia de calidad; no es una dependencia del producto.

Todos resuelven el mismo problema: pedidos con peso, una flota homogénea de camiones de 1.500 kg, salida y regreso al
depósito, sin ventanas horarias (las ventanas penalizan por igual a todos los enfoques propios y OR-Tools las trata distinto,
por eso aquí se compara la parte común). Las instancias son reproducibles (semillas fijas). Uso:

    python scripts/spike_algoritmos.py [--tamanos 50 150 400] [--semillas 3] [--limite 10] [--salida spike.json]
"""

import argparse
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "backend"))

from app.algoritmos_alternativos import algoritmo_genetico, busqueda_tabu  # noqa: E402
from app.optimizador import Parametros, Punto, _clarke_wright, _dos_opt, _largo, _matriz, _Problema  # noqa: E402

DEPOSITO = (-12.0464, -77.0428)
CAPACIDAD = 1500.0


def instancia(n: int, semilla: int) -> list[Punto]:
    azar = random.Random(semilla)
    return [
        Punto(f"p{i}", DEPOSITO[0] + azar.uniform(-0.12, 0.12), DEPOSITO[1] + azar.uniform(-0.12, 0.12), azar.uniform(20, 150))
        for i in range(n)
    ]


def costo(m, rutas) -> float:
    return sum(_largo(m, r) for r in rutas if r)


def con_cw_2opt(prob, n, limite):
    vence = time.perf_counter() + limite
    rutas, _ = _clarke_wright(prob, list(range(1, n + 1)), CAPACIDAD, math.inf, vence)
    return [_dos_opt(prob, r, vence)[0] for r in rutas]


def con_tabu(prob, n, limite):
    vence = time.perf_counter() + limite
    base = con_cw_2opt(prob, n, limite)
    return busqueda_tabu(prob, base, CAPACIDAD, math.inf, vence)


def con_genetico(prob, n, limite):
    return algoritmo_genetico(prob, list(range(1, n + 1)), CAPACIDAD, math.inf, time.perf_counter() + limite, generaciones=100_000)


def con_ortools(prob, n, limite):
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # type: ignore[import-not-found]

    escala = 1000
    m = prob.m
    vehiculos = math.ceil(sum(prob.pesos) / CAPACIDAD) + 4
    gestor = pywrapcp.RoutingIndexManager(n + 1, vehiculos, 0)
    modelo = pywrapcp.RoutingModel(gestor)
    modelo.SetArcCostEvaluatorOfAllVehicles(
        modelo.RegisterTransitCallback(lambda a, b: int(m[gestor.IndexToNode(a)][gestor.IndexToNode(b)] * escala)),
    )
    demanda = modelo.RegisterUnaryTransitCallback(
        lambda i: 0 if gestor.IndexToNode(i) == 0 else int(prob.pesos[gestor.IndexToNode(i) - 1] * 100),
    )
    modelo.AddDimensionWithVehicleCapacity(demanda, 0, [int(CAPACIDAD * 100)] * vehiculos, True, "Peso")
    parametros = pywrapcp.DefaultRoutingSearchParameters()
    parametros.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    parametros.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    parametros.time_limit.FromSeconds(int(limite))
    solucion = modelo.SolveWithParameters(parametros)
    rutas = []
    for v in range(vehiculos):
        indice, ruta = modelo.Start(v), []
        while not modelo.IsEnd(indice):
            nodo = gestor.IndexToNode(indice)
            if nodo:
                ruta.append(nodo)
            indice = solucion.Value(modelo.NextVar(indice))
        if ruta:
            rutas.append(ruta)
    return rutas


def disponible_ortools() -> bool:
    try:
        import ortools  # noqa: F401
    except ImportError:
        return False
    return True


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("--tamanos", type=int, nargs="+", default=[50, 150, 400])
    analizador.add_argument("--semillas", type=int, default=3)
    analizador.add_argument("--limite", type=float, default=10.0, help="Segundos máximos por algoritmo e instancia")
    analizador.add_argument("--salida", default="spike-algoritmos.json")
    args = analizador.parse_args()

    algoritmos = {
        "Clarke-Wright + 2-opt": con_cw_2opt,
        "+ búsqueda tabú": con_tabu,
        "Algoritmo genético": con_genetico,
    }
    if disponible_ortools():
        algoritmos["OR-Tools (GLS)"] = con_ortools
    resultados: dict[str, dict[int, dict[str, list[float]]]] = {a: {} for a in algoritmos}

    for n in args.tamanos:
        for semilla in range(1, args.semillas + 1):
            puntos = instancia(n, semilla)
            prob = _Problema(_matriz(DEPOSITO, puntos), puntos, None, Parametros())
            for nombre, funcion in algoritmos.items():
                inicio = time.perf_counter()
                rutas = funcion(prob, n, args.limite)
                segundos = time.perf_counter() - inicio
                cubiertos = sorted(i for r in rutas for i in r)
                assert cubiertos == list(range(1, n + 1)), f"{nombre} no cubrió todos los pedidos (n={n})"
                assert all(sum(prob.pesos[i - 1] for i in r) <= CAPACIDAD + 1e-6 for r in rutas), f"{nombre} excedió la capacidad"
                celda = resultados[nombre].setdefault(n, {"km": [], "s": [], "rutas": []})
                celda["km"].append(costo(prob.m, rutas))
                celda["s"].append(segundos)
                celda["rutas"].append(len(rutas))

    base = resultados["Clarke-Wright + 2-opt"]
    print(f"Instancias aleatorias en Lima, camiones de {CAPACIDAD:g} kg, límite de {args.limite:g} s por corrida, "
          f"{args.semillas} semillas por tamaño (se muestra el promedio).\n")
    print("| Pedidos | Algoritmo | Km totales | vs. base | Tiempo (s) | Rutas |")
    print("|---|---|---|---|---|---|")
    for n in args.tamanos:
        referencia = statistics.mean(base[n]["km"])
        for nombre in algoritmos:
            c = resultados[nombre][n]
            km = statistics.mean(c["km"])
            print(f"| {n} | {nombre} | {km:,.1f} | {(km - referencia) / referencia * 100:+.1f} % | "
                  f"{statistics.mean(c['s']):.2f} | {statistics.mean(c['rutas']):.1f} |")
    if "OR-Tools (GLS)" not in algoritmos:
        print("\nOR-Tools no está instalado: ejecute `pip install ortools` para incluirlo en la comparación.")

    with open(args.salida, "w", encoding="utf-8") as archivo:
        json.dump({a: {str(n): v for n, v in d.items()} for a, d in resultados.items()}, archivo, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
