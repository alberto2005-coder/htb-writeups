#!/usr/bin/env python3
"""Dependency-free repository sanity checks."""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FRONT_MATTER_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
ERRORS = []

def git_files():
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "-co", "--exclude-standard"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        )
        return [Path(x) for x in out.splitlines() if x]
    except Exception:
        return [p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file()]

def check_front_matter(files):
    """Validate the flat YAML front matter used by every writeup.

    The blocks are simple ``key: value`` mappings. This checker rejects the
    syntax errors a YAML parser would reject in that subset, including an
    unquoted colon followed by a space, unterminated quotes, tabs, duplicate
    keys and malformed or unterminated blocks. It reports file and line.
    """
    for rel in files:
        if rel.suffix.lower() not in {".md", ".markdown"}:
            continue
        path = ROOT / rel
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        if not lines or lines[0].strip() != "---":
            continue
        end = None
        for index, line in enumerate(lines[1:], 2):
            if line.strip() == "---":
                end = index
                break
        if end is None:
            ERRORS.append(f"{rel}:1: unterminated YAML front matter")
            continue

        seen = {}
        for number, line in enumerate(lines[1:end - 1], 2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if "\t" in line:
                ERRORS.append(f"{rel}:{number}: tab character in YAML front matter")
                continue
            match = FRONT_MATTER_KEY_RE.match(line)
            if not match:
                ERRORS.append(f"{rel}:{number}: invalid YAML front-matter line: {line.strip()!r}")
                continue
            key, value = match.group(1), (match.group(2) or "").strip()
            if key in seen:
                ERRORS.append(f"{rel}:{number}: duplicate front-matter key {key!r} (first at line {seen[key]})")
            else:
                seen[key] = number
            if not value:
                continue
            if value[0] in "\"'":
                if len(value) < 2 or value[-1] != value[0]:
                    ERRORS.append(f"{rel}:{number}: unterminated quoted value for {key!r}")
                continue
            if ": " in value or value.endswith(":"):
                ERRORS.append(
                    f"{rel}:{number}: unquoted ':' in {key!r}; quote the value"
                )
            if value.startswith(("[", "{")) and value[-1] not in "]}":
                ERRORS.append(f"{rel}:{number}: unterminated flow collection for {key!r}")


def check_links(files):
    for rel in files:
        if rel.suffix.lower() not in {".md", ".markdown"}:
            continue
        path = ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for raw in LINK_RE.findall(text):
            target = raw.strip().split()[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                ERRORS.append(f"{rel}: link escapes repository: {raw}")
                continue
            if not candidate.exists():
                ERRORS.append(f"{rel}: broken relative link: {raw}")

def main():
    files = git_files()
    names = {p.as_posix() for p in files}
    if any(p.startswith("private/") for p in names):
        ERRORS.append("private/: private files must not be tracked or included in the published file set")
    if any(re.match(r"(machines|challenges|sherlocks)/active/", p) for p in names):
        ERRORS.append("active writeups are tracked; remove them from the public index")
    for category in ("machines", "challenges", "sherlocks"):
        for p in files:
            value = p.as_posix()
            if value.startswith(category + "/") and value.endswith("/README.md") and "/active/" not in value:
                en = value[:-9] + "README.en.md"
                if en not in names:
                    ERRORS.append(f"{value}: missing English counterpart {en}")
    for name in ("README.md", "README.en.md"):
        path = ROOT / name
        if path.exists() and len(path.read_text(encoding="utf-8").splitlines()) > 120:
            ERRORS.append(f"{name}: too long; keep the repository landing page concise")
    check_front_matter(files)
    check_links(files)
    if ERRORS:
        print(f"Repository checks failed: {len(ERRORS)} issue(s)")
        for error in ERRORS[:200]:
            print(" -", error)
        if len(ERRORS) > 200:
            print(f" ... and {len(ERRORS)-200} more")
        return 1
    print(f"Repository checks passed ({len(files)} publishable files inspected).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
