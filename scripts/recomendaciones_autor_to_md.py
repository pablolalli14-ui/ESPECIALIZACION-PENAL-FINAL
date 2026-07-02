#!/usr/bin/env python3
"""Genera un Markdown legible con la recomendación de autor por caso del banco,
mostrando el enunciado de cada caso en un recuadro justo arriba de la
recomendación (para no tener que ir y volver a leerlo). Cero tokens: cruza
casos/_RECOMENDACIONES_AUTOR.json (recomendación + justificación, escritas a
mano) con cada casos/<id>/caso.json (enunciado, número, título).

Nota: un PDF generado por este pipeline (HTML -> PDF estático, sin JS) no
soporta desplegables interactivos reales; el recuadro con el enunciado queda
siempre visible, que es la forma de lograr el mismo efecto práctico.

Uso:
    python3 scripts/recomendaciones_autor_to_md.py [salida.md]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASOS = ROOT / "casos"


def main():
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else CASOS / "_RECOMENDACIONES_AUTOR.md"

    data = json.loads((CASOS / "_RECOMENDACIONES_AUTOR.json").read_text(encoding="utf-8"))
    comparativa_path = ROOT / "doctrina" / "_COMPARATIVA_teoria_del_delito.json"
    autores_nombres = {}
    if comparativa_path.exists():
        comparativa = json.loads(comparativa_path.read_text(encoding="utf-8"))
        autores_nombres = {k: v.get("nombre", k) for k, v in comparativa.get("autores", {}).items()}

    L = []
    L.append("# Recomendación de autor por caso")
    L.append("")
    L.append(
        "*" + data.get("proposito", "") + "*"
    )
    L.append("")

    for rec in data.get("recomendaciones", []):
        caso_json = CASOS / rec["caso_id"] / "caso.json"
        if not caso_json.exists():
            continue
        caso = json.loads(caso_json.read_text(encoding="utf-8"))
        meta = caso.get("meta", {})
        numero = meta.get("numero", rec["caso_id"])
        titulo = meta.get("titulo", "")
        enunciado = caso.get("enunciado", "")
        autor_slug = rec.get("autor", "")
        autor_nombre = autores_nombres.get(autor_slug, autor_slug.capitalize())

        L.append(f"## Caso {numero} — {titulo}")
        L.append("")
        L.append("> **Enunciado:**")
        L.append(">")
        for linea in enunciado.split("\n"):
            L.append(f"> {linea}")
        L.append("")
        L.append(f"**Problema dogmático:** {rec.get('problema_dogmatico', '')}")
        L.append("")
        L.append(f"**Autor recomendado: {autor_nombre}.** {rec.get('justificacion', '')}")
        L.append("")
        L.append("---")
        L.append("")

    contenido = "\n".join(L) + "\n"
    salida.write_text(contenido, encoding="utf-8")
    print(f"Recomendaciones: {salida.relative_to(ROOT)} ({len(data.get('recomendaciones', []))} casos)")


if __name__ == "__main__":
    main()
