"""Calcula la energía y las emisiones de CO2e con el Sustainable Web Design Model v4 (SWDM v4).

Modelo (https://sustainablewebdesign.org/estimating-digital-emissions/):
    energía (kWh)  = datos (GB) x suma de intensidades de los tres segmentos (kWh/GB)
    emisiones (g)  = energía (kWh) x intensidad de la red eléctrica (g CO2e/kWh)

Segmentos (operación + fabricación del equipo): centros de datos, redes y dispositivos del usuario.
Intensidad eléctrica por defecto de SWDM v4: 494 g CO2e/kWh (promedio mundial, Ember).

Uso:  python scripts/calcular_swdm.py
"""

GB = 1_000_000_000  # 1 GB = 10^9 bytes

OPERACION = {"centros de datos": 0.055, "redes": 0.059, "dispositivos": 0.080}  # kWh/GB
FABRICACION = {"centros de datos": 0.012, "redes": 0.013, "dispositivos": 0.081}  # kWh/GB
RED_ELECTRICA = 494.0  # g CO2e/kWh

KWH_POR_GB = sum(OPERACION.values()) + sum(FABRICACION.values())  # 0.300 kWh/GB


def energia_kwh(bytes_transferidos: float) -> float:
    return bytes_transferidos / GB * KWH_POR_GB


def emisiones_g(bytes_transferidos: float) -> float:
    return energia_kwh(bytes_transferidos) * RED_ELECTRICA


ESCENARIOS = {
    "Carga inicial, ANTES (Lighthouse móvil)": 105_397,
    "Carga inicial, DESPUÉS (API con Brotli)": 68_966,
    "Listado de vehículos (50 filas), ANTES": 8_601,
    "Listado de vehículos, DESPUÉS (página de 12, Brotli)": 446,
    "Listado de pedidos (50 filas), ANTES": 18_001,
    "Listado de pedidos, DESPUÉS (página de 12, Brotli)": 555,
    "Ilustración del Dashboard, ANTES (PNG 560 px)": 39_905,
    "Ilustración del Dashboard, DESPUÉS (AVIF 560 px)": 7_958,
}

if __name__ == "__main__":
    print(f"Intensidad total: {KWH_POR_GB:.3f} kWh/GB  |  red eléctrica: {RED_ELECTRICA:.0f} g/kWh")
    print(f"Emisiones por GB: {KWH_POR_GB * RED_ELECTRICA:.2f} g CO2e/GB\n")
    for nombre, b in ESCENARIOS.items():
        print(f"{nombre:56s} {b:8d} B = {b / GB:.9f} GB | {energia_kwh(b):.3e} kWh | "
              f"{emisiones_g(b) * 1000:8.3f} mg CO2e")
    antes, despues = ESCENARIOS["Carga inicial, ANTES (Lighthouse móvil)"], ESCENARIOS["Carga inicial, DESPUÉS (API con Brotli)"]
    print(f"\nReducción de bytes carga inicial: {100 * (1 - despues / antes):.1f} %")
    for visitas in (50_000, 500_000):
        ahorro = (emisiones_g(antes) - emisiones_g(despues)) * visitas / 1000
        print(f"Ahorro con {visitas:>7,} cargas iniciales/año: {ahorro:8.3f} kg CO2e "
              f"(antes {emisiones_g(antes) * visitas / 1000:.3f} kg, después {emisiones_g(despues) * visitas / 1000:.3f} kg)")
    png, avif = ESCENARIOS["Ilustración del Dashboard, ANTES (PNG 560 px)"], ESCENARIOS["Ilustración del Dashboard, DESPUÉS (AVIF 560 px)"]
    print(f"Reducción de la ilustración PNG a AVIF: {100 * (1 - avif / png):.1f} %")
    for vistas in (50_000, 500_000):
        print(f"Ahorro de la ilustración con {vistas:>7,} vistas del Dashboard/año: "
              f"{(emisiones_g(png) - emisiones_g(avif)) * vistas / 1000:.3f} kg CO2e")
    print("\nSegmentos de la carga inicial DESPUÉS (mg CO2e):")
    for nombre in OPERACION:
        e = (OPERACION[nombre] + FABRICACION[nombre]) * despues / GB
        print(f"  {nombre:18s} {(OPERACION[nombre] + FABRICACION[nombre]):.3f} kWh/GB -> {e * RED_ELECTRICA * 1000:.3f} mg")
