"""Utilidades de consulta compartidas por los routers de listado."""


def patron_like(texto: str) -> str:
    """Convierte la búsqueda del usuario en un patrón LIKE seguro (escapa % y _)."""
    limpio = texto.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{limpio}%"


LIKE_ESCAPE = "\\"
