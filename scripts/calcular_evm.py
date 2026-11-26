"""Calcula el Análisis de Valor Ganado (EVM) del proyecto y genera los gráficos de los tableros de cierre.

Uso (desde la raíz del repositorio):
    python scripts/calcular_evm.py              # imprime las tablas en Markdown
    python scripts/calcular_evm.py --graficos   # además escribe los SVG en "docs/04 Cierre/imagenes"

Todos los datos de entrada están en este archivo (sección DATOS) para que el cálculo sea verificable y repetible.

SUPUESTOS DECLARADOS (no existe una bitácora de horas ni costos reales del equipo):
1. Presupuesto hasta la conclusión (BAC): S/ 84.258,75 del Documento 04 de Planificación (sin la reserva de contingencia
   de S/ 10.111,05, que se gestiona aparte).
2. Valor Planificado (PV): el BAC se reparte en proporción a los puntos de historia del backlog (116 puntos) según la
   iteración de la hoja de ruta (Acta de constitución y Artefactos Jira). Las épicas transversales (EL-6, 53 puntos) se
   reparten en partes casi iguales entre las cuatro iteraciones.
3. Valor Ganado (EV): regla de crédito fijo 0/50/100 sobre los puntos de cada ítem del backlog, acreditado en el sprint en
   que sus pruebas lo verifican (Revisiones de Sprint y Matriz de cumplimiento). Un ítem gana el 100 % cuando está
   implementado y sus criterios de aceptación verificables por el equipo se cumplen con pruebas automáticas; gana el 50 % si
   queda implementado pero depende de infraestructura de pago o de validación externa que aún no existe.
   El trabajo de calidad, seguridad, Green IT, E2E y despliegue no tenía puntos en el backlog y NO se acredita (criterio
   conservador).
4. Costo Real (AC): dedicación planificada constante: AC = BAC x semanas transcurridas desde el 01/09/2026 / 14 semanas
   presupuestadas.
5. El proyecto tiene cuatro sprints; el cuarto se extiende hasta la fecha de corte, el 28/11/2026.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

BAC = 84258.75
RESERVA = 10111.05
PUNTOS_TOTALES = 116
INICIO = date(2026, 9, 1)
SEMANAS_PRESUPUESTADAS = 14

# ── DATOS ────────────────────────────────────────────────────────────────
# (nombre, fin del sprint, puntos planificados acumulados al fin de la iteración correspondiente)
SPRINTS = [
    ("Sprint 1", date(2026, 9, 22), 24),
    ("Sprint 2", date(2026, 10, 6), 68),
    ("Sprint 3", date(2026, 10, 20), 94),
    ("Sprint 4 (cierre)", date(2026, 11, 28), 116),
]

# (id, puntos, crédito, índice del sprint en que se acredita); un ítem puede acreditarse en dos momentos (50 % y luego el resto).
GANADO = [
    # Sprint 1
    ("US-001", 3, 1.0, 0), ("US-003", 5, 1.0, 0), ("EN-002", 5, 0.5, 0),
    # Sprint 2 y 3: avances parciales de accesibilidad y de reducción de recómputo
    ("EN-007", 3, 0.5, 1),
    ("EN-009", 3, 0.5, 2),
    # Sprint 4 (hasta el 28/11): implementación completa y verificada con pruebas
    ("EN-002", 5, 0.5, 3), ("EN-007", 3, 0.5, 3), ("EN-009", 3, 0.5, 3),
    ("US-005", 13, 1.0, 3), ("US-007", 5, 1.0, 3), ("US-008", 8, 1.0, 3), ("US-009", 3, 1.0, 3),
    ("US-010", 5, 1.0, 3), ("EN-005", 5, 1.0, 3), ("EN-001", 8, 1.0, 3), ("US-002", 8, 1.0, 3),
    ("US-004", 5, 1.0, 3), ("US-006", 8, 1.0, 3), ("EN-004", 3, 1.0, 3), ("EN-008", 5, 1.0, 3),
    ("EN-010", 8, 1.0, 3),
    # Implementados pero que requieren infraestructura de pago para cumplir su medida en producción
    ("EN-003", 5, 0.5, 3), ("EN-006", 8, 0.5, 3),
]

PARCIALES = {"EN-003": 5, "EN-006": 8}  # 50 %: el failover y el escalado se demuestran con dos instancias, no en la nube
NO_INICIADOS: list[str] = []
PUNTOS_NO_INICIADOS: dict[str, int] = {}
ITEMS_TOTALES = 20
HECHOS_FINAL = [
    "US-001", "US-002", "US-003", "US-004", "US-005", "US-006", "US-007", "US-008", "US-009", "US-010",
    "EN-001", "EN-002", "EN-004", "EN-005", "EN-007", "EN-008", "EN-009", "EN-010",
]

# Flujo acumulado de ítems (de 20) al cierre de cada sprint: (Hecho, En curso, Por hacer)
FLUJO = [(2, 1, 17), (2, 2, 16), (2, 3, 15), (18, 2, 0)]


def semanas(fin: date) -> float:
    return (fin - INICIO).days / 7.0


def calcular() -> list[dict]:
    valor_punto = BAC / PUNTOS_TOTALES
    filas = []
    ganados_acum = 0.0
    for i, (nombre, fin, pv_pts) in enumerate(SPRINTS):
        ganados_acum += sum(p * c for _, p, c, s in GANADO if s == i)
        pv = pv_pts * valor_punto
        ev = ganados_acum * valor_punto
        ac = BAC * semanas(fin) / SEMANAS_PRESUPUESTADAS
        filas.append({
            "sprint": nombre, "fin": fin, "pv_pts": pv_pts, "ev_pts": ganados_acum,
            "pv": pv, "ev": ev, "ac": ac,
            "sv": ev - pv, "cv": ev - ac,
            "spi": ev / pv if pv else None, "cpi": ev / ac if ac else None,
        })
    return filas


def eac(f: dict) -> dict:
    cpi, spi = f["cpi"], f["spi"]
    return {
        "f1": BAC / cpi,
        "f2": BAC / (cpi * spi),
        "f3": f["ac"] + (BAC - f["ev"]) / (cpi * spi),
    }


def d(v: float, dec: int = 2) -> str:
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")  # 1 234,56


def tablas() -> None:
    filas = calcular()
    print(f"BAC = S/ {d(BAC)} · valor por punto = S/ {d(BAC / PUNTOS_TOTALES)} · {PUNTOS_TOTALES} puntos\n")
    print("| Sprint (fin) | PV acum. (pts) | EV acum. (pts) | PV (S/) | EV (S/) | AC (S/) | SV | CV | SPI | CPI |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for f in filas:
        print(f"| {f['sprint']} ({f['fin']:%d/%m}) | {f['pv_pts']} | {f['ev_pts']:g} | {d(f['pv'])} | {d(f['ev'])} | {d(f['ac'])} | "
              f"{d(f['sv'])} | {d(f['cv'])} | {d(f['spi'], 3)} | {d(f['cpi'], 3)} |")
    print("\nPeriodo actual (Sprint 4, hasta el cierre) = acumulado actual - acumulado del Sprint 3:")
    a, b = filas[-1], filas[-2]
    pv_p, ev_p, ac_p = a["pv"] - b["pv"], a["ev"] - b["ev"], a["ac"] - b["ac"]
    print(f"PV={d(pv_p)} EV={d(ev_p)} AC={d(ac_p)} SV={d(ev_p - pv_p)} CV={d(ev_p - ac_p)} "
          f"SPI={'n/a' if not pv_p else d(ev_p / pv_p, 3)} CPI={d(ev_p / ac_p, 3)}")
    for f in filas:
        print(f"{f['sprint']}: % planificado={d(f['pv'] / BAC * 100, 1)} % ganado={d(f['ev'] / BAC * 100, 1)} % gastado={d(f['ac'] / BAC * 100, 1)}")
    e = eac(a)
    print(f"\nEAC1 = {d(e['f1'])} | EAC2 = {d(e['f2'])} | EAC3 = {d(e['f3'])}")
    print(f"ETC (con EAC1) = {d(e['f1'] - a['ac'])} | VAC (BAC-EAC1) = {d(BAC - e['f1'])}")
    pendiente = sum(PARCIALES.values()) / 2
    print(f"Puntos ganados: {a['ev_pts']:g} de {PUNTOS_TOTALES}; pendientes por el 50 % de {', '.join(PARCIALES)}: {pendiente:g} pts")


# ── Gráficos SVG sin dependencias ───────────────────────────────────────

COLOR = {"pv": "#6b7280", "ev": "#059669", "ac": "#dc2626", "ideal": "#9ca3af", "real": "#2563eb"}


def _marco(ancho, alto, titulo, cuerpo):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" '
        f'font-family="Arial, sans-serif" role="img" aria-label="{titulo}">'
        f'<rect width="{ancho}" height="{alto}" fill="#ffffff"/>'
        f'<text x="{ancho / 2}" y="24" text-anchor="middle" font-size="15" font-weight="bold" fill="#111827">{titulo}</text>'
        f"{cuerpo}</svg>"
    )


def _ejes(x0, y0, x1, y1, ymax, etiquetas_x, paso_y, unidad=""):
    s = f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#374151"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#374151"/>'
    n = int(ymax / paso_y)
    for k in range(n + 1):
        v = k * paso_y
        y = y1 - (y1 - y0) * v / ymax
        s += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#e5e7eb"/>'
        s += f'<text x="{x0 - 6}" y="{y + 4}" text-anchor="end" font-size="10" fill="#374151">{v:g}{unidad}</text>'
    for i, et in enumerate(etiquetas_x):
        x = x0 + (x1 - x0) * i / (len(etiquetas_x) - 1)
        s += f'<text x="{x}" y="{y1 + 16}" text-anchor="middle" font-size="10" fill="#374151">{et}</text>'
    return s


def _linea(puntos, color, ancho=2.5, punteada=False):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in puntos)
    extra = ' stroke-dasharray="6 4"' if punteada else ""
    marcas = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>' for x, y in puntos)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{ancho}"{extra}/>{marcas}'


def _leyenda(items, x, y):
    s = ""
    for i, (nombre, color) in enumerate(items):
        s += f'<rect x="{x + i * 130}" y="{y}" width="12" height="12" fill="{color}"/><text x="{x + i * 130 + 18}" y="{y + 11}" font-size="11" fill="#111827">{nombre}</text>'
    return s


def grafico_evm(filas):
    ancho, alto, x0, x1, y0, y1 = 640, 340, 70, 610, 50, 280
    ymax = 25000
    etiquetas = ["Inicio"] + [f["sprint"].replace(" (cierre)", "") for f in filas]
    cuerpo = _ejes(x0, y0, x1, y1, ymax, etiquetas, 5000)

    def pos(i, v):
        return x0 + (x1 - x0) * i / (len(etiquetas) - 1), y1 - (y1 - y0) * v / ymax

    series = {"pv": [0] + [f["pv"] for f in filas], "ev": [0] + [f["ev"] for f in filas], "ac": [0] + [f["ac"] for f in filas]}
    for clave, valores in series.items():
        cuerpo += _linea([pos(i, v) for i, v in enumerate(valores)], COLOR[clave])
    cuerpo += _leyenda([("PV planificado", COLOR["pv"]), ("EV ganado", COLOR["ev"]), ("AC real (estimado)", COLOR["ac"])], 90, 305)
    cuerpo += f'<text x="{x0 - 55}" y="{(y0 + y1) / 2}" font-size="10" fill="#374151" transform="rotate(-90 {x0 - 55} {(y0 + y1) / 2})">S/ acumulados</text>'
    return _marco(ancho, alto, "Tendencia de valor ganado (EVM acumulado)", cuerpo)


def grafico_indices(filas):
    ancho, alto, x0, x1, y0, y1 = 640, 340, 70, 610, 50, 280
    ymax = 1.5
    etiquetas = [f["sprint"].replace(" (cierre)", "") for f in filas]
    cuerpo = _ejes(x0, y0, x1, y1, ymax, etiquetas, 0.25)
    ref = y1 - (y1 - y0) * 1.0 / ymax
    cuerpo += f'<line x1="{x0}" y1="{ref}" x2="{x1}" y2="{ref}" stroke="#059669" stroke-dasharray="5 4"/><text x="{x1 - 4}" y="{ref - 5}" text-anchor="end" font-size="10" fill="#059669">1,0 = según lo planificado</text>'

    def pos(i, v):
        return x0 + (x1 - x0) * i / (len(etiquetas) - 1), y1 - (y1 - y0) * v / ymax

    cuerpo += _linea([pos(i, f["spi"]) for i, f in enumerate(filas)], "#2563eb")
    cuerpo += _linea([pos(i, f["cpi"]) for i, f in enumerate(filas)], "#d97706")
    cuerpo += _leyenda([("SPI (cronograma)", "#2563eb"), ("CPI (costo)", "#d97706")], 200, 305)
    return _marco(ancho, alto, "Índices de desempeño SPI y CPI por sprint", cuerpo)


def grafico_flujo():
    ancho, alto, x0, x1, y0, y1 = 640, 340, 70, 610, 50, 280
    etiquetas = [s[0].replace(" (cierre)", "") for s in SPRINTS]
    n = len(etiquetas)
    cuerpo = _ejes(x0, y0, x1, y1, 20, etiquetas, 5)

    def pos(i, v):
        return x0 + (x1 - x0) * i / (n - 1), y1 - (y1 - y0) * v / 20

    capas = [("Por hacer", "#d1d5db", lambda t: t[0] + t[1] + t[2]), ("En curso", "#fbbf24", lambda t: t[0] + t[1]), ("Hecho", "#34d399", lambda t: t[0])]
    for _, color, acumulado in capas:
        arriba = [pos(i, acumulado(t)) for i, t in enumerate(FLUJO)]
        puntos = arriba + [(x1, y1), (x0, y1)]
        cuerpo += f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in puntos)}" fill="{color}" opacity="0.9"/>'
    cuerpo += _leyenda([("Por hacer", "#d1d5db"), ("En curso", "#fbbf24"), ("Hecho", "#34d399")], 190, 305)
    return _marco(ancho, alto, "Flujo acumulado de ítems del backlog (20 ítems)", cuerpo)


def grafico_burndown(filas):
    ancho, alto, x0, x1, y0, y1 = 640, 340, 70, 610, 50, 280
    etiquetas = ["Inicio"] + [f["sprint"].replace(" (cierre)", "") for f in filas]
    cuerpo = _ejes(x0, y0, x1, y1, 120, etiquetas, 20)

    def pos(i, v):
        return x0 + (x1 - x0) * i / (len(etiquetas) - 1), y1 - (y1 - y0) * v / 120

    total = len(etiquetas) - 1
    ideal = [PUNTOS_TOTALES * (1 - i / total) for i in range(total + 1)]
    real = [PUNTOS_TOTALES] + [PUNTOS_TOTALES - f["ev_pts"] for f in filas]
    cuerpo += _linea([pos(i, v) for i, v in enumerate(ideal)], COLOR["ideal"], punteada=True)
    cuerpo += _linea([pos(i, v) for i, v in enumerate(real)], COLOR["real"])
    cuerpo += _leyenda([("Ritmo ideal", COLOR["ideal"]), ("Trabajo restante real", COLOR["real"])], 190, 305)
    return _marco(ancho, alto, "Burndown: puntos restantes del backlog", cuerpo)


def grafico_burnup(filas):
    ancho, alto, x0, x1, y0, y1 = 640, 340, 70, 610, 50, 280
    etiquetas = ["Inicio"] + [f["sprint"].replace(" (cierre)", "") for f in filas]
    cuerpo = _ejes(x0, y0, x1, y1, 120, etiquetas, 20)

    def pos(i, v):
        return x0 + (x1 - x0) * i / (len(etiquetas) - 1), y1 - (y1 - y0) * v / 120

    alcance = [PUNTOS_TOTALES] * len(etiquetas)
    hecho = [0] + [f["ev_pts"] for f in filas]
    cuerpo += _linea([pos(i, v) for i, v in enumerate(alcance)], COLOR["ideal"], punteada=True)
    cuerpo += _linea([pos(i, v) for i, v in enumerate(hecho)], COLOR["ev"])
    cuerpo += _leyenda([("Alcance total (116 pts)", COLOR["ideal"]), ("Trabajo completado", COLOR["ev"])], 170, 305)
    cuerpo += f'<text x="{x1}" y="{y0 + 12}" text-anchor="end" font-size="10" fill="#374151">Sin cambios de alcance formalizados</text>'
    return _marco(ancho, alto, "Burnup: trabajo completado y alcance", cuerpo)


def grafico_burbujas(filas):
    ancho, alto, x0, x1, y0, y1 = 640, 340, 70, 610, 50, 280
    cuerpo = ""
    # ejes SPI (x) y CPI (y) de 0 a 1,5
    for k in range(7):
        v = k * 0.25
        x = x0 + (x1 - x0) * v / 1.5
        y = y1 - (y1 - y0) * v / 1.5
        cuerpo += f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="#e5e7eb"/><text x="{x}" y="{y1 + 15}" text-anchor="middle" font-size="10">{v:g}</text>'
        cuerpo += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#e5e7eb"/><text x="{x0 - 6}" y="{y + 4}" text-anchor="end" font-size="10">{v:g}</text>'
    xr, yr = x0 + (x1 - x0) / 1.5, y1 - (y1 - y0) / 1.5
    cuerpo += f'<line x1="{xr}" y1="{y0}" x2="{xr}" y2="{y1}" stroke="#059669" stroke-dasharray="5 4"/><line x1="{x0}" y1="{yr}" x2="{x1}" y2="{yr}" stroke="#059669" stroke-dasharray="5 4"/>'
    cuerpo += f'<text x="{x1 / 2 + 30}" y="{y1 + 32}" text-anchor="middle" font-size="11">SPI (cronograma)</text>'
    cuerpo += f'<text x="{x0 - 52}" y="{(y0 + y1) / 2}" font-size="11" transform="rotate(-90 {x0 - 52} {(y0 + y1) / 2})">CPI (costo)</text>'
    for f in filas:
        spi, cpi = f["spi"], f["cpi"]
        csi = spi * cpi  # Índice de Cronograma-Costo (CSI = SPI x CPI), define el tamaño de la burbuja
        x = x0 + (x1 - x0) * min(spi, 1.5) / 1.5
        y = y1 - (y1 - y0) * min(cpi, 1.5) / 1.5
        radio = 8 + 40 * min(csi, 1.0)
        cuerpo += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radio:.1f}" fill="#2563eb" fill-opacity="0.35" stroke="#1d4ed8"/>'
        cuerpo += f'<text x="{x:.1f}" y="{y - radio - 4:.1f}" text-anchor="middle" font-size="10" fill="#111827">{f["sprint"].replace(" (cierre)", "")}</text>'
    return _marco(ancho, alto, "SPI vs CPI (tamaño de burbuja = CSI = SPI x CPI)", cuerpo)


def grafico_medidores(filas):
    ancho, alto = 640, 300
    f = filas[-1]
    cuerpo = ""
    medidas = [
        ("Planificado", f["pv"] / BAC * 100, "#6b7280"),
        ("Ganado", f["ev"] / BAC * 100, "#059669"),
        ("Gastado", f["ac"] / BAC * 100, "#dc2626"),
    ]
    cuerpo += '<text x="320" y="48" text-anchor="middle" font-size="11" fill="#374151">Avance acumulado respecto al BAC al 28/11/2026</text>'
    for i, (nombre, valor, color) in enumerate(medidas):
        y = 80 + i * 62
        cuerpo += f'<text x="30" y="{y + 18}" font-size="13" fill="#111827">{nombre}</text>'
        cuerpo += f'<rect x="150" y="{y}" width="420" height="26" fill="#e5e7eb" rx="4"/>'
        cuerpo += f'<rect x="150" y="{y}" width="{420 * min(valor, 100) / 100:.1f}" height="26" fill="{color}" rx="4"/>'
        cuerpo += f'<text x="{150 + 420 * min(valor, 100) / 100 - 8:.1f}" y="{y + 18}" text-anchor="end" font-size="12" font-weight="bold" fill="#ffffff">{d(valor, 1)} %</text>'
    cuerpo += '<text x="30" y="275" font-size="11" fill="#374151">Un ganado muy por debajo del planificado indica retraso de alcance; un gastado por encima del ganado, baja eficiencia de costo.</text>'
    return _marco(ancho, alto, "Barras de estado del proyecto", cuerpo)


def _texto_lineas(x, y, lineas, tam=11, paso=15, color="#111827"):
    return "".join(
        f'<text x="{x}" y="{y + i * paso}" font-size="{tam}" fill="{color}">{linea}</text>' for i, linea in enumerate(lineas)
    )


def grafico_kanban():
    """Instantánea del tablero Scrum al 28/11/2026: 20 ítems del backlog repartidos por columna."""
    ancho, alto = 700, 400
    columnas = [
        ("Por hacer (0)", "#e5e7eb", []),
        (f"En curso ({len(PARCIALES)})", "#fde68a", sorted(PARCIALES)),
        (f"Hecho ({len(HECHOS_FINAL)})", "#a7f3d0", HECHOS_FINAL),
    ]
    cuerpo = ""
    for k, (titulo, color, ids) in enumerate(columnas):
        x = 20 + k * 225
        cuerpo += f'<rect x="{x}" y="46" width="210" height="290" fill="{color}" rx="6"/>'
        cuerpo += f'<text x="{x + 105}" y="68" text-anchor="middle" font-size="13" font-weight="bold" fill="#111827">{titulo}</text>'
        for j, ident in enumerate(ids):
            fila, col = divmod(j, 2)
            cx, cy = x + 10 + col * 100, 82 + fila * 30
            cuerpo += f'<rect x="{cx}" y="{cy}" width="92" height="24" fill="#ffffff" stroke="#6b7280" rx="4"/>'
            cuerpo += f'<text x="{cx + 46}" y="{cy + 16}" text-anchor="middle" font-size="12" fill="#111827">{ident}</text>'
    cuerpo += '<text x="350" y="360" text-anchor="middle" font-size="10" fill="#374151">EN-003 (failover) y EN-006 (escalado) están implementados y medidos con dos instancias;</text>'
    cuerpo += '<text x="350" y="375" text-anchor="middle" font-size="10" fill="#374151">cumplir su medida en la nube exige un plan de pago de la plataforma (varias instancias y escalado automático).</text>'
    return _marco(ancho, alto, "Tablero Scrum al 28/11/2026 (20 ítems del backlog)", cuerpo)


def grafico_retrospectiva():
    ancho, alto = 760, 380
    columnas = [
        ("Qué funcionó", "#a7f3d0", [
            "Flujos de Actions en verde",
            "E2E en 3 navegadores y móvil",
            "Trazabilidad requisito-prueba",
            "Auditoría contra los requisitos",
            "Documentos con enlaces verificados",
        ]),
        ("Qué mejorar", "#fde68a", [
            "El motor y la app de campo llegaron tarde",
            "Docker con poca memoria local",
            "Demostración al Product Owner",
            "SUS con usuarios reales",
            "Registro de horas por sprint",
        ]),
        ("Acciones", "#bfdbfe", [
            "Spike EN-001 ejecutado y publicado",
            "Suite completa en Actions",
            "Pruebas ofensivas en cada commit",
            "Agendar demo con fecha desde el inicio",
            "Bitácora de horas desde el Sprint 1",
        ]),
    ]
    cuerpo = ""
    for k, (titulo, color, notas) in enumerate(columnas):
        x = 20 + k * 245
        cuerpo += f'<rect x="{x}" y="46" width="230" height="310" fill="{color}" rx="6"/>'
        cuerpo += f'<text x="{x + 115}" y="70" text-anchor="middle" font-size="14" font-weight="bold" fill="#111827">{titulo}</text>'
        for j, nota in enumerate(notas):
            y = 86 + j * 54
            cuerpo += f'<rect x="{x + 12}" y="{y}" width="206" height="44" fill="#fffbe6" stroke="#9ca3af" rx="3"/>'
            cuerpo += _texto_lineas(x + 20, y + 26, [nota], tam=11)
    return _marco(ancho, alto, "Tablero de retrospectiva del cierre (Sprint 4)", cuerpo)


def escribir_graficos(carpeta: Path) -> None:
    filas = calcular()
    carpeta.mkdir(parents=True, exist_ok=True)
    archivos = {
        "evm-tendencias.svg": grafico_evm(filas),
        "indices-spi-cpi.svg": grafico_indices(filas),
        "flujo-acumulado.svg": grafico_flujo(),
        "burndown.svg": grafico_burndown(filas),
        "burnup.svg": grafico_burnup(filas),
        "burbujas-spi-cpi.svg": grafico_burbujas(filas),
        "medidores-barras.svg": grafico_medidores(filas),
        "tablero-kanban.svg": grafico_kanban(),
        "tablero-retrospectiva.svg": grafico_retrospectiva(),
    }
    for nombre, contenido in archivos.items():
        (carpeta / nombre).write_text(contenido, encoding="utf-8", newline="\n")
        print(f"escrito {carpeta / nombre}")


if __name__ == "__main__":
    tablas()
    if "--graficos" in sys.argv:
        escribir_graficos(Path("docs/04 Cierre/imagenes"))
