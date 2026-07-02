# Proyecto: Especialización Penal — banco de casos, doctrina y pipeline de PDFs

Base de conocimiento para el **Trabajo Final** de la Carrera de Especialización en
Derecho Penal (UBA): almacena los **casos** que suelen tomarse, **cómo se resuelven**
(trabajos-modelo aprobados + síntesis de doctrina) y la **doctrina** de los autores de
referencia, todo procesado una sola vez con un pipeline eficiente en tokens.

## Regla de lectura de PDFs (importante, ahorro de tokens)

**Nunca leas archivos `.pdf` directamente para trabajo de texto completo.**

Para cada PDF debe existir, al lado, un `.txt` pre-extraído (texto plano) y, cuando se
necesite reutilizar el contenido entre sesiones, un `*_synthesis.json` (síntesis
estructurada).

Cómo trabajar:
- Para **análisis o lectura de contenido** → lee el `.txt`.
- Para **reutilizar** lo ya procesado (resúmenes, posturas de autor, conceptos) → lee el
  `*_synthesis.json` si existe. Es casi gratis en tokens y debe ser la primera fuente.
- Solo usa el **MCP `pdf-reader`** para lecturas puntuales de páginas o búsquedas.

Si falta un `.txt` para un PDF con texto, genéralo (no cuesta tokens de API):

```
python3 scripts/extract_pdf.py "<archivo>.pdf"
```

Si el PDF es un **escaneo de imágenes** (pypdf devuelve 0 páginas con texto), usa OCR
(requiere Tesseract + datos de idioma `spa`; en este entorno están instalados):

```
python3 scripts/ocr_pdf.py "<archivo>.pdf" --lang spa --dpi 300
```

> Los libros de doctrina se aportaron por Google Drive. Como son PDFs muy grandes
> (17–62 MB), su texto se obtuvo con el MCP de Drive (`read_file_content`, que hace la
> extracción del lado del servidor y guarda el resultado en un archivo) y se copió al
> `.txt` de cada autor. No hace falta el PDF binario en el repo.

Para sintetizar un `.txt` largo: trocearlo con `python3 scripts/chunk_txt.py "<archivo>.txt"`
y ejecutar un pase map-reduce (subagentes Haiku por chunk → pase final que escribe
`<archivo>_synthesis.json`). Para convertir una síntesis a Markdown/PDF legible, usar
`scripts/synthesis_to_md.py` + `scripts/md_to_pdf.py`.

## Pipeline / herramientas

- MCP de PDF: `@sylphx/pdf-reader-mcp` (`.mcp.json`, se lanza con `npx`; requiere Node).
- Extracción local: `scripts/extract_pdf.py` (`pypdf`).
- OCR de escaneos: `scripts/ocr_pdf.py` (PyMuPDF + pytesseract).
- Troceado para síntesis: `scripts/chunk_txt.py`.
- Síntesis legible: `scripts/synthesis_to_md.py` (un `_synthesis.json` → `.md`).
- Markdown → PDF: `scripts/md_to_pdf.py` (`markdown` + `xhtml2pdf`, sin deps de sistema).
- Índice del banco de casos: `scripts/build_casos_index.py` (cero tokens; lee los
  `casos/*/caso.json` y escribe `casos/_INDEX.json`).

Dependencias de Python en `requirements.txt` (`python3 -m pip install -r requirements.txt`).
En este entorno Linux los scripts se corren con `python3` (el `py` de la doc es el
launcher de Windows).

## Reglas del Trabajo Final (`pautas/`)

`pautas/PAUTAS_TRABAJO_FINAL.md` es el **checklist rector** (transcripción de la pauta
estricta de la cátedra). Reglas duras: estructura fija (Sumario · Introducción · Planteo
del problema · Solución dogmática · Conclusiones · Bibliografía), **una sola línea
doctrinal sin mezclar autores**, sin jurisprudencia / derecho comparado / tratados /
discusión procesal / discusión constitucional / códigos de otros países / criminología;
no estipular pena; no elaborar sentencia ni defensa; **no modificar los hechos**; notas
al pie solo bibliográficas; ~10 páginas.

`pautas/_SEÑALES_INSTITUTOS.json` es una checklist de patrones narrativos → institutos
dogmáticos típicos (desajuste dolo/resultado, dolus generalis, legítima defensa y sus
patologías, tentativa inidónea/supersticiosa, imputabilidad/emoción violenta, aportes
de terceros, consentimiento), extraída de los 14 casos ya cargados. Apoya la detección
de institutos al leer un enunciado nuevo (Paso 1 del skill); no reemplaza la lectura
del caso concreto.

## Banco de casos (`casos/`)

Un caso por carpeta `casos/<slug>/`:
- `caso.json` — enunciado **literal** + sujetos + `institutos_dogmaticos` +
  `problema_central` + `lineas_solucion` (por autor, se completan de a poco).
- `resoluciones/` — trabajos-modelo aprobados de ese caso (`<alumno>.txt`) +
  `_modelos.json` (autores usados, tesis, estructura, resultado). Los modelos sirven
  como referencia de **estructura y razonamiento**; ojo: algunos comparan autores, cosa
  que la pauta vigente prohíbe (usar solo como modelo estructural).
- Índice maestro `casos/_INDEX.json` (regenerar con `build_casos_index.py`): lista
  liviana + índice invertido `por_instituto` (instituto dogmático → casos).

Esquema completo de `caso.json` y flujo de resolución: skill `resolver-caso-penal`.

## Doctrina (`doctrina/`)

Una carpeta por autor (`frister`, `otto`, `roxin`, `jakobs`, `wessels`, `hilgendorf`),
con el `.txt` del libro y su `<archivo>_synthesis.json` (+ render `.md`/`.pdf`). La
síntesis está orientada a la teoría del delito: `estructura_delito` (postura del autor
en cada estamento: acción, tipicidad objetiva, imputación objetiva, tipo subjetivo/dolo,
error de tipo, antijuridicidad, culpabilidad, error de prohibición, tentativa, autoría y
participación), `posturas_debates`, `glosario` y `capitulos`.

`doctrina/_COMPARATIVA_teoria_del_delito.json` (+ render) contrasta a los 6 autores por
etapa de la teoría del delito — **material de referencia rápida para estudiar y para
elegir la línea**; NO se copia al trabajo (que exige una sola línea).

`doctrina/_CRITERIO_SELECCION_AUTOR.json` recomienda, por etapa de la teoría del
delito y por instituto específico, qué autor conviene usar como línea única —
combina la comparativa teórica con evidencia empírica (qué autor usaron los
modelos aprobados para institutos similares). Es un default razonado, no una regla
rígida: el skill lo consulta y **siempre se lo muestra al usuario para confirmar**
antes de redactar.

`doctrina/GUIA_AUTORES_INSTITUTOS.md/.pdf` es una guía de estudio compuesta (cero
tokens, `scripts/guia_autores_institutos.py`) a partir de las síntesis + la
comparativa + el criterio de selección: perfil de cada autor, postura por
estamento, glosario combinado y recomendación de autor. Regenerar tras agregar o
editar una síntesis.

`doctrina/_auxiliar/` guarda material complementario que no es la postura de un
autor de línea (ni un caso): p. ej. `esquema_general_cp_argentino.json` (+ render),
un mapa mnemotécnico de la teoría del delito referido a los artículos del Código
Penal argentino (art. 34 y ss.), útil como checklist estructural independiente de
la línea doctrinal elegida.

**Estado de fuentes pendientes:** Otto (62 MB) y Rafecas — *Derecho penal sobre
bases constitucionales* (37–41 MB, escaneado sin capa de texto) no pudieron
extraerse vía Drive por tamaño; ver `doctrina/otto/_PENDIENTE.md`. Rafecas se
usa como bibliografía secundaria en varios trabajos-modelo del banco, pero su
enfoque constitucional no puede ser la línea única del trabajo final (la pauta
prohíbe discusión constitucional) — solo serviría como referencia complementaria,
no como una 7ª línea de autor.

## Skill de resolución (`.claude/skills/resolver-caso-penal/`)

De un enunciado produce un borrador del trabajo final respetando `pautas/`: elige UNA
línea de autor, usa su `_synthesis.json` como fuente, se apoya en `casos/_INDEX.json`
para hallar precedentes de estructura, y entrega en Markdown/texto plano (no PDF, salvo
pedido) para pegar en Word con el formato exigido.
