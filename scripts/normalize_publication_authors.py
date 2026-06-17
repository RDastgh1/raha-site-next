#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUB_DIR = ROOT / "content" / "publication"


def read_page(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


def front_value(front: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*\"?(.+?)\"?\s*$", front)
    return match.group(1).strip().strip('"') if match else ""


def front_authors(front: str) -> list[str]:
    match = re.search(r"(?m)^authors:\n((?:^  - [^\n]+\n?)+)", front)
    if not match:
        return []
    authors = []
    for line in match.group(1).splitlines():
        item = re.sub(r"^\s*-\s*", "", line).strip().strip('"')
        if item:
            authors.append(item)
    return authors


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def replace_authors(front: str, authors: list[str]) -> str:
    block = "authors:\n" + "\n".join(f"  - {yaml_quote(author)}" for author in authors)
    if re.search(r"(?m)^authors:\n(?:^  - [^\n]+\n?)+", front):
        return re.sub(r"(?m)^authors:\n(?:^  - [^\n]+\n?)+", block + "\n", front)
    lines = front.splitlines()
    insert_at = 0
    for index, line in enumerate(lines):
        if line.startswith("publication:"):
            insert_at = index + 1
            break
    lines.insert(insert_at, block)
    return "\n".join(lines) + "\n"


def punctuate_initials(name: str) -> str:
    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        return ".".join(token) + "."

    name = re.sub(r"\b[A-Z]{1,3}\b(?!\.)", repl, name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def display_name(raw: str) -> str:
    raw = raw.strip()
    if raw.lower() == "others":
        return raw
    if "," in raw:
        family, given = [part.strip() for part in raw.split(",", 1)]
        return punctuate_initials(f"{given} {family}")
    return punctuate_initials(raw)


def crossref_authors(doi: str) -> list[str]:
    encoded = urllib.parse.quote(doi)
    request = urllib.request.Request(
        f"https://api.crossref.org/works/{encoded}",
        headers={"User-Agent": "raha-site-next-author-normalizer/1.0 (mailto:example@example.com)"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    authors = []
    for author in data.get("message", {}).get("author", []):
        given = author.get("given", "").strip()
        family = author.get("family", "").strip()
        literal = author.get("name", "").strip()
        if family and given:
            authors.append(punctuate_initials(f"{given} {family}"))
        elif family:
            authors.append(punctuate_initials(family))
        elif literal:
            authors.append(punctuate_initials(literal))
    return authors


def main() -> None:
    updated = []
    unresolved = []
    for path in sorted(PUB_DIR.glob("*/index.md")):
        front, body = read_page(path)
        if not front:
            continue
        current = front_authors(front)
        if not current:
            continue

        authors = [display_name(author) for author in current]
        had_others = any(author.lower() == "others" for author in current)
        doi = front_value(front, "doi")

        if had_others and doi:
            try:
                fetched = crossref_authors(doi)
                if fetched and len(fetched) >= len([a for a in authors if a.lower() != "others"]):
                    authors = fetched
                else:
                    unresolved.append(f"{path.parent.name}: CrossRef returned too few authors")
            except Exception as exc:
                unresolved.append(f"{path.parent.name}: {exc}")
            time.sleep(0.1)
        elif had_others:
            unresolved.append(f"{path.parent.name}: no DOI")

        if authors != current:
            path.write_text("---\n" + replace_authors(front, authors) + "---" + body, encoding="utf-8")
            updated.append(path.parent.name)

    print(f"Updated {len(updated)} publication author lists")
    if unresolved:
        print("Unresolved placeholders:")
        for item in unresolved:
            print(f"- {item}")


if __name__ == "__main__":
    main()
