"""Verifica los enlaces relativos y las anclas de los documentos Markdown del repositorio.

Comprueba tres cosas en cada documento:
  1. Que cada enlace a un archivo apunte a un archivo que existe.
  2. Que cada ancla (`archivo.md#seccion` o `#seccion`) coincida con un título real, calculado con la
     misma regla que usa GitHub para generar los identificadores de los títulos.
  3. Que cada documento dentro de `docs/` tenga su enlace de regreso al README principal.

Uso (desde la raíz del repositorio):
    python scripts/verificar_enlaces.py                 # README, CONTRIBUTING y docs/
    python scripts/verificar_enlaces.py ruta/doc.md ... # solo los archivos indicados

Termina con código 1 si encuentra algún problema (sirve para integrarlo en el CI).
"""

import re
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def identificador(titulo: str) -> str:
    """Identificador de un título según GitHub: minúsculas, sin signos y con guiones en lugar de espacios."""
    titulo = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", titulo)
    titulo = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", titulo)
    titulo = re.sub(r"[`*~]", "", titulo).strip().lower()
    titulo = "".join(c for c in titulo if c.isalnum() or c in "_- ")
    return titulo.replace(" ", "-")


def titulos(ruta: Path) -> set[str]:
    """Identificadores de todos los títulos del documento (los repetidos llevan sufijo -1, -2, ...)."""
    vistos: dict[str, int] = {}
    resultado: set[str] = set()
    en_codigo = False
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("```"):
            en_codigo = not en_codigo
        elif not en_codigo and re.match(r"#{1,6}\s", linea):
            base = identificador(linea.lstrip("#"))
            n = vistos.get(base, 0)
            resultado.add(base if n == 0 else f"{base}-{n}")
            vistos[base] = n + 1
    return resultado


def enlaces(ruta: Path):
    en_codigo = False
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if linea.startswith("```"):
            en_codigo = not en_codigo
            continue
        if en_codigo:
            continue
        linea = re.sub(r"`[^`]*`", "", linea)  # los enlaces dentro de código no cuentan
        for m in re.finditer(r"\]\(([^)\s]+)\)", linea):
            yield numero, m.group(1)


def verificar(ruta: Path) -> list[str]:
    problemas = []
    for numero, destino in enlaces(ruta):
        if destino.startswith(("http://", "https://", "mailto:")):
            continue
        archivo, _, ancla = destino.partition("#")
        objetivo = (ruta.parent / urllib.parse.unquote(archivo)).resolve() if archivo else ruta
        if not objetivo.exists():
            problemas.append(f"{ruta.relative_to(RAIZ)}:{numero}: no existe el archivo {urllib.parse.unquote(archivo)}")
        elif ancla and objetivo.suffix == ".md" and urllib.parse.unquote(ancla) not in titulos(objetivo):
            problemas.append(f"{ruta.relative_to(RAIZ)}:{numero}: no existe la sección #{urllib.parse.unquote(ancla)} en {objetivo.name}")
    if "docs" in ruta.relative_to(RAIZ).parts and "Volver al README" not in ruta.read_text(encoding="utf-8"):
        problemas.append(f"{ruta.relative_to(RAIZ)}: falta el enlace de regreso al README")
    return problemas


def main(argumentos: list[str]) -> int:
    if argumentos:
        archivos = [Path(a).resolve() for a in argumentos]
    else:
        archivos = [RAIZ / "README.md", RAIZ / "CONTRIBUTING.md", *sorted((RAIZ / "docs").rglob("*.md"))]
    problemas = [p for archivo in archivos for p in verificar(archivo)]
    for problema in problemas:
        print("PROBLEMA", problema)
    print(f"{len(archivos)} documentos revisados, {len(problemas)} problemas")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
