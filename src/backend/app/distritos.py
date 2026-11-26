"""
Distritos de Lima Metropolitana (RF-005: filtro del dashboard por distrito).

Cada distrito se representa por su centro aproximado; un pedido sin distrito declarado se asigna al centro más cercano de
su ubicación. Las coordenadas son referenciales (no un límite oficial) y alcanzan para agrupar los pedidos del reporte.
"""

from app.optimizador import distancia_km

CENTROS: dict[str, tuple[float, float]] = {
    "Ate": (-12.0259, -76.9178),
    "Barranco": (-12.1490, -77.0210),
    "Breña": (-12.0568, -77.0510),
    "Callao": (-12.0566, -77.1181),
    "Carabayllo": (-11.8670, -77.0330),
    "Chorrillos": (-12.1700, -77.0170),
    "Comas": (-11.9390, -77.0560),
    "El Agustino": (-12.0450, -77.0010),
    "Independencia": (-11.9920, -77.0540),
    "Jesús María": (-12.0710, -77.0490),
    "La Molina": (-12.0870, -76.9100),
    "La Victoria": (-12.0650, -77.0160),
    "Lima": (-12.0464, -77.0428),
    "Lince": (-12.0840, -77.0360),
    "Los Olivos": (-11.9920, -77.0720),
    "Magdalena": (-12.0900, -77.0690),
    "Miraflores": (-12.1211, -77.0297),
    "Pueblo Libre": (-12.0740, -77.0630),
    "Rímac": (-12.0290, -77.0430),
    "San Borja": (-12.1000, -77.0000),
    "San Isidro": (-12.0970, -77.0360),
    "San Juan de Lurigancho": (-11.9780, -77.0080),
    "San Juan de Miraflores": (-12.1550, -76.9700),
    "San Luis": (-12.0770, -76.9980),
    "San Martín de Porres": (-12.0000, -77.0850),
    "San Miguel": (-12.0790, -77.0860),
    "Santa Anita": (-12.0440, -76.9710),
    "Santiago de Surco": (-12.1380, -76.9910),
    "Surquillo": (-12.1110, -77.0120),
    "Villa El Salvador": (-12.2130, -76.9330),
}

# El análisis del proyecto se centra en el este de Lima: se ofrecen primero en los filtros.
DISTRITOS_PRIORITARIOS = ("San Juan de Lurigancho", "El Agustino", "Santa Anita", "Ate")


def distrito_mas_cercano(latitud: float, longitud: float) -> str:
    return min(CENTROS, key=lambda d: distancia_km(latitud, longitud, *CENTROS[d]))


def lista_distritos() -> list[str]:
    resto = sorted(d for d in CENTROS if d not in DISTRITOS_PRIORITARIOS)
    return [*DISTRITOS_PRIORITARIOS, *resto]
