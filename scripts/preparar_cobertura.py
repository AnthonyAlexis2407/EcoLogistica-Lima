"""Normaliza los informes de cobertura para que SonarQube los asocie a los archivos.

SonarQube resuelve las rutas de los informes respecto de la raíz del repositorio
(`sonar.projectBaseDir`). Pero:

* Vitest escribe `src/frontend/coverage/lcov.info` con rutas relativas a `src/frontend`
  (por ejemplo `src\\App.tsx` en Windows).
* coverage.py escribe `src/backend/coverage.xml` con nombres relativos a `src/backend/app`
  (por ejemplo `auth.py`).

Si no se corrigen, SonarQube informa 0 % de cobertura aunque las pruebas pasen. Este script
reescribe ambas rutas a la forma `src/frontend/src/App.tsx` y `src/backend/app/auth.py`.

Uso (desde la raíz del repositorio, después de generar los dos informes):
    python scripts/preparar_cobertura.py
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LCOV = RAIZ / "src" / "frontend" / "coverage" / "lcov.info"
COBERTURA_XML = RAIZ / "src" / "backend" / "coverage.xml"


def normalizar_lcov(ruta: Path) -> int:
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    cambios = 0
    for i, linea in enumerate(lineas):
        if linea.startswith("SF:"):
            archivo = linea[3:].replace("\\", "/")
            if not archivo.startswith("src/frontend/"):
                lineas[i] = "SF:src/frontend/" + archivo.lstrip("./")
                cambios += 1
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return cambios


def normalizar_cobertura_xml(ruta: Path) -> int:
    texto = ruta.read_text(encoding="utf-8")
    texto = re.sub(r"<sources>.*?</sources>", "<sources><source>.</source></sources>", texto, flags=re.S)

    def reescribir(m: re.Match) -> str:
        archivo = m.group(1).replace("\\", "/")
        if archivo.startswith("src/backend/"):
            return m.group(0)
        return 'filename="src/backend/app/' + archivo + '"'

    texto, cambios = re.subn(r'filename="([^"]+)"', reescribir, texto)
    ruta.write_text(texto, encoding="utf-8")
    return cambios


def main() -> int:
    faltan = [str(r) for r in (LCOV, COBERTURA_XML) if not r.exists()]
    if faltan:
        print("Faltan informes de cobertura (genérelos primero):", *faltan, sep="\n  ")
        return 1
    print(f"lcov del frontend: {normalizar_lcov(LCOV)} rutas normalizadas")
    print(f"coverage.xml del backend: {normalizar_cobertura_xml(COBERTURA_XML)} rutas normalizadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
