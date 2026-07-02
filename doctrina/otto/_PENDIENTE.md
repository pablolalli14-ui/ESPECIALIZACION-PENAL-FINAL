# Otto — resuelto (extracción vía conversión a Google Docs)

El PDF original (~62 MB) no se pudo extraer ni descargar con las herramientas de Drive
por su tamaño (límite de 10 MB para descarga directa, y `read_file_content` devolvía
contenido vacío sobre el PDF binario).

**Solución aplicada:** en Google Drive, clic derecho sobre el PDF → *Abrir con* →
*Documentos de Google*. Esto dispara la conversión y OCR del lado de Google (el libro
es un escaneo), generando un Google Doc nativo sin límite de tamaño de descarga para
nuestras herramientas. Se leyó ese documento con `read_file_content` y se guardó como
`harro-otto-derecho-penal.txt`.

**Calidad del texto resultante:** el OCR tiene ruido considerable (columnas mezcladas,
palabras cortadas, notas al pie intercaladas, números de página sueltos). La síntesis
(`harro-otto-derecho-penal_synthesis.json`) se hizo igual, reconstruyendo el sentido
general por estamento; los estamentos de tentativa y autoría/participación quedaron
sin síntesis confiable por el estado del texto en esas secciones. Si en el futuro se
consigue una copia de mejor calidad (texto nativo, no escaneado), conviene reprocesar
todo el libro con el pipeline estándar (`extract_pdf.py` + `chunk_txt.py` + síntesis).

Este mismo método (Abrir con Documentos de Google) es el camino recomendado para
cualquier libro grande futuro que falle por tamaño en `read_file_content`/`download_file_content`.
