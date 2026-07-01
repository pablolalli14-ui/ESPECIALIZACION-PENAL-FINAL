#!/usr/bin/env python3
"""Genera un Markdown legible a partir de un _synthesis.json de un libro.

Cero tokens de API: solo formatea el JSON ya generado. Escribe un archivo
hermano <stem>.md (donde <stem> es el del .json, sin la extensión).

Uso:
    py scripts/synthesis_to_md.py "books/.../<libro>_synthesis.json" [salida.md]
"""
import json
import sys
from pathlib import Path


def render(d):
    L = []
    title = d.get("title", "Síntesis")
    L.append(f"# {title}")
    if d.get("author"):
        L.append(f"*{d['author']}*"
                 + (f" — {d['edition']}" if d.get("edition") else ""))
    L.append("")
    if d.get("page_count"):
        L.append(f"<sub>{d['page_count']} págs. · {d.get('method','')}</sub>")
        L.append("")
    if d.get("thesis"):
        L.append("## Tesis")
        L.append("")
        L.append(d["thesis"])
        L.append("")
    if d.get("overview"):
        L.append("## Panorama")
        L.append("")
        L.append(d["overview"])
        L.append("")
    if d.get("chapters"):
        L.append("## Mapa de capítulos")
        L.append("")
        for c in d["chapters"]:
            L.append(f"### {c.get('heading','')}")
            L.append("")
            L.append(c.get("summary", ""))
            L.append("")
    if d.get("key_concepts"):
        L.append("## Conceptos clave")
        L.append("")
        for k in d["key_concepts"]:
            L.append(f"- {k}")
        L.append("")
    if d.get("protocolos_accionables"):
        L.append("## Protocolos accionables")
        L.append("")
        for p in d["protocolos_accionables"]:
            L.append(f"### {p.get('id','')} · {p.get('nombre','')}")
            meta = " · ".join(x for x in [p.get("fase_litigacion", ""),
                                          p.get("fuente_paginas", "")] if x)
            if meta:
                L.append(f"<sub>{meta}</sub>")
            L.append("")
            if p.get("objetivo"):
                L.append(f"**Objetivo.** {p['objetivo']}")
                L.append("")
            if p.get("cuando_usar"):
                L.append("**Cuándo usar:** " + "; ".join(p["cuando_usar"]) + ".")
                L.append("")
            if p.get("reglas"):
                L.append("**Reglas:**")
                for r in p["reglas"]:
                    L.append(f"- {r}")
                L.append("")
            if p.get("pasos"):
                L.append("**Pasos:**")
                for i, s in enumerate(p["pasos"], 1):
                    L.append(f"{i}. {s}")
                L.append("")
            if p.get("errores_a_evitar"):
                L.append("**Errores a evitar:**")
                for e in p["errores_a_evitar"]:
                    L.append(f"- {e}")
                L.append("")
            if p.get("disparadores_decision"):
                L.append("**Disparadores de decisión:**")
                for x in p["disparadores_decision"]:
                    L.append(f"- {x}")
                L.append("")
    if d.get("checklists"):
        L.append("## Checklists")
        L.append("")
        for c in d["checklists"]:
            L.append(f"**{c.get('nombre','')}**")
            L.append("")
            for it in c.get("items", []):
                L.append(f"- {it}")
            L.append("")
    return "\n".join(L)


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: py scripts/synthesis_to_md.py <_synthesis.json> [salida.md]")
    src = Path(sys.argv[1])
    d = json.loads(src.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".md")
    out.write_text(render(d), encoding="utf-8")
    print(f"MD: {out}")


if __name__ == "__main__":
    main()
