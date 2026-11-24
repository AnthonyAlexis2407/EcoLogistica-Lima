# ruff: noqa: E501  (las cadenas XML del formato Office Open XML son largas por naturaleza)
"""
Escritores de archivos para los reportes exportables (RF-006): Excel (.xlsx) y PDF, sin dependencias externas.

- `generar_xlsx` arma un libro de una hoja (formato Office Open XML) con encabezado en negrita y celdas tipadas.
- `generar_pdf` arma un documento A4 horizontal con una tabla de texto paginada (fuente Helvetica estándar).

Ambos son deliberadamente simples: sirven para entregar datos tabulares, no maquetación avanzada.
"""

import io
import zipfile
from html import escape  # escapa & < > y comillas: válido también para texto y atributos XML

_TIPOS_PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")


def _celda_texto(valor: str) -> str:
    # Inyección de fórmulas: Excel interpreta como fórmula el texto que empieza con estos caracteres.
    if valor.startswith(_TIPOS_PELIGROSOS):
        valor = "'" + valor
    return valor


def _columna(i: int) -> str:
    nombre = ""
    i += 1
    while i:
        i, resto = divmod(i - 1, 26)
        nombre = chr(65 + resto) + nombre
    return nombre


def generar_xlsx(encabezados: list[str], filas: list[list], hoja: str = "Reporte") -> bytes:
    """Libro de Excel con una hoja. Los números se guardan como números y el texto como texto en línea."""

    def fila_xml(numero: int, valores: list, estilo: int) -> str:
        celdas = []
        for i, v in enumerate(valores):
            ref = f"{_columna(i)}{numero}"
            if isinstance(v, bool):
                celdas.append(f'<c r="{ref}" s="{estilo}" t="inlineStr"><is><t>{"SI" if v else "NO"}</t></is></c>')
            elif isinstance(v, (int, float)):
                celdas.append(f'<c r="{ref}" s="{estilo}"><v>{v}</v></c>')
            elif v is None or v == "":
                celdas.append(f'<c r="{ref}" s="{estilo}"/>')
            else:
                texto = escape(_celda_texto(str(v)))
                celdas.append(f'<c r="{ref}" s="{estilo}" t="inlineStr"><is><t xml:space="preserve">{texto}</t></is></c>')
        return f'<row r="{numero}">{"".join(celdas)}</row>'

    datos = [fila_xml(1, encabezados, 1)] + [fila_xml(i, f, 0) for i, f in enumerate(filas, start=2)]
    ancho = "".join(f'<col min="{i}" max="{i}" width="22" customWidth="1"/>' for i in range(1, len(encabezados) + 1))
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<cols>{ancho}</cols><sheetData>{''.join(datos)}</sheetData></worksheet>"
    )
    estilos = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
        "</styleSheet>"
    )
    contenido = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>"
        ),
        "xl/workbook.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<sheets><sheet name="{escape(hoja)[:31]}" sheetId="1" r:id="rId1"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            "</Relationships>"
        ),
        "xl/styles.xml": estilos,
        "xl/worksheets/sheet1.xml": sheet,
    }
    salida = io.BytesIO()
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, xml in contenido.items():
            z.writestr(nombre, xml)
    return salida.getvalue()


# ── PDF ────────────────────────────────────────────────────────────────

ANCHO_PAGINA, ALTO_PAGINA = 842, 595  # A4 horizontal, en puntos
MARGEN = 36
TAM_FUENTE = 7.5
ANCHO_CARACTER = TAM_FUENTE * 0.52  # aproximación para Helvetica
INTERLINEA = 11
_REEMPLAZOS = {"₂": "2", "³": "3", "–": "-", "—": "-", "“": '"', "”": '"', "‘": "'", "’": "'"}


def _pdf_texto(valor) -> str:
    texto = "" if valor is None else str(valor)
    for origen, destino in _REEMPLAZOS.items():
        texto = texto.replace(origen, destino)
    texto = texto.encode("cp1252", errors="replace").decode("cp1252")
    return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def generar_pdf(titulo: str, encabezados: list[str], filas: list[list], subtitulo: str = "") -> bytes:
    """PDF A4 horizontal con tabla paginada; el texto que no cabe en su columna se recorta con «…»."""
    n = max(1, len(encabezados))
    util = ANCHO_PAGINA - 2 * MARGEN
    caracteres = max(4, int(util / n / ANCHO_CARACTER) - 1)
    por_pagina = int((ALTO_PAGINA - 2 * MARGEN - 40) / INTERLINEA)

    def linea(valores: list, y: float, negrita: bool = False) -> str:
        fuente = "F2" if negrita else "F1"
        trozos = []
        for i, v in enumerate(valores):
            texto = "" if v is None else str(v)
            if len(texto) > caracteres:
                texto = texto[: caracteres - 1] + "~"
            x = MARGEN + i * util / n
            trozos.append(f"BT /{fuente} {TAM_FUENTE} Tf {x:.1f} {y:.1f} Td ({_pdf_texto(texto)}) Tj ET")
        return "\n".join(trozos)

    paginas: list[str] = []
    bloques = [filas[i: i + por_pagina] for i in range(0, max(1, len(filas)), por_pagina)] or [[]]
    for numero, bloque in enumerate(bloques, start=1):
        y = ALTO_PAGINA - MARGEN
        partes = [f"BT /F2 12 Tf {MARGEN} {y} Td ({_pdf_texto(titulo)}) Tj ET"]
        y -= 14
        if subtitulo:
            partes.append(f"BT /F1 8 Tf {MARGEN} {y} Td ({_pdf_texto(subtitulo)}) Tj ET")
            y -= 12
        y -= 6
        partes.append(linea(encabezados, y, negrita=True))
        y -= INTERLINEA
        for fila in bloque:
            partes.append(linea(fila, y))
            y -= INTERLINEA
        partes.append(f"BT /F1 7 Tf {ANCHO_PAGINA - MARGEN - 60} {MARGEN - 18} Td (Pagina {numero} de {len(bloques)}) Tj ET")
        paginas.append("\n".join(partes))

    objetos: list[bytes] = []

    def agregar(cuerpo: str | bytes) -> int:
        objetos.append(cuerpo.encode("latin-1") if isinstance(cuerpo, str) else cuerpo)
        return len(objetos)

    agregar("<< /Type /Catalog /Pages 2 0 R >>")  # 1
    ids_paginas = [5 + 2 * i for i in range(len(paginas))]
    agregar(f"<< /Type /Pages /Kids [{' '.join(f'{i} 0 R' for i in ids_paginas)}] /Count {len(paginas)} >>")  # 2
    agregar("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")  # 3
    agregar("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")  # 4
    for i, contenido in enumerate(paginas):
        datos = contenido.encode("latin-1", errors="replace")
        agregar(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {ANCHO_PAGINA} {ALTO_PAGINA}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {6 + 2 * i} 0 R >>"
        )
        agregar(b"<< /Length " + str(len(datos)).encode() + b" >>\nstream\n" + datos + b"\nendstream")

    salida = io.BytesIO()
    salida.write(b"%PDF-1.4\n")
    posiciones = []
    for i, cuerpo in enumerate(objetos, start=1):
        posiciones.append(salida.tell())
        salida.write(f"{i} 0 obj\n".encode() + cuerpo + b"\nendobj\n")
    inicio_xref = salida.tell()
    salida.write(f"xref\n0 {len(objetos) + 1}\n".encode() + b"0000000000 65535 f \n")
    for pos in posiciones:
        salida.write(f"{pos:010d} 00000 n \n".encode())
    salida.write(f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF\n".encode())
    return salida.getvalue()
