---
name: resolver-caso-penal
description: Asiste la redacción del trabajo final de la Especialización en Derecho Penal (UBA) a partir de un enunciado de caso. Produce un borrador con la estructura obligatoria (Sumario, Introducción, Planteo del problema, Solución dogmática, Conclusiones, Bibliografía) respetando estrictamente las pautas de la cátedra: UNA sola línea doctrinal (sin mezclar autores), sin jurisprudencia, sin derecho comparado, sin tratados internacionales, sin discusión procesal ni constitucional, y sin modificar los hechos. Úsala cuando el usuario quiera resolver, analizar o redactar la resolución de un caso penal para el trabajo final.
---

# Resolver un caso para el Trabajo Final (Especialización en Derecho Penal, UBA)

Este skill ayuda a redactar el análisis dogmático de un caso siguiendo **al pie** las
pautas de la cátedra. El objetivo NO es un dictamen ni una sentencia: es un análisis
de teoría del delito, con una sola corriente doctrinal, centrado en el caso.

## Paso 0 — Leer las reglas (obligatorio)

Leé `pautas/PAUTAS_TRABAJO_FINAL.md` **antes de redactar** y respetalas literalmente.
Reglas duras que no se pueden violar:

- **Una sola línea doctrinal.** Elegí UN autor (Frister, Otto, Roxin, Jakobs, Wessels
  o Hilgendorf) y resolvé todo el caso desde su sistema. **NO comparar autores, NO
  mezclar líneas contrarias.** (Los trabajos-modelo del banco a veces comparan autores:
  son modelo de *estructura*, no de este punto.)
- **NO** jurisprudencia, **NO** derecho comparado, **NO** tratados internacionales,
  **NO** discusión procesal, **NO** discusión constitucional, **NO** códigos de otros
  países, **NO** criminología, **NO** estipular pena, **NO** elaborar sentencia ni defensa.
- **NO modificar los hechos** ni agregar datos que no están en el relato. Si falta un
  dato, eso mismo es parte del problema a analizar (no se inventa).
- Notas al pie: **SOLO bibliografía** (parafraseo con referencia; no citas textuales).
- Centrarse en el caso en todo momento: no exponer conceptos en abstracto, no dar
  ejemplos ajenos, no contar por qué se descartan otras teorías.
- Extensión objetivo: ~10 páginas (≈8 para la Solución dogmática).

## Paso 1 — Cargar el caso

- Si el usuario da un enunciado nuevo: transcribilo **literal** a `casos/<slug>/caso.json`
  (esquema abajo) sin alterar hechos. Si viene en PDF/imagen, extraelo con el pipeline
  (`scripts/extract_pdf.py`, o `scripts/ocr_pdf.py --lang spa` si es escaneo) o leelo.
- Si ya está en el banco: leé su `casos/<slug>/caso.json`.
- Identificá: sujetos intervinientes, tipo(s) penal(es) en juego, y los **institutos
  dogmáticos** centrales (imputación objetiva, error de tipo/prohibición, tentativa,
  autoría y participación, causas de justificación, culpabilidad, etc.).

## Paso 2 — Buscar precedentes de estructura

Leé `casos/_INDEX.json` (índice liviano, casi gratis en tokens). Usá `por_instituto`
para encontrar casos del banco con institutos afines y mirá sus `resoluciones/` como
**modelo de estructura y razonamiento** (no para copiar contenido: cada caso tiene
sus propios hechos). Buscá también `casos/<slug>/resoluciones/_modelos.json`.

## Paso 3 — Elegir UNA línea de autor y traer su doctrina

Elegí un autor y cargá su síntesis en `doctrina/<autor>/<archivo>_synthesis.json`
(primera fuente, barata en tokens). Usá su bloque `estructura_delito` y
`posturas_debates` para fundamentar cada estamento del análisis, y citá la obra en
nota al pie. Si necesitás contrastar rápido posturas para **elegir** el autor (no para
el trabajo), consultá `doctrina/_COMPARATIVA_teoria_del_delito.json` — pero recordá:
la comparativa es para vos, NO va al trabajo (que exige una sola línea).

Si falta la síntesis del autor: generala con el pipeline (ver CLAUDE.md, Fase doctrina).

## Paso 4 — Redactar con la estructura obligatoria

1. **Sumario:** I. Introducción · II. Planteo del problema · III. Solución dogmática
   [con subtítulos] · IV. Conclusiones · V. Bibliografía.
2. **Introducción** (1 párrafo): número/nombre del caso, conductas a analizar y
   responsabilidad de cada sujeto. NO contar el caso.
3. **Planteo del problema** (1-2 párrafos): el problema dogmático específico y el tipo
   penal. Si hay variantes o varios momentos, un problema por cada uno.
4. **Solución dogmática** (~8 págs): recorrer la teoría del delito del autor elegido
   aplicada al caso (acción → tipicidad objetiva/imputación objetiva → tipo subjetivo/
   dolo/error → antijuridicidad → culpabilidad → en su caso tentativa, autoría/
   participación). Siempre pegado a los hechos. Fuente en nota al pie.
5. **Conclusiones** (1-2 párrafos): solución/responsabilidad para **cada** sujeto.
6. **Bibliografía:** formato de la cátedra (Apellido, N., *Título en cursiva*, ciudad,
   editorial, año).
7. **Anexo:** adjuntar el enunciado del caso al final.

## Paso 5 — Entregar

Salida en **Markdown / texto plano** (no PDF), para que el usuario lo pegue en Word con
el formato exigido (A4, Times New Roman/Arial 12, interlineado 1,5, notas al pie cuerpo
10, numeración automática 1-10). Generá PDF **solo si el usuario lo pide** (con
`scripts/md_to_pdf.py`). Antes de cerrar, verificá contra el checklist del Paso 0.

## Esquema de `casos/<slug>/caso.json`

```jsonc
{
  "meta": { "id":"caso-05", "numero":"V", "titulo":"", "fuente":"",
            "articulos_indicados":[], "consigna":"", "tiene_modelo":false },
  "enunciado":"texto LITERAL del caso, sin modificar ni completar hechos",
  "sujetos":[ { "nombre":"A", "rol":"activo|pasivo|tercero", "notas":"" } ],
  "institutos_dogmaticos":[ "..." ],
  "problema_central":"1-2 frases: qué categoría de la teoría del delito se pone en juego",
  "lineas_solucion":{ "frister":{ "resumen":"", "resultado":"" }, "otto":{}, "roxin":{},
                      "jakobs":{}, "wessels":{}, "hilgendorf":{} },
  "modelos_disponibles":[ "resoluciones/<alumno>.txt" ],
  "notas":""
}
```
Tras crear o editar casos, regenerá el índice: `python3 scripts/build_casos_index.py`.
