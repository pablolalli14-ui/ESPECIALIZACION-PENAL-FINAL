#!/usr/bin/env python3
"""Genera Markdown legible a partir de las síntesis de doctrina (cero tokens).

Maneja dos formatos:
  1) Síntesis por autor: doctrina/<autor>/<libro>_synthesis.json
     (autor, obra, linea_teorica, estructura_delito, posturas_debates, glosario, capitulos)
  2) Comparativa: doctrina/_COMPARATIVA_teoria_del_delito.json
     (etapas[] con autores{} y sintesis_contraste)

Uso:
    python3 scripts/doctrina_to_md.py "doctrina/frister/..._synthesis.json" [salida.md]
    python3 scripts/doctrina_to_md.py "doctrina/_COMPARATIVA_teoria_del_delito.json"
"""
import json
import sys
from pathlib import Path

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


def render_autor(d):
    L = []
    L.append(f"# {d.get('autor','Síntesis de doctrina')}")
    sub = " — ".join(x for x in [d.get("obra", ""), d.get("edicion", "")] if x)
    if sub:
        L.append(f"*{sub}*")
    if d.get("linea_teorica"):
        L.append("")
        L.append(f"**Línea teórica:** {d['linea_teorica']}")
    L.append("")
    if d.get("tesis_central"):
        L.append("## Tesis central")
        L.append("")
        L.append(d["tesis_central"])
        L.append("")
    if d.get("overview"):
        L.append("## Panorama")
        L.append("")
        L.append(d["overview"])
        L.append("")
    est = d.get("estructura_delito") or {}
    if any(est.values()):
        L.append("## Postura en la teoría del delito")
        L.append("")
        for key, label in ETAPAS_LABEL.items():
            val = est.get(key)
            if val:
                L.append(f"### {label}")
                L.append("")
                L.append(val)
                L.append("")
    if d.get("posturas_debates"):
        L.append("## Posturas en debates clave")
        L.append("")
        for p in d["posturas_debates"]:
            tema = p.get("tema", "")
            fuente = f" <sub>({p['fuente_paginas']})</sub>" if p.get("fuente_paginas") else ""
            L.append(f"- **{tema}.** {p.get('postura','')}{fuente}")
        L.append("")
    if d.get("glosario"):
        L.append("## Glosario")
        L.append("")
        for g in d["glosario"]:
            L.append(f"- **{g.get('termino','')}:** {g.get('definicion','')}")
        L.append("")
    if d.get("capitulos"):
        L.append("## Mapa de capítulos")
        L.append("")
        for c in d["capitulos"]:
            pag = f" <sub>{c['paginas']}</sub>" if c.get("paginas") else ""
            L.append(f"### {c.get('titulo','')}{pag}")
            L.append("")
            if c.get("resumen"):
                L.append(c["resumen"])
                L.append("")
    return "\n".join(L)


def render_comparativa(d):
    L = []
    L.append("# Comparativa por etapas de la teoría del delito")
    L.append("")
    L.append("*Material de referencia rápida para estudiar y para elegir la línea. "
             "NO se copia al trabajo final, que exige una sola línea doctrinal.*")
    L.append("")
    if d.get("autores"):
        L.append("Autores comparados: " + ", ".join(d["autores"]) + ".")
        L.append("")
    for et in d.get("etapas", []):
        L.append(f"## {et.get('etapa','').capitalize()}")
        L.append("")
        autores = et.get("autores") or {}
        for autor, postura in autores.items():
            if postura:
                L.append(f"- **{autor.capitalize()}:** {postura}")
        L.append("")
        if et.get("sintesis_contraste"):
            L.append(f"> **Contraste:** {et['sintesis_contraste']}")
            L.append("")
    return "\n".join(L)


def render_esquema_general(d):
    L = []
    L.append(f"# {d.get('titulo', 'Esquema general')}")
    L.append("")
    if d.get("fuente"):
        L.append(f"*Fuente: {d['fuente']}*")
        L.append("")
    if d.get("proposito"):
        L.append(d["proposito"])
        L.append("")
    for e in d.get("estamentos", []):
        L.append(f"## {e.get('estamento','')}")
        L.append("")
        if e.get("elementos"):
            L.append("**Elementos:** " + "; ".join(e["elementos"]))
            L.append("")
        if e.get("causas_exclusion"):
            L.append("**Causas de exclusión / justificación:**")
            L.append("")
            for c in e["causas_exclusion"]:
                art = f" ({c['articulo']})" if c.get("articulo") else ""
                L.append(f"- {c.get('causa','')}{art}")
            L.append("")
    if d.get("nota_relacion_con_autores"):
        L.append("> " + d["nota_relacion_con_autores"])
        L.append("")
    return "\n".join(L)


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 scripts/doctrina_to_md.py <_synthesis.json | _COMPARATIVA...json | esquema...json> [salida.md]")
    src = Path(sys.argv[1])
    d = json.loads(src.read_text(encoding="utf-8"))
    if "etapas" in d:
        md = render_comparativa(d)
    elif "estamentos" in d:
        md = render_esquema_general(d)
    else:
        md = render_autor(d)
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".md")
    out.write_text(md, encoding="utf-8")
    print(f"MD: {out}")


if __name__ == "__main__":
    main()
