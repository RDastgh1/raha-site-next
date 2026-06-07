#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from import_publications import ROOT, ascii_norm, write_yaml


PUB_DIR = ROOT / "content" / "publication"
REPORT = ROOT / "data" / "publications" / "enrichment_report.yaml"


def read_front(path: Path) -> tuple[dict[str, str], str, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    front = parts[1]
    body = parts[2] if len(parts) > 2 else ""
    fields: dict[str, str] = {}
    for line in front.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields, front, body


def write_front(path: Path, front: str, body: str, updates: dict[str, str]) -> None:
    lines = []
    seen = set()
    for line in front.splitlines():
        if ":" in line and not line.startswith(" "):
            key = line.split(":", 1)[0].strip()
            if key in updates:
                lines.append(f'{key}: "{updates[key].replace(chr(34), chr(92)+chr(34))}"')
                seen.add(key)
                continue
        lines.append(line)
    for key, value in updates.items():
        if key not in seen:
            lines.append(f'{key}: "{value.replace(chr(34), chr(92)+chr(34))}"')
    path.write_text("---\n" + "\n".join(lines) + "\n---" + body, encoding="utf-8")


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "raha-site-next-publication-enrichment/1.0 (mailto:example@example.com)"})
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def similarity(a: str, b: str) -> float:
    at = set(ascii_norm(a).split())
    bt = set(ascii_norm(b).split())
    if not at or not bt:
        return 0
    return len(at & bt) / len(at | bt)


def crossref_lookup(title: str, year: str) -> tuple[dict[str, str], float, str]:
    query = urllib.parse.urlencode({"query.title": title, "rows": "3"})
    data = get_json(f"https://api.crossref.org/works?{query}")
    items = data.get("message", {}).get("items", [])
    if not items:
        return {}, 0, "no CrossRef candidates"
    best = None
    best_score = 0.0
    for item in items:
        candidate_title = " ".join(item.get("title") or [])
        score = similarity(title, candidate_title)
        issued = str((((item.get("issued") or {}).get("date-parts") or [[""]])[0] or [""])[0])
        if year and issued == year:
            score += 0.08
        if score > best_score:
            best = item
            best_score = score
    if not best:
        return {}, 0, "no usable CrossRef candidate"
    result = {
        "doi": best.get("DOI", ""),
        "url_doi": best.get("URL", ""),
        "abstract": re.sub("<[^>]+>", "", best.get("abstract", "") or "").strip(),
    }
    return result, min(best_score, 1.0), "CrossRef title/year match"


def main() -> None:
    successful = []
    ambiguous = []
    unresolved = []
    for index_path in sorted(PUB_DIR.glob("*/index.md")):
        fields, front, body = read_front(index_path)
        if fields.get("tier") == "report":
            continue
        title = fields.get("title", "")
        year = fields.get("year", "")
        updates: dict[str, str] = {}
        try:
            result, score, reason = crossref_lookup(title, year)
            if score >= 0.82 and result.get("doi"):
                for key in ["doi", "url_doi", "abstract"]:
                    if result.get(key) and not fields.get(key):
                        updates[key] = result[key]
                if updates:
                    write_front(index_path, front, body, updates)
                successful.append({"title": title, "slug": index_path.parent.name, "score": round(score, 3), "source": reason, "updated_fields": list(updates.keys())})
            elif score >= 0.58:
                ambiguous.append({"title": title, "slug": index_path.parent.name, "score": round(score, 3), "reason": "CrossRef match below auto-apply threshold"})
            else:
                unresolved.append({"title": title, "slug": index_path.parent.name, "reason": reason, "score": round(score, 3)})
        except Exception as exc:
            unresolved.append({"title": title, "slug": index_path.parent.name, "reason": str(exc)})
        time.sleep(0.08)
    write_yaml(REPORT, {"successful": successful, "ambiguous": ambiguous, "unresolved": unresolved})


if __name__ == "__main__":
    main()
