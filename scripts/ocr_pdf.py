#!/usr/bin/env python3
"""OCR a scanned (image-only) PDF to a sibling .txt using PyMuPDF + Tesseract.

For PDFs where pypdf extracts no text (pure image scans). Renders each page to a
high-res bitmap with PyMuPDF (no Poppler/Ghostscript needed) and runs Tesseract via
pytesseract. Output format matches scripts/extract_pdf.py (page markers) so the
chunker/synthesis pipeline can reuse it.

Usage:
    py scripts/ocr_pdf.py "books/<file>.pdf" [output.txt] [--lang spa] [--dpi 300]

Requires the Tesseract binary installed (UB-Mannheim build) and the language
traineddata (e.g. spa) present in its tessdata folder.
"""
import sys
import os
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF no está instalado. Ejecuta: py -m pip install pymupdf")
try:
    import pytesseract
    from PIL import Image
except ImportError:
    sys.exit("Falta dependencia. Ejecuta: py -m pip install pytesseract pillow")
import io


def find_tesseract() -> str | None:
    """Locate tesseract.exe; prefer PATH, fall back to default install dir."""
    from shutil import which
    exe = which("tesseract")
    if exe:
        return exe
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for c in candidates:
        if Path(c).is_file():
            return c
    return None


def parse_args(argv):
    path = None
    out = None
    lang = "spa"
    dpi = 300
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--lang":
            lang = argv[i + 1]; i += 2
        elif a == "--dpi":
            dpi = int(argv[i + 1]); i += 2
        elif path is None:
            path = a; i += 1
        elif out is None:
            out = argv[i]; i += 1
        else:
            i += 1
    if path is None:
        sys.exit("Uso: py scripts/ocr_pdf.py <ruta.pdf> [salida.txt] [--lang spa] [--dpi 300]")
    return Path(path), (Path(out) if out else None), lang, dpi


def main():
    pdf_path, out_path, lang, dpi = parse_args(sys.argv)
    if not pdf_path.is_file():
        sys.exit(f"No existe el PDF: {pdf_path}")
    if out_path is None:
        out_path = pdf_path.with_suffix(".txt")

    exe = find_tesseract()
    if not exe:
        sys.exit("No se encontró tesseract.exe. Instala UB-Mannheim.TesseractOCR.")
    pytesseract.pytesseract.tesseract_cmd = exe

    # If the system tessdata lacks the language but a local ./tessdata has it,
    # point Tesseract there via TESSDATA_PREFIX so runs work without admin/setup.
    local_td = Path.cwd() / "tessdata"
    if (local_td / f"{lang}.traineddata").is_file():
        os.environ["TESSDATA_PREFIX"] = str(local_td)

    # Verify the requested language is available; fall back to eng with a warning.
    try:
        langs = pytesseract.get_languages(config="")
    except Exception:
        langs = []
    if lang not in langs:
        print(f"AVISO: idioma '{lang}' no disponible en Tesseract (langs: {langs}). "
              f"Usando 'eng'. Coloca {lang}.traineddata en la carpeta tessdata para "
              f"mejor calidad.")
        lang = "eng" if "eng" in langs else (langs[0] if langs else lang)

    doc = fitz.open(str(pdf_path))
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    parts = []
    nonempty = 0
    n = doc.page_count
    for i in range(n):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang=lang) or ""
        if text.strip():
            nonempty += 1
        parts.append(f"\f=== PÁGINA {i + 1} ===\n{text}")
        if (i + 1) % 10 == 0 or i + 1 == n:
            print(f"  OCR {i + 1}/{n} páginas...")

    full = "\n".join(parts)
    out_path.write_text(full, encoding="utf-8")

    print(f"PDF:        {pdf_path}")
    print(f"TXT:        {out_path}")
    print(f"Idioma OCR: {lang}  | DPI: {dpi}")
    print(f"Páginas:    {n} (con texto: {nonempty})")
    print(f"Tamaño TXT: {len(full.encode('utf-8')):,} bytes")
    if nonempty == 0:
        print("AVISO: OCR no produjo texto; revisa idioma/calidad del escaneo.")


if __name__ == "__main__":
    main()
