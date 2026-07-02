#!/usr/bin/env python3
"""Genera una guía de estudio (Markdown) de los autores y los institutos de la
teoría del delito, combinando las síntesis por autor (doctrina/<autor>/*_synthesis.json)
y la comparativa transversal (doctrina/_COMPARATIVA_teoria_del_delito.json).

Cero tokens: solo lee y reordena datos ya sintetizados, no vuelve a leer los libros.

Uso:
    python3 scripts/guia_autores_institutos.py [salida.md]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCTRINA = ROOT / "doctrina"
CASOS = ROOT / "casos"

ETAPAS_LABEL = {
    "accion": "Acción",
    "tipicidad_objetiva": "Tipicidad objetiva",
    "imputacion_objetiva": "Imputación objetiva",
    "tipicidad_subjetiva_dolo": "Tipo subjetivo · Dolo",
    "error_de_tipo": "Error de tipo",
    "antijuridicidad": "Antijuridicidad",
    "culpabilidad": "Culpabilidad",
    "error_de_prohibicion": "Error de prohibición",
    "tentativa": "Tentativa",
    "autoria_participacion": "Autoría y participación",
}

AUTOR_ORDEN = ["frister", "otto", "roxin", "jakobs", "wessels", "hilgendorf"]


def cargar_sintesis():
    sintesis = {}
    for autor in AUTOR_ORDEN:
        carpeta = DOCTRINA / autor
        if not carpeta.is_dir():
            continue
        archivos = sorted(carpeta.glob("*_synthesis.json"))
        if archivos:
            sintesis[autor] = json.loads(archivos[0].read_text(encoding="utf-8"))
    return sintesis


def main():
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else DOCTRINA / "GUIA_AUTORES_INSTITUTOS.md"

    sintesis = cargar_sintesis()
    comparativa_path = DOCTRINA / "_COMPARATIVA_teoria_del_delito.json"
    comparativa = json.loads(comparativa_path.read_text(encoding="utf-8")) if comparativa_path.exists() else None

    lineas = []
    lineas.append("# Guía de autores e institutos de la teoría del delito")
    lineas.append("")
    lineas.append(
        "*Especialización en Derecho Penal (UBA) — material de estudio y de apoyo para elegir "
        "la línea doctrinal del Trabajo Final. Resume las síntesis de "
        f"{len(sintesis)} de 6 autores procesados. NO reemplaza la lectura de los libros ni se "
        "copia tal cual al trabajo, que exige una sola línea doctrinal sin comparar autores.*"
    )
    lineas.append("")

    # --- Parte 1: perfil de cada autor ---
    lineas.append("## Parte 1 — Perfil de cada autor")
    lineas.append("")
    for autor in AUTOR_ORDEN:
        datos = sintesis.get(autor)
        if not datos:
            lineas.append(f"### {autor.capitalize()} — pendiente")
            lineas.append("")
            lineas.append(
                "Síntesis todavía no disponible (ver `doctrina/otto/_PENDIENTE.md`)."
                if autor == "otto" else "Síntesis todavía no disponible."
            )
            lineas.append("")
            continue
        lineas.append(f"### {datos.get('autor', autor.capitalize())}")
        lineas.append("")
        if datos.get("obra"):
            edicion = f" ({datos['edicion']})" if datos.get("edicion") else ""
            lineas.append(f"**Obra:** *{datos['obra']}*{edicion}")
            lineas.append("")
        if datos.get("linea_teorica"):
            lineas.append(f"**Línea teórica:** {datos['linea_teorica']}")
            lineas.append("")
        if datos.get("tesis_central"):
            lineas.append(f"**Tesis central:** {datos['tesis_central']}")
            lineas.append("")
        if datos.get("overview"):
            lineas.append(datos["overview"])
            lineas.append("")

    # --- Parte 2: guía por institutos (etapas de la teoría del delito) ---
    lineas.append("## Parte 2 — Guía por institutos de la teoría del delito")
    lineas.append("")
    lineas.append(
        "Para cada estamento de la teoría del delito, la postura resumida de cada autor "
        "disponible y en qué coinciden o se apartan entre sí."
    )
    lineas.append("")

    if comparativa:
        for etapa in comparativa.get("etapas", []):
            nombre = ETAPAS_LABEL.get(etapa["etapa"], etapa["etapa"].replace("_", " ").capitalize())
            lineas.append(f"### {nombre}")
            lineas.append("")
            for autor in AUTOR_ORDEN:
                postura = etapa.get("autores", {}).get(autor)
                if postura:
                    nombre_autor = comparativa.get("autores", {}).get(autor, {}).get("nombre", autor.capitalize())
                    lineas.append(f"- **{nombre_autor}:** {postura}")
            lineas.append("")
            if etapa.get("sintesis_contraste"):
                lineas.append(f"> **En síntesis:** {etapa['sintesis_contraste']}")
                lineas.append("")

    # --- Parte 3: glosario combinado ---
    lineas.append("## Parte 3 — Glosario combinado")
    lineas.append("")
    lineas.append("Términos clave de las síntesis, agrupados por autor de origen (puede haber solapamiento conceptual entre autores).")
    lineas.append("")
    for autor in AUTOR_ORDEN:
        datos = sintesis.get(autor)
        if not datos or not datos.get("glosario"):
            continue
        nombre_autor = datos.get("autor", autor.capitalize())
        lineas.append(f"**{nombre_autor}**")
        lineas.append("")
        for entrada in datos["glosario"]:
            termino = entrada.get("termino", "")
            definicion = entrada.get("definicion", "")
            lineas.append(f"- *{termino}:* {definicion}")
        lineas.append("")

    # --- Parte 4: cómo elegir autor (referencia al criterio ya construido) ---
    criterio_path = DOCTRINA / "_CRITERIO_SELECCION_AUTOR.json"
    if criterio_path.exists():
        criterio = json.loads(criterio_path.read_text(encoding="utf-8"))
        lineas.append("## Parte 4 — Cómo elegir el autor para un caso")
        lineas.append("")
        lineas.append(criterio.get("proposito", ""))
        lineas.append("")
        lineas.append("**Recomendación por estamento (default, ver `doctrina/_CRITERIO_SELECCION_AUTOR.json` para el detalle y las excepciones por instituto específico):**")
        lineas.append("")
        for etapa_key, info in criterio.get("por_etapa", {}).items():
            nombre = ETAPAS_LABEL.get(etapa_key, etapa_key.replace("_", " ").capitalize())
            autor_rec = info.get("autor_recomendado", "")
            nombre_autor = (comparativa or {}).get("autores", {}).get(autor_rec, {}).get("nombre", autor_rec.capitalize())
            lineas.append(f"- **{nombre}** → {nombre_autor}. {info.get('justificacion', '')}")
        lineas.append("")

    # --- Parte 5: recomendación de autor por caso del banco ---
    recomendaciones_path = CASOS / "_RECOMENDACIONES_AUTOR.json"
    if recomendaciones_path.exists():
        recs = json.loads(recomendaciones_path.read_text(encoding="utf-8"))
        lineas.append("## Parte 5 — Recomendación de autor por caso del banco")
        lineas.append("")
        lineas.append(recs.get("proposito", ""))
        lineas.append("")
        for rec in recs.get("recomendaciones", []):
            caso_json = CASOS / rec["caso_id"] / "caso.json"
            if not caso_json.exists():
                continue
            caso = json.loads(caso_json.read_text(encoding="utf-8"))
            meta = caso.get("meta", {})
            numero = meta.get("numero", rec["caso_id"])
            titulo = meta.get("titulo", "")
            enunciado = caso.get("enunciado", "")
            autor_slug = rec.get("autor", "")
            nombre_autor = (comparativa or {}).get("autores", {}).get(autor_slug, {}).get("nombre", autor_slug.capitalize())

            lineas.append(f"### Caso {numero} — {titulo}")
            lineas.append("")
            lineas.append("> **Enunciado:**")
            lineas.append(">")
            for linea_enun in enunciado.split("\n"):
                lineas.append(f"> {linea_enun}")
            lineas.append("")
            lineas.append(f"**Problema dogmático:** {rec.get('problema_dogmatico', '')}")
            lineas.append("")
            lineas.append(f"**Autor recomendado: {nombre_autor}.** {rec.get('justificacion', '')}")
            lineas.append("")

    contenido = "\n".join(lineas) + "\n"
    salida.write_text(contenido, encoding="utf-8")
    print(f"Guía generada: {salida.relative_to(ROOT)} ({len(contenido.splitlines())} líneas)")


if __name__ == "__main__":
    main()
