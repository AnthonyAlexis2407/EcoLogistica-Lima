"""Genera la ilustración del banner del Dashboard y sus variantes optimizadas (Informe Green IT, optimización 3).

Dibuja una ruta de entrega con una hoja (el tema del proyecto) y la exporta en dos anchos (280 y 560 px,
para pantallas normales y de alta densidad) y tres formatos: AVIF, WebP y PNG de respaldo. Imprime una
tabla con el peso de cada variante para decidir con datos, no por costumbre.

Requiere Pillow 11 o superior (con soporte AVIF):
    pip install pillow
    python scripts/generar_ilustracion_hero.py

Para usar otra imagen de marca, reemplace `dibujar()` por la carga de su archivo (`Image.open(...)`):
el resto del proceso (anchos, formatos y tabla de pesos) no cambia.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

SALIDA = Path(__file__).resolve().parent.parent / "src" / "frontend" / "public" / "img"
ANCHOS = (280, 560)
BASE_W, BASE_H = 560, 320
SUPERMUESTREO = 4  # se dibuja 4 veces más grande y se reduce: bordes suaves sin filtros

ESMERALDA = (16, 185, 129, 255)
MENTA = (110, 231, 183, 255)
BLANCO = (255, 255, 255, 255)


def hoja(d: ImageDraw.ImageDraw, cx: float, cy: float, tam: float, angulo: float, color) -> None:
    """Hoja con dos arcos simétricos (curvas cuadráticas aproximadas con 40 puntos)."""
    def arco(signo: int):
        puntos = []
        for i in range(41):
            t = i / 40
            x = (1 - t) * (1 - t) * -tam + 2 * (1 - t) * t * 0 + t * t * tam
            y = 2 * (1 - t) * t * (signo * tam * 0.9)
            puntos.append((x, y))
        return puntos
    contorno = arco(-1) + arco(1)[::-1]
    c, s = math.cos(angulo), math.sin(angulo)
    d.polygon([(cx + x * c - y * s, cy + x * s + y * c) for x, y in contorno], fill=color)


def dibujar() -> Image.Image:
    k = SUPERMUESTREO
    img = Image.new("RGBA", (BASE_W * k, BASE_H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Resplandor suave detrás de la ruta
    d.ellipse([60 * k, 10 * k, 520 * k, 310 * k], fill=(16, 185, 129, 38))
    d.ellipse([140 * k, 50 * k, 460 * k, 280 * k], fill=(16, 185, 129, 30))

    # Ruta de entrega con trazo discontinuo
    nodos = [(70, 250), (170, 130), (290, 215), (400, 100), (490, 165)]
    for (x0, y0), (x1, y1) in zip(nodos, nodos[1:]):
        largo = math.hypot(x1 - x0, y1 - y0)
        pasos = int(largo / 14)
        for i in range(0, pasos, 2):
            a, b = i / pasos, min((i + 1) / pasos, 1)
            d.line([(x0 + (x1 - x0) * a) * k, (y0 + (y1 - y0) * a) * k,
                    (x0 + (x1 - x0) * b) * k, (y0 + (y1 - y0) * b) * k], fill=MENTA, width=5 * k)

    # Paradas: almacén (primero) y clientes
    for i, (x, y) in enumerate(nodos):
        radio = 17 if i == 0 else 11
        d.ellipse([(x - radio - 5) * k, (y - radio - 5) * k, (x + radio + 5) * k, (y + radio + 5) * k], fill=(16, 185, 129, 70))
        d.ellipse([(x - radio) * k, (y - radio) * k, (x + radio) * k, (y + radio) * k], fill=ESMERALDA)
        d.ellipse([(x - radio * 0.45) * k, (y - radio * 0.45) * k, (x + radio * 0.45) * k, (y + radio * 0.45) * k], fill=BLANCO)

    # Hoja: la marca de sostenibilidad sobre la última parada
    hoja(d, 490 * k, 98 * k, 34 * k, -math.pi / 4, ESMERALDA)
    hoja(d, 490 * k, 98 * k, 22 * k, -math.pi / 4, MENTA)
    d.line([(472 * k, 116 * k), (500 * k, 88 * k)], fill=BLANCO, width=3 * k)
    return img


def exportar(base: Image.Image) -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    print(f"{'archivo':26s} {'bytes':>7s}")
    for ancho in ANCHOS:
        alto = round(ancho * BASE_H / BASE_W)
        variante = base.resize((ancho, alto), Image.LANCZOS)
        destinos = {
            "avif": dict(quality=55),
            "webp": dict(quality=80, method=6),
            "png": dict(optimize=True),
        }
        for formato, opciones in destinos.items():
            ruta = SALIDA / f"hero-rutas-{ancho}.{formato}"
            variante.save(ruta, formato.upper(), **opciones)
            print(f"{ruta.name:26s} {ruta.stat().st_size:7d}")


if __name__ == "__main__":
    exportar(dibujar())
