#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from pathlib import Path

from import_publications import ROOT, write_yaml


PUB_DIR = ROOT / "content" / "publication"
REPORT = ROOT / "data" / "publications" / "figure_extraction_report.yaml"


def read_front(path: Path) -> tuple[dict[str, str], str, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    front = parts[1]
    body = parts[2] if len(parts) > 2 else ""
    fields = {}
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
                lines.append(f'{key}: "{updates[key]}"')
                seen.add(key)
                continue
        lines.append(line)
    for key, value in updates.items():
        if key not in seen:
            lines.append(f'{key}: "{value}"')
    path.write_text("---\n" + "\n".join(lines) + "\n---" + body, encoding="utf-8")


def main() -> None:
    entries = []
    for index_path in sorted(PUB_DIR.glob("*/index.md")):
        fields, front, body = read_front(index_path)
        if fields.get("tier") == "report":
            continue
        pdf = fields.get("url_pdf", "")
        slug = index_path.parent.name
        if not pdf:
            entries.append({"title": fields.get("title", ""), "slug": slug, "status": "placeholder_used", "reason": "no associated PDF", "confidence": 0})
            continue
        pdf_path = index_path.parent / pdf
        if not pdf_path.exists():
            entries.append({"title": fields.get("title", ""), "slug": slug, "status": "placeholder_used", "source_pdf": str(pdf_path), "reason": "PDF path missing", "confidence": 0})
            continue
        out_name = "extracted-figure-page-1.png"
        out_path = index_path.parent / out_name
        try:
            subprocess.run(["sips", "-s", "format", "png", str(pdf_path), "--out", str(out_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if out_path.exists() and out_path.stat().st_size > 0:
                write_front(index_path, front, body, {"thumbnail": out_name, "extracted_figure": out_name, "extracted_figure_source_pdf": pdf, "extracted_figure_page": "1", "extracted_figure_confidence": "0.62"})
                entries.append({"title": fields.get("title", ""), "slug": slug, "status": "figure_extracted", "extracted_figure": out_name, "source_pdf": pdf, "page_number": 1, "confidence": 0.62, "thumbnail_updated": True})
            else:
                entries.append({"title": fields.get("title", ""), "slug": slug, "status": "placeholder_used", "source_pdf": pdf, "reason": "sips produced no output", "confidence": 0})
        except Exception as exc:
            entries.append({"title": fields.get("title", ""), "slug": slug, "status": "placeholder_used", "source_pdf": pdf, "reason": str(exc), "confidence": 0})
    write_yaml(REPORT, {"method": "Rendered page 1 from associated PDFs with sips; confidence is moderate because this is page-level extraction rather than semantic graphical-abstract detection.", "entries": entries})


if __name__ == "__main__":
    main()
