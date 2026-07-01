# Otto — pendiente de extracción

El libro **Harro Otto — Derecho Penal** (PDF ~62 MB en Drive) no pudo extraerse con el
MCP de Google Drive: por su tamaño, `read_file_content` devuelve contenido vacío en
sucesivos intentos (los otros 5 libros, de 17–32 MB, sí se extrajeron).

Para completarlo, hacer una de estas opciones y luego correr el pipeline normal:

1. **Descargar el PDF a mano** y colocarlo en esta carpeta como `harro-otto-derecho-penal.pdf`;
   luego `python3 scripts/extract_pdf.py "doctrina/otto/harro-otto-derecho-penal.pdf"`
   (o `ocr_pdf.py --lang spa` si es un escaneo). Después, chunk + síntesis map-reduce.
2. **Subir a Drive una versión más liviana** (comprimida o por tomos) y reintentar
   `read_file_content`.

Mientras tanto, Otto queda fuera de la síntesis y de la comparativa (se lo marca como
`disponible: false`).
