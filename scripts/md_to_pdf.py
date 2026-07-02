#!/usr/bin/env python3
"""Convierte un Markdown a PDF (pura Python: markdown -> HTML -> xhtml2pdf).

Sin dependencias de sistema (no requiere wkhtmltopdf ni GTK), por lo que
funciona en Windows sin instalación adicional más allá de los paquetes pip
`markdown` y `xhtml2pdf`.

Uso:
    py scripts/md_to_pdf.py "ruta/archivo.md" [salida.pdf]
"""
import sys
from pathlib import Path

import markdown
from xhtml2pdf import pisa

CSS = """
@page { size: A4; margin: 2cm 1.8cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #1a1a1a; line-height: 1.4; }
h1 { font-size: 20pt; color: #6b2d2d; border-bottom: 2px solid #6b2d2d; padding-bottom: 4px; }
h2 { font-size: 14pt; color: #6b2d2d; margin-top: 16px; border-bottom: 1px solid #cda; padding-bottom: 2px; }
h3 { font-size: 11.5pt; color: #333; margin-top: 12px; }
h4 { font-size: 10.5pt; color: #6b2d2d; margin-top: 10px; margin-bottom: 2px; }
sub { color: #777; font-size: 8pt; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th, td { border: 1px solid #bbb; padding: 4px 6px; text-align: left; vertical-align: top; font-size: 8.5pt; }
th { background: #f0e8e8; }
li { margin-bottom: 2px; }
strong { color: #4a2020; }
code { background: #f2f2f2; padding: 0 2px; }
blockquote { background: #f6f1e9; border: 1px solid #cda; border-left: 4px solid #6b2d2d;
             padding: 6px 10px; margin: 6px 0; }
blockquote p { margin: 2px 0; }
"""


def convert(md_path: Path, pdf_path: Path) -> bool:
    text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists"]
    )
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    with pdf_path.open("wb") as fh:
        result = pisa.CreatePDF(src=html, dest=fh, encoding="utf-8")
    return not result.err


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: py scripts/md_to_pdf.py <archivo.md> [salida.pdf]")
    md_path = Path(sys.argv[1])
    pdf_path = Path(sys.argv[2]) if len(sys.argv) > 2 else md_path.with_suffix(".pdf")
    ok = convert(md_path, pdf_path)
    size = pdf_path.stat().st_size if pdf_path.is_file() else 0
    print(f"PDF: {pdf_path}  ({size:,} bytes)  {'OK' if ok else 'CON ERRORES'}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
