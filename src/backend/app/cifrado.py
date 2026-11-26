"""
Cifrado de datos personales en reposo (RNF-008, RN-008, Ley N.° 29733).

Se usa AES-SIV (AES-256 en modo SIV, RFC 5297), un cifrado autenticado **determinista**: el mismo texto produce siempre el
mismo valor cifrado. Eso permite conservar las restricciones de unicidad y las búsquedas por igualdad (por ejemplo, el
inicio de sesión por correo) sin guardar el dato en claro.

Qué se cifra (clasificación de datos personales en el Documento 11, sección 6):
nombre, correo y teléfono de los usuarios; licencia y teléfono de los conductores; dirección y coordenadas de bodegas,
pedidos y entregas (geolocalización); y la evidencia de entrega (foto o firma).

La clave sale de `DATA_ENCRYPTION_KEY` (recomendado, un secreto propio) o, si falta, se deriva de `SECRET_KEY` con HKDF.
Los valores cifrados llevan el prefijo `enc1:`; un valor sin prefijo (datos anteriores al cifrado) se lee tal cual.
"""

import base64
from decimal import Decimal

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from app.config import settings

PREFIJO = "enc1:"
_cache: dict[str, AESSIV] = {}


def _cifrador() -> AESSIV:
    semilla = (settings.DATA_ENCRYPTION_KEY or settings.SECRET_KEY)
    if semilla not in _cache:
        clave = HKDF(
            algorithm=hashes.SHA512(), length=64, salt=b"ecologistica-lima-datos-personales", info=b"aes-siv",
        ).derive(semilla.encode("utf-8"))
        _cache[semilla] = AESSIV(clave)
    return _cache[semilla]


def cifrar(texto: str) -> str:
    """Devuelve `enc1:` más el texto cifrado en base64 (URL segura)."""
    cifrado = _cifrador().encrypt(texto.encode("utf-8"), None)
    return PREFIJO + base64.urlsafe_b64encode(cifrado).decode("ascii")


def descifrar(valor: str) -> str:
    """Descifra un valor con prefijo; un valor sin prefijo se devuelve igual (dato previo al cifrado)."""
    if not valor.startswith(PREFIJO):
        return valor
    crudo = base64.urlsafe_b64decode(valor[len(PREFIJO):].encode("ascii"))
    return _cifrador().decrypt(crudo, None).decode("utf-8")


def esta_cifrado(valor: str | None) -> bool:
    return bool(valor) and valor.startswith(PREFIJO)


class TextoCifrado(TypeDecorator):
    """Columna de texto cifrada de forma transparente (determinista: admite igualdad y unicidad)."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return None if value is None else cifrar(str(value))

    def process_result_value(self, value, dialect):
        return None if value is None else descifrar(value)


class NumeroCifrado(TypeDecorator):
    """Columna numérica (coordenadas) guardada cifrada; se lee como `Decimal`."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return None if value is None else cifrar(str(value))

    def process_result_value(self, value, dialect):
        return None if value is None else Decimal(descifrar(value))
