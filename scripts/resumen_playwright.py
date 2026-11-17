"""Resume los resultados de Playwright en tablas Markdown (para el informe y para el resumen de GitHub Actions).

Lee `test-results/resultados.json` (reportero JSON) y `test-results/metricas/*.json` (Web Vitals, tiempos de la API y uptime
que escriben las pruebas de rendimiento y disponibilidad).

Uso:
    python scripts/resumen_playwright.py [carpeta_resultados] [--anotaciones]

    carpeta_resultados   carpeta `test-results` (por defecto src/frontend/test-results)
    --anotaciones        además imprime líneas `::notice` de GitHub Actions con los totales por navegador
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def recorrer(suite: dict, archivo: str = ""):
    archivo = suite.get("file") or archivo
    for spec in suite.get("specs", []):
        for prueba in spec.get("tests", []):
            yield archivo, spec["title"], prueba
    for hija in suite.get("suites", []):
        yield from recorrer(hija, archivo)


def estado(prueba: dict) -> str:
    """passed, failed, flaky (pasó tras reintento) o skipped."""
    resultado = prueba.get("status")  # expected | unexpected | flaky | skipped
    return {"expected": "passed", "unexpected": "failed", "flaky": "flaky", "skipped": "skipped"}.get(resultado, "failed")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    anotar = "--anotaciones" in sys.argv
    carpeta = Path(args[0]) if args else Path("src/frontend/test-results")
    datos = json.loads((carpeta / "resultados.json").read_text(encoding="utf-8"))

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
                fallos.append(f"[{proyecto}] {archivo} › {titulo}")

    orden = ["chromium", "firefox", "webkit", "movil", "smoke"]
    proyectos = sorted(por_proyecto, key=lambda p: orden.index(p) if p in orden else 99)

    print("### Resultados por navegador\n")
    print("| Navegador | Pruebas | Pasan | Fallan | Inestables | Omitidas | Éxito | Duración |")
    print("|---|---|---|---|---|---|---|---|")
    total = defaultdict(int)
    for p in proyectos:
        c = por_proyecto[p]
        n = sum(c.values())
        ok = c["passed"] + c["flaky"]
        for k, v in c.items():
            total[k] += v
        print(f"| {p} | {n} | {c['passed']} | {c['failed']} | {c['flaky']} | {c['skipped']} | {ok / n * 100:.1f} % | {duracion[p] / 1000:.0f} s |")
        if anotar:
            print(f"::notice title=Playwright {p}::{n} pruebas, {c['passed']} pasan, {c['failed']} fallan, {c['flaky']} inestables, "
                  f"{c['skipped']} omitidas; éxito {ok / n * 100:.1f} %")
    n = sum(total.values())
    ok = total["passed"] + total["flaky"]
    print(f"| **Total** | **{n}** | **{total['passed']}** | **{total['failed']}** | **{total['flaky']}** | **{total['skipped']}** | "
          f"**{ok / n * 100:.1f} %** | |")

    print("\n### Resultados por archivo de pruebas (pasan / total)\n")
    archivos = sorted({a for a, _ in por_archivo})
    print("| Archivo | " + " | ".join(proyectos) + " |")
    print("|---|" + "---|" * len(proyectos))
    for a in archivos:
        celdas = []
        for p in proyectos:
            c = por_archivo.get((a, p))
            celdas.append("—" if not c else f"{c['passed'] + c['flaky']}/{sum(c.values())}")
        print(f"| `{a}` | " + " | ".join(celdas) + " |")

    if fallos:
        print("\n### Pruebas que fallan\n")
        for f in fallos:
            print(f"- {f}")

    metricas = carpeta / "metricas"
    vitals = sorted(metricas.glob("*-webvitals.json")) if metricas.exists() else []
    if vitals:
        print("\n### Web Vitals de la pantalla de inicio de sesión (ms; CLS sin unidad)\n")
        print("| Navegador | TTFB | FCP | LCP | CLS | DOM cargado | Carga total | Bytes |")
        print("|---|---|---|---|---|---|---|---|")
        for ruta in vitals:
            m = json.loads(ruta.read_text(encoding="utf-8"))
            f = lambda v: "n/d" if v is None else f"{v:.0f}"  # noqa: E731
            print(f"| {m['navegador']} | {f(m['ttfb'])} | {f(m['fcp'])} | {f(m['lcp'])} | {m['cls']:.3f} | "
                  f"{f(m['dominCargado'])} | {f(m['carga'])} | {m['bytesTransferidos']} |")
            if anotar:
                print(f"::notice title=Web Vitals {m['navegador']}::TTFB {f(m['ttfb'])} ms, FCP {f(m['fcp'])} ms, "
                      f"LCP {f(m['lcp'])} ms, CLS {m['cls']:.3f}")

    apis = sorted(metricas.glob("*-api.json")) if metricas.exists() else []
    if apis:
        print("\n### Tiempos de respuesta de la API (ms; 15 repeticiones por ruta)\n")
        print("| Navegador | Ruta | Mediana | p95 | Máximo | Estados |")
        print("|---|---|---|---|---|---|")
        for ruta in apis:
            m = json.loads(ruta.read_text(encoding="utf-8"))
            for endpoint, d in m["resumen"].items():
                print(f"| {m['navegador']} | `{endpoint}` | {d['mediana']} | {d['p95']} | {d['maximo']} | {d['estados']} |")
                if anotar:
                    print(f"::notice title=API {m['navegador']} {endpoint}::mediana {d['mediana']} ms, p95 {d['p95']} ms, máx {d['maximo']} ms")

    ups = sorted(metricas.glob("*-uptime.json")) if metricas.exists() else []
    if ups:
        print("\n### Uptime: sondeos a /api/health\n")
        print("| Navegador | Sondeos | Correctos | Disponibilidad | Latencia mediana (ms) | Latencia máxima (ms) |")
        print("|---|---|---|---|---|---|")
        for ruta in ups:
            m = json.loads(ruta.read_text(encoding="utf-8"))
            print(f"| {m['navegador']} | {m['sondeos']} | {m['correctos']} | {m['disponibilidadPorcentaje']:.1f} % | "
                  f"{m['latenciaMedianaMs']} | {m['latenciaMaximaMs']} |")
            if anotar:
                print(f"::notice title=Uptime {m['navegador']}::{m['disponibilidadPorcentaje']:.1f} % en {m['sondeos']} sondeos, "
                      f"mediana {m['latenciaMedianaMs']} ms")


if __name__ == "__main__":
    main()
