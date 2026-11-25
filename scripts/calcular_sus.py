"""Calcula la puntuación SUS (System Usability Scale) a partir de un CSV con respuestas REALES.

Uso:
    python scripts/calcular_sus.py "docs/03 Inplementación/Etapa final/datos/respuestas_sus.csv"

Formato del CSV (una fila por participante, 10 respuestas de 1 a 5):
    participante,perfil,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10

Cálculo (Brooke, 1996):
    - Ítems impares (1,3,5,7,9) aportan (respuesta - 1).
    - Ítems pares (2,4,6,8,10) aportan (5 - respuesta).
    - SUS individual = suma de las 10 aportaciones x 2,5  (rango 0 a 100).
    - SUS global = media de los SUS individuales. Umbral de aceptación: 68.

La salida es Markdown listo para pegar en el documento de usabilidad.
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

UMBRAL = 68.0
PREGUNTAS = 10


def aportaciones(respuestas: list[int]) -> list[int]:
    """Aportación de cada ítem (0 a 4) según la regla de Brooke."""
    return [(r - 1) if (i % 2 == 0) else (5 - r) for i, r in enumerate(respuestas)]


def puntuacion(respuestas: list[int]) -> float:
    return sum(aportaciones(respuestas)) * 2.5


def calificacion(sus: float) -> tuple[str, str]:
    """Nota por letra (curva de Sauro y Lewis, 2016) y adjetivo (Bangor, Kortum y Miller, 2009)."""
    letras = [
        (84.1, "A+"), (80.8, "A"), (78.9, "A-"), (77.2, "B+"), (74.1, "B"), (72.6, "B-"),
        (71.1, "C+"), (65.0, "C"), (62.7, "C-"), (51.7, "D"), (0.0, "F"),
    ]
    letra = next(letra for minimo, letra in letras if sus >= minimo)
    if sus >= 85.5:
        adjetivo = "Excelente"
    elif sus >= 71.4:
        adjetivo = "Bueno"
    elif sus >= 50.9:
        adjetivo = "Aceptable (OK)"
    elif sus >= 35.7:
        adjetivo = "Pobre"
    else:
        adjetivo = "Pésimo"
    return letra, adjetivo


def leer(ruta: Path) -> list[dict]:
    filas = []
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        for n, fila in enumerate(csv.DictReader(f), start=2):
            try:
                resp = [int(fila[f"p{i}"]) for i in range(1, PREGUNTAS + 1)]
            except (KeyError, ValueError) as error:
                raise SystemExit(f"Fila {n}: faltan o no son números las columnas p1..p10 ({error}).") from error
            if any(r < 1 or r > 5 for r in resp):
                raise SystemExit(f"Fila {n}: las respuestas deben estar entre 1 y 5.")
            filas.append({"participante": fila["participante"], "perfil": fila.get("perfil", ""), "resp": resp})
    if len(filas) < 5:
        raise SystemExit(f"Se necesitan al menos 5 participantes (hay {len(filas)}).")
    return filas


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    filas = leer(Path(sys.argv[1]))
    puntos = [puntuacion(f["resp"]) for f in filas]
    media = statistics.mean(puntos)
    desviacion = statistics.stdev(puntos) if len(puntos) > 1 else 0.0
    letra, adjetivo = calificacion(media)

    print("### Matriz de respuestas\n")
    print("| Participante | Perfil | " + " | ".join(f"P{i}" for i in range(1, 11)) + " |")
    print("|---|---|" + "---|" * 10)
    for f in filas:
        print(f"| {f['participante']} | {f['perfil']} | " + " | ".join(str(r) for r in f["resp"]) + " |")

    print("\n### Aportación de cada ítem y SUS individual\n")
    print("| Participante | " + " | ".join(f"P{i}" for i in range(1, 11)) + " | Suma | SUS (suma × 2,5) |")
    print("|---|" + "---|" * 10 + "---|---|")
    for f, sus in zip(filas, puntos, strict=True):
        ap = aportaciones(f["resp"])
        print(f"| {f['participante']} | " + " | ".join(str(a) for a in ap) + f" | {sum(ap)} | **{sus:g}** |")

    print("\n### Resultado global\n")
    print("| Indicador | Valor |\n|---|---|")
    print(f"| Participantes (n) | {len(filas)} |")
    print(f"| SUS medio | **{media:.1f}** |")
    print(f"| Desviación estándar | {desviacion:.1f} |")
    print(f"| Mínimo / máximo | {min(puntos):g} / {max(puntos):g} |")
    print(f"| Umbral de aceptación | {UMBRAL:g} |")
    print(f"| ¿Supera el umbral? | {'Sí' if media >= UMBRAL else 'No'} |")
    print(f"| Calificación | {letra} ({adjetivo}) |")

    print("\n### Promedio por pregunta (1 a 5)\n")
    print("| Pregunta | Promedio | Aportación media (0 a 4) |\n|---|---|---|")
    for i in range(PREGUNTAS):
        prom = statistics.mean(f["resp"][i] for f in filas)
        aport = statistics.mean(aportaciones(f["resp"])[i] for f in filas)
        print(f"| P{i + 1} | {prom:.1f} | {aport:.1f} |")


if __name__ == "__main__":
    main()
