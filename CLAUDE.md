# Proyecto: Especialización Penal — pipeline de lectura de PDFs

## Regla de lectura de PDFs (importante, ahorro de tokens)

**Nunca leas archivos `.pdf` directamente para trabajo de texto completo.**

Para cada PDF debe existir, al lado, un `.txt` pre-extraído (texto plano) y,
cuando se necesite reutilizar el contenido entre sesiones, un `*_synthesis.json`
(síntesis estructurada por capítulos/secciones).

Cómo trabajar:
- Para **análisis o lectura de contenido** → lee el `.txt`.
- Para **reutilizar** lo ya procesado (resúmenes, conceptos) → lee el
  `*_synthesis.json` si existe. Es casi gratis en tokens y debe ser la primera fuente.
- Solo usa el **MCP `pdf-reader`** para lecturas puntuales de páginas concretas o
  búsquedas dentro del PDF (cuando necesites una cita textual o una página exacta).

Si falta un `.txt` para un PDF, genéralo (no cuesta tokens de API):

```
py scripts/extract_pdf.py "<archivo>.pdf"
```

Si el PDF es un **escaneo de imágenes** (pypdf devuelve 0 páginas con texto),
usa OCR (requiere Tesseract + datos de idioma en `./tessdata`):

```
py scripts/ocr_pdf.py "<archivo>.pdf" --lang spa --dpi 300
```

Para sintetizar un `.txt` largo: trocearlo con `py scripts/chunk_txt.py "<archivo>.txt"`
y luego ejecutar un pase map-reduce (subagentes baratos por chunk → pase final que
escribe `<archivo>_synthesis.json`). Para convertir una síntesis a Markdown legible,
usar `scripts/synthesis_to_md.py`.

## Pipeline / herramientas

- MCP de PDF: `@sylphx/pdf-reader-mcp` (configurado en `.mcp.json`, se lanza con
  `npx`). Requiere Node.js.
- Extracción local: `scripts/extract_pdf.py` (usa `pypdf`, requiere Python).
- OCR de escaneos: `scripts/ocr_pdf.py` (usa PyMuPDF + pytesseract; Tesseract
  requerido en el sistema, datos de idioma `spa` en `./tessdata`).
- Troceado para síntesis: `scripts/chunk_txt.py`.
- Síntesis legible: `scripts/synthesis_to_md.py` (un `_synthesis.json` → `.md`).
- Markdown → PDF: `scripts/md_to_pdf.py` (pura Python: `markdown` + `xhtml2pdf`,
  sin dependencias de sistema). Requiere `py -m pip install markdown xhtml2pdf`.

Dependencias de Python en `requirements.txt` (`py -m pip install -r requirements.txt`).
