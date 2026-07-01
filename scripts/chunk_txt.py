#!/usr/bin/env python3
"""Split an extracted book .txt into chunk files for map-reduce summarization.

Zero API tokens: pure local text processing. Tries to break on chapter/section
headings ("CAPÍTULO", "Capítulo N", "TÍTULO", "PARTE"...). If headings are sparse,
falls back to fixed-size character windows so no chunk overflows a cheap model's
context. Page markers ("=== PÁGINA n ===") are preserved inside chunks.

Usage:
    py scripts/chunk_txt.py "books/<file>.txt" [--max-chars 24000] [--target 10]

Writes:
    books/_chunks/<file-stem>/chunk_00.txt, chunk_01.txt, ...
    books/_chunks/<file-stem>/manifest.txt   (one line per chunk: name + char count)
"""
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(
    r"^\s*(CAP[IÍ]TULO|Cap[ií]tulo|T[IÍ]TULO|T[ií]tulo|PARTE|Parte|SECCI[OÓ]N|Secci[oó]n)\b.*$",
    re.MULTILINE,
)


def parse_args(argv):
    path = None
    max_chars = 24000
    target = 10
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--max-chars":
            max_chars = int(argv[i + 1]); i += 2
        elif a == "--target":
            target = int(argv[i + 1]); i += 2
        elif path is None:
            path = a; i += 1
        else:
            i += 1
    if path is None:
        sys.exit("Uso: py scripts/chunk_txt.py <ruta.txt> [--max-chars N] [--target N]")
    return Path(path), max_chars, target


def split_on_headings(text, max_chars):
    """Build segments at heading boundaries, then pack them up to max_chars."""
    idxs = [m.start() for m in HEADING_RE.finditer(text)]
    if len(idxs) < 3:
        return None  # too few headings; caller falls back to fixed windows
    if idxs[0] != 0:
        idxs = [0] + idxs
    idxs.append(len(text))
    raw = [text[idxs[i]:idxs[i + 1]] for i in range(len(idxs) - 1)]
    # Pack consecutive segments until adding the next would exceed max_chars.
    chunks, cur = [], ""
    for seg in raw:
        if cur and len(cur) + len(seg) > max_chars:
            chunks.append(cur); cur = seg
        else:
            cur += seg
    if cur.strip():
        chunks.append(cur)
    return chunks


def split_fixed(text, n_chunks):
    """Even character windows, nudged to the next newline to avoid mid-line cuts."""
    n = max(1, n_chunks)
    size = max(1, len(text) // n)
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + size)
        nl = text.find("\n", end)
        if nl != -1 and nl - end < 2000:
            end = nl
        chunks.append(text[start:end])
        start = end
    return [c for c in chunks if c.strip()]


def main():
    txt_path, max_chars, target = parse_args(sys.argv)
    if not txt_path.is_file():
        sys.exit(f"No existe el .txt: {txt_path}")
    text = txt_path.read_text(encoding="utf-8", errors="replace")

    chunks = split_on_headings(text, max_chars)
    mode = "headings"
    if chunks is None or len(chunks) < 2:
        # Choose chunk count so chunks stay under max_chars but near target.
        by_size = (len(text) // max_chars) + 1
        chunks = split_fixed(text, max(target, by_size))
        mode = "fixed"

    out_dir = txt_path.parent / "_chunks" / txt_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    # Clear any stale chunks from a previous run.
    for old in out_dir.glob("chunk_*.txt"):
        old.unlink()

    manifest = []
    for i, c in enumerate(chunks):
        name = f"chunk_{i:02d}.txt"
        (out_dir / name).write_text(c, encoding="utf-8")
        manifest.append(f"{name}\t{len(c)} chars")
    (out_dir / "manifest.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(f"TXT:     {txt_path}")
    print(f"Modo:    {mode}")
    print(f"Chunks:  {len(chunks)}")
    print(f"Salida:  {out_dir}")
    for line in manifest:
        print("  " + line)


if __name__ == "__main__":
    main()
