"""
Mide el tiempo de recuperación (RTO) ante la caída de una instancia del backend (RNF-003: RTO ≤ 60 s).

Requiere el entorno de `docker-compose.failover.yml` en marcha (dos instancias de la API detrás de un balanceador en el
puerto 8080). El script:

1. Consulta `/api/health/ready` cada 100 ms a través del balanceador durante todo el experimento.
2. Tras 5 s de funcionamiento normal detiene de golpe una instancia (`docker compose kill`).
3. Sigue consultando 15 s más y calcula la interrupción más larga del servicio y la disponibilidad durante la prueba.
4. Hace lo mismo con la otra instancia, una vez recuperada la primera.

El RTO es el tiempo máximo entre dos respuestas correctas consecutivas durante la caída. La prueba falla (código 1) si supera
el límite o si hay peticiones sin respuesta durante más de ese límite. Uso:

    python scripts/medir_rto.py [--url http://localhost:8080] [--limite 60] [--salida resultado-rto.json]
"""

import argparse
import json
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

COMPOSE = ["docker", "compose", "-f", "docker-compose.failover.yml"]


class Sonda(threading.Thread):
    """Hace peticiones cada 100 ms y guarda (instante, éxito)."""

    def __init__(self, url: str):
        super().__init__(daemon=True)
        self.url = url
        self.muestras: list[tuple[float, bool]] = []
        self.detener = threading.Event()

    def run(self) -> None:
        while not self.detener.is_set():
            inicio = time.monotonic()
            try:
                with urllib.request.urlopen(self.url, timeout=3) as respuesta:  # noqa: S310 - URL local de la prueba
                    ok = respuesta.status == 200
            except (urllib.error.URLError, OSError):
                ok = False
            self.muestras.append((inicio, ok))
            self.detener.wait(max(0.0, 0.1 - (time.monotonic() - inicio)))


def interrupcion_maxima(muestras: list[tuple[float, bool]], desde: float, hasta: float) -> float:
    """Mayor intervalo, en segundos, entre dos respuestas correctas consecutivas dentro de [desde, hasta]."""
    exitos = [t for t, ok in muestras if ok and desde - 1 <= t <= hasta]
    if len(exitos) < 2:
        return hasta - desde
    return max(b - a for a, b in zip(exitos, exitos[1:], strict=False))


def disponibilidad(muestras: list[tuple[float, bool]], desde: float, hasta: float) -> float:
    ventana = [ok for t, ok in muestras if desde <= t <= hasta]
    return round(sum(ventana) / len(ventana) * 100.0, 2) if ventana else 0.0


def experimento(sonda: Sonda, servicio: str) -> dict:
    time.sleep(5)  # funcionamiento normal
    inicio = time.monotonic()
    subprocess.run([*COMPOSE, "kill", servicio], check=True, capture_output=True)  # noqa: S603
    time.sleep(15)
    fin = time.monotonic()
    return {
        "instancia_detenida": servicio,
        "rto_s": round(interrupcion_maxima(sonda.muestras, inicio, fin), 3),
        "disponibilidad_pct": disponibilidad(sonda.muestras, inicio, fin),
        "peticiones": len([1 for t, _ in sonda.muestras if inicio <= t <= fin]),
        "fallidas": len([1 for t, ok in sonda.muestras if inicio <= t <= fin and not ok]),
    }


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("--url", default="http://localhost:8080")
    analizador.add_argument("--limite", type=float, default=60.0, help="RTO máximo aceptado, en segundos")
    analizador.add_argument("--salida", default="resultado-rto.json")
    args = analizador.parse_args()

    sonda = Sonda(f"{args.url}/api/health/ready")
    sonda.start()
    resultados = []
    try:
        resultados.append(experimento(sonda, "api1"))
        subprocess.run([*COMPOSE, "up", "-d", "--wait", "api1"], check=True, capture_output=True)  # noqa: S603
        time.sleep(3)
        resultados.append(experimento(sonda, "api2"))
    finally:
        sonda.detener.set()
        sonda.join(timeout=5)

    peor = max(r["rto_s"] for r in resultados)
    informe = {"limite_s": args.limite, "peor_rto_s": peor, "cumple": peor <= args.limite, "experimentos": resultados}
    with open(args.salida, "w", encoding="utf-8") as archivo:
        json.dump(informe, archivo, indent=2, ensure_ascii=False)

    print("| Instancia detenida | RTO (s) | Disponibilidad | Peticiones | Fallidas |")
    print("|---|---|---|---|---|")
    for r in resultados:
        print(f"| {r['instancia_detenida']} | {r['rto_s']} | {r['disponibilidad_pct']} % | {r['peticiones']} | {r['fallidas']} |")
    print(f"\nPeor RTO: {peor} s (límite {args.limite} s): {'CUMPLE' if informe['cumple'] else 'NO CUMPLE'}")
    return 0 if informe["cumple"] else 1


if __name__ == "__main__":
    sys.exit(main())
