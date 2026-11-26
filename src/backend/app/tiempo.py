"""
Manejo de fechas y horas.

Todo instante se guarda y se devuelve en UTC con su zona horaria explícita (`...Z`). Un valor sin zona horaria llega de dos
orígenes y se interpreta distinto:

- Un dato **de entrada** del usuario (por ejemplo el campo «datetime-local» de un formulario, que no lleva zona) se entiende
  como hora de Lima (UTC-5, Perú no usa horario de verano) y se convierte a UTC (`lima_a_utc`).
- Un dato **leído de la base de datos** sin zona (SQLite no la conserva) ya está en UTC (`como_utc`).

PostgreSQL (`timestamptz`) exige valores con zona horaria, por eso esta normalización es necesaria para producción.
"""

from datetime import datetime, timedelta, timezone

LIMA = timezone(timedelta(hours=-5))


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def como_utc(valor: datetime | None) -> datetime | None:
    """Dato leído de la base: sin zona significa UTC."""
    if valor is not None and valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor


utc = como_utc  # nombre corto usado por los servicios


def lima_a_utc(valor: datetime | None) -> datetime | None:
    """Dato de entrada: sin zona significa hora de Lima; con zona se convierte a UTC."""
    if valor is None:
        return None
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=LIMA)
    return valor.astimezone(timezone.utc)
