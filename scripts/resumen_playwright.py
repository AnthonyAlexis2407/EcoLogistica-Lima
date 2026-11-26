"""Resume los resultados de Playwright en tablas Markdown (para el informe y para el resumen de GitHub Actions).

Lee `test-results/resultados.json` (reportero JSON) y `test-results/metricas/*.json` (Web Vitals, tiempos de la API y uptime
que escriben las pruebas de rendimiento y disponibilidad).

Uso:
    python scripts/resumen_playwright.py [carpeta_resultados] [--anotaciones]

    carpeta_resultados   carpeta `test-results` (por defecto src/frontend/test-results)
    --anotaciones        además imprime una línea `::notice` de GitHub Actions con todo el resumen, para que
                         quede visible en la ejecución del flujo
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ORDEN = ["chromium", "firefox", "webkit", "rutas-chromium", "conductor-chromium", "rutas-firefox", "conductor-firefox", "rutas-webkit", "conductor-webkit", "movil", "smoke"]
SALIDA: list[str] = []


def emitir(texto: str = "") -> None:
    SALIDA.append(texto)
    print(texto)


def recorrer(suite: dict, archivo: str = ""):
    archivo = suite.get("file") or archivo
    for spec in suite.get("specs", []):
        for prueba in spec.get("tests", []):
            yield archivo, spec["title"], prueba
    for hija in suite.get("suites", []):
        yield from recorrer(hija, archivo)


def estado(prueba: dict) -> str:
    """passed, failed, flaky (pasó tras reintento) o skipped."""
    return {"expected": "passed", "unexpected": "failed", "flaky": "flaky", "skipped": "skipped"}.get(prueba.get("status"), "failed")


def mensaje_de_error(prueba: dict) -> str:
    for resultado in reversed(prueba.get("results", [])):
        error = resultado.get("error") or (resultado.get("errors") or [{}])[0]
        texto = (error or {}).get("message", "")
        if texto:
            return " ".join(texto.split())[:300]
    return ""


def cifra(valor) -> str:
    return "n/d" if valor is None else f"{valor:.0f}"


def tabla_de_resultados(datos: dict) -> None:
    por_proyecto: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    por_archivo: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    duracion: dict[str, float] = defaultdict(float)
    fallos: list[str] = []
    for suite in datos.get("suites", []):
        for archivo, titulo, prueba in recorrer(suite):
            proyecto = prueba.get("projectName", "?")
            if proyecto == "setup":
                continue
            e = estado(prueba)
            por_proyecto[proyecto][e] += 1
            por_archivo[(archivo, proyecto)][e] += 1
            duracion[proyecto] += sum(r.get("duration", 0) for r in prueba.get("results", []))
            if e == "failed":
                fallos.append(f"[{proyecto}] {archivo} › {titulo}: {mensaje_de_error(prueba)}")

    proyectos = sorted(por_proyecto, key=lambda p: ORDEN.index(p) if p in ORDEN else 99)
    emitir("### Resultados por navegador\n")
    emitir("| Navegador | Pruebas | Pasan | Fallan | Inestables | Omitidas | Éxito | Duración |")
    emitir("|---|---|---|---|---|---|---|---|")
    total: dict[str, int] = defaultdict(int)
    for p in proyectos:
        c = por_proyecto[p]
        n = sum(c.values())
        for k, v in c.items():
            total[k] += v
        emitir(f"| {p} | {n} | {c['passed']} | {c['failed']} | {c['flaky']} | {c['skipped']} | "
               f"{(c['passed'] + c['flaky']) / n * 100:.1f} % | {duracion[p] / 1000:.0f} s |")
    n = sum(total.values())
    emitir(f"| **Total** | **{n}** | **{total['passed']}** | **{total['failed']}** | **{total['flaky']}** | **{total['skipped']}** | "
           f"**{(total['passed'] + total['flaky']) / n * 100:.1f} %** | |")

    emitir("\n### Resultados por archivo de pruebas (pasan / total)\n")
    emitir("| Archivo | " + " | ".join(proyectos) + " |")
    emitir("|---|" + "---|" * len(proyectos))
    for archivo in sorted({a for a, _ in por_archivo}):
        celdas = []
        for p in proyectos:
            c = por_archivo.get((archivo, p))
            celdas.append("—" if not c else f"{c['passed'] + c['flaky']}/{sum(c.values())}")
        emitir(f"| `{archivo}` | " + " | ".join(celdas) + " |")

    if fallos:
        emitir("\n### Pruebas que fallan\n")
        for f in fallos:
            emitir(f"- {f}")


def tablas_de_metricas(carpeta: Path) -> None:
    metricas = carpeta / "metricas"
    if not metricas.exists():
        return
    vitals = sorted(metricas.glob("*-webvitals.json"))
    if vitals:
        emitir("\n### Web Vitals de la pantalla de inicio de sesión (ms; CLS sin unidad)\n")
        emitir("| Navegador | TTFB | FCP | LCP | CLS | DOM cargado | Carga total | Bytes |")
        emitir("|---|---|---|---|---|---|---|---|")
        for ruta in vitals:
            m = json.loads(ruta.read_text(encoding="utf-8"))
            emitir(f"| {m['navegador']} | {cifra(m['ttfb'])} | {cifra(m['fcp'])} | {cifra(m['lcp'])} | {m['cls']:.3f} | "
                   f"{cifra(m['dominCargado'])} | {cifra(m['carga'])} | {m['bytesTransferidos']} |")

    apis = sorted(metricas.glob("*-api.json"))
    if apis:
        emitir("\n### Tiempos de respuesta de la API (ms; 15 repeticiones por ruta)\n")
        emitir("| Navegador | Ruta | Mediana | p95 | Máximo | Estados |")
        emitir("|---|---|---|---|---|---|")
        for ruta in apis:
            m = json.loads(ruta.read_text(encoding="utf-8"))
            for endpoint, d in m["resumen"].items():
                emitir(f"| {m['navegador']} | `{endpoint}` | {d['mediana']} | {d['p95']} | {d['maximo']} | {d['estados']} |")

    ups = sorted(metricas.glob("*-uptime.json"))
    if ups:
        emitir("\n### Uptime: sondeos a /api/health\n")
        emitir("| Navegador | Sondeos | Correctos | Disponibilidad | Latencia mediana (ms) | Latencia máxima (ms) |")
        emitir("|---|---|---|---|---|---|")
        for ruta in ups:
            m = json.loads(ruta.read_text(encoding="utf-8"))
            emitir(f"| {m['navegador']} | {m['sondeos']} | {m['correctos']} | {m['disponibilidadPorcentaje']:.1f} % | "
                   f"{m['latenciaMedianaMs']} | {m['latenciaMaximaMs']} |")

    optimizaciones = sorted(metricas.glob("*-optimizacion.json"))
    if optimizaciones:
        emitir("\n### Motor de rutas frente al SLA de 45 s (RNF-001); cada corrida incluye 50 pedidos propios y los pendientes previos\n")
        emitir("| Navegador | Pedidos | Rutas | Sin asignar | Cálculo (ms) | Respuesta HTTP (ms) | Ahorro de km | Ahorro de CO₂ | CO₂ evitado (kg) |")
        emitir("|---|---|---|---|---|---|---|---|---|")
        for ruta in optimizaciones:
            m = json.loads(ruta.read_text(encoding="utf-8"))
            emitir(f"| {m['navegador']} | {m['pedidos']} | {m['rutas']} | {m['sinAsignar']} | {m['tiempoCalculoMs']} | "
                   f"{m['tiempoRespuestaMs']} | {m['ahorroKmPct']} % | {m['ahorroCo2Pct']} % | {m['co2EvitadoKg']} |")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    carpeta = Path(args[0]) if args else Path("src/frontend/test-results")
    datos = json.loads((carpeta / "resultados.json").read_text(encoding="utf-8"))

    tabla_de_resultados(datos)
    tablas_de_metricas(carpeta)

    if "--anotaciones" in sys.argv:
        texto = "\n".join(SALIDA).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::notice title=Resumen completo de Playwright::{texto}")


if __name__ == "__main__":
    main()
