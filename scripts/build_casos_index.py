#!/usr/bin/env python3
"""Indexa el banco de casos (cero tokens de API).

Recorre cada `casos/<slug>/caso.json` y emite un índice maestro
`casos/_INDEX.json` con los datos livianos de cada caso (número, título,
institutos dogmáticos, si tiene trabajo-modelo, ruta). Sirve para buscar
rápido "¿qué casos ya vimos sobre error de tipo / imputación objetiva?" sin
abrir cada archivo, y para poblar el índice invertido instituto → casos.

Uso:
    python3 scripts/build_casos_index.py

Salida: casos/_INDEX.json
"""
import json
import sys
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
CASOS = ROOT / "casos"


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def main():
    casos = []
    for caso_json in sorted(CASOS.glob("*/caso.json")):
        try:
            data = json.loads(caso_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"AVISO: JSON inválido en {caso_json.relative_to(ROOT)}: {e}")
            continue
        meta = data.get("meta", {})
        slug = caso_json.parent.name
        resoluciones = sorted(
            str(p.relative_to(caso_json.parent)).replace("\\", "/")
            for p in (caso_json.parent / "resoluciones").glob("*.txt")
        ) if (caso_json.parent / "resoluciones").is_dir() else []
        casos.append({
            "id": meta.get("id", slug),
            "numero": meta.get("numero", ""),
            "titulo": meta.get("titulo") or "",
            "institutos_dogmaticos": data.get("institutos_dogmaticos", []),
            "tiene_modelo": bool(resoluciones) or bool(meta.get("tiene_modelo")),
            "articulos_indicados": meta.get("articulos_indicados", []),
            "resoluciones": resoluciones,
            "path": str(caso_json.relative_to(ROOT)).replace("\\", "/"),
        })

    # Índice invertido: instituto dogmático -> lista de ids de casos.
    por_instituto: dict[str, list[str]] = {}
    for c in casos:
        for inst in c["institutos_dogmaticos"]:
            por_instituto.setdefault(_norm(inst), []).append(c["id"])

    index = {
        "generated": date.today().isoformat(),
        "n_casos": len(casos),
        "n_con_modelo": sum(1 for c in casos if c["tiene_modelo"]),
        "casos": casos,
        "por_instituto": dict(sorted(por_instituto.items())),
    }
    out = CASOS / "_INDEX.json"
    out.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Índice de casos: casos/_INDEX.json "
          f"({len(casos)} casos, {index['n_con_modelo']} con modelo, "
          f"{len(por_instituto)} institutos)")
    for c in casos:
        marca = "★" if c["tiene_modelo"] else " "
        print(f"  {marca} {c['id']:14} (caso {c['numero']}) — {c['titulo'][:60]}")


if __name__ == "__main__":
    main()
