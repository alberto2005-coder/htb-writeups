#!/usr/bin/env python3
"""Generate repository catalogues and statistics from tracked, publishable Markdown."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "machines": ("Máquinas", "Machines", "machines"),
    "challenges": ("Retos", "Challenges", "challenges"),
    "sherlocks": ("Sherlocks", "Sherlocks", "sherlocks"),
    "knowledge": ("Conocimiento", "Knowledge", "knowledge"),
}

def published_files():
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "-co", "--exclude-standard"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        )
        paths = [Path(x) for x in out.splitlines() if x]
    except (OSError, subprocess.CalledProcessError):
        paths = [p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file()]
    def is_excluded(p):
        value = p.as_posix()
        if any(part in {".git", "private", ".venv", "node_modules"} for part in p.parts):
            return True
        return any(value.startswith(f"{category}/active/") for category in ("machines", "challenges", "sherlocks"))
    return {p.as_posix() for p in paths if not is_excluded(p)}

def paired_writeups(files, category):
    found = []
    prefix = category + "/"
    for value in sorted(files, key=str.casefold):
        p = Path(value)
        if not value.startswith(prefix):
            continue
        if category == "knowledge":
            if p.suffix != ".md" or p.name == "README.md" or p.name.endswith(".en.md"):
                continue
            en = p.with_name(p.stem + ".en.md").as_posix()
            if en in files:
                found.append(p)
        else:
            if p.name != "README.md" or len(p.parts) < (4 if category == "machines" else 3):
                continue
            if p.with_name("README.en.md").as_posix() in files:
                found.append(p)
    return found

def link(path):
    return quote(path.as_posix(), safe="/")

def render_index(category, title, lang, docs):
    out = [f"# {title}", "", "<!-- AUTO-GENERATED FILE. DO NOT EDIT MANUALLY. -->", ""]
    if lang == "es":
        out += ["Este índice se genera a partir de las fichas versionadas del repositorio.", ""]
        label = "Ficha"
    else:
        out += ["This index is generated from the repository's versioned writeups.", ""]
        label = "Writeup"
    if not docs:
        out += ["_No entries found._", ""]
    else:
        out += ["| " + ("Ruta" if lang == "es" else "Path") + " | " + label + " |",
                "|---|---|"]
        for p in docs:
            if category == "knowledge":
                target = p.with_name(p.stem + ".en.md") if lang == "en" else p
                rel = p.relative_to(Path(category)).with_suffix("").as_posix()
                name = p.stem
            else:
                target = p
                rel = p.parent.relative_to(Path(category)).as_posix()
                name = p.parent.name
            out.append(f"| `{rel}` | [{name}]({link(target.relative_to(Path(category)))}) |")
        out.append("")
    return "\n".join(out)

def stats(files):
    counts = {}
    for category in CATEGORIES:
        counts[category] = len(paired_writeups(files, category))
    counts["writeups"] = counts["machines"] + counts["challenges"] + counts["sherlocks"]
    return counts

def replace_region(path, start, end, replacement, check):
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        raise SystemExit(f"Missing generated markers in {path.relative_to(ROOT)}")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    new = before + start + "\n" + replacement.rstrip() + "\n" + end + after
    if check:
        if new != text:
            raise SystemExit(f"Generated content is stale: {path.relative_to(ROOT)} (run tools/generate_indexes.py)")
    else:
        path.write_text(new, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()
    files = published_files()
    counts = stats(files)
    outputs = []
    for category, (es, en, dirname) in CATEGORIES.items():
        docs = paired_writeups(files, category)
        if category == "knowledge":
            # Knowledge notes use topic/name.md + topic/name.en.md rather than README pairs.
            es_path, en_path = ROOT/"knowledge/README.md", ROOT/"knowledge/README.en.md"
        else:
            es_path, en_path = ROOT/category/"INDEX.generated.md", ROOT/category/"INDEX.generated.en.md"
        outputs.append((es_path, render_index(category, es, "es", docs)))
        outputs.append((en_path, render_index(category, en, "en", docs)))

    for path, content in outputs:
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Generated file is stale: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    es_stats = (
        f"- **Writeups:** {counts['writeups']} "
        f"({counts['machines']} máquinas, {counts['challenges']} retos y {counts['sherlocks']} Sherlocks; fichas ES/EN).\n"
        f"- **Conocimiento:** {counts['knowledge']} temas con fichas ES/EN."
    )
    en_stats = (
        f"- **Writeups:** {counts['writeups']} "
        f"({counts['machines']} machines, {counts['challenges']} challenges and {counts['sherlocks']} Sherlocks; ES/EN writeups).\n"
        f"- **Knowledge:** {counts['knowledge']} topics with ES/EN notes."
    )
    replace_region(ROOT/"README.md", "<!-- BEGIN AUTO-GENERATED STATS -->",
                   "<!-- END AUTO-GENERATED STATS -->", es_stats, args.check)
    replace_region(ROOT/"README.en.md", "<!-- BEGIN AUTO-GENERATED STATS -->",
                   "<!-- END AUTO-GENERATED STATS -->", en_stats, args.check)
    print("Statistics:", json.dumps(counts, ensure_ascii=False, sort_keys=True))
    print("Generated indexes:", len(outputs))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
