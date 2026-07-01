#!/usr/bin/env python3
"""Extract text from a PDF to a sibling .txt file using pypdf.

Zero API tokens: this is pure local file I/O. Page boundaries are marked so
downstream tooling (chunker, synthesis) can map text back to pages.

Usage:
    py scripts/extract_pdf.py "books/<file>.pdf" [output.txt]

If no output path is given, writes "<file>.txt" next to the PDF.
Prints page count and output size to stdout.
"""
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("pypdf no está instalado. Ejecuta: py -m pip install pypdf")


def extract(pdf_path: Path, out_path: Path) -> tuple[int, int, int]:
    reader = PdfReader(str(pdf_path))
    pages = reader.pages
    parts = []
    nonempty = 0
    for i, page in enumerate(pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            nonempty += 1
        # Page marker on its own line; form-feed keeps it greppable.
        parts.append(f"\f=== PÁGINA {i} ===\n{text}")
    full = "\n".join(parts)
    out_path.write_text(full, encoding="utf-8")
    return len(pages), nonempty, len(full.encode("utf-8"))


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: py scripts/extract_pdf.py <ruta.pdf> [salida.txt]")
    pdf_path = Path(sys.argv[1])
    if not pdf_path.is_file():
        sys.exit(f"No existe el PDF: {pdf_path}")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf_path.with_suffix(".txt")

    n_pages, n_nonempty, n_bytes = extract(pdf_path, out_path)

    print(f"PDF:        {pdf_path}")
    print(f"TXT:        {out_path}")
    print(f"Páginas:    {n_pages} (con texto: {n_nonempty})")
    print(f"Tamaño TXT: {n_bytes:,} bytes")
    if n_nonempty == 0:
        print("AVISO: 0 páginas con texto. El PDF parece escaneado (solo imagen); "
              "necesitaría OCR.")
    elif n_nonempty < n_pages * 0.5:
        print("AVISO: muchas páginas sin texto; el PDF puede estar parcialmente "
              "escaneado.")


if __name__ == "__main__":
    main()
