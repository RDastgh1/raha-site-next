#!/usr/bin/env python3

from __future__ import annotations

import shutil
import unicodedata
from pathlib import Path

from import_publications import ROOT, write_yaml


PUB_DIR = ROOT / "content" / "publication"
ASSET_SOURCE = ROOT.parent / "publications"
REPORT = ROOT / "data" / "publications" / "figure_extraction_report.yaml"

REAL_FIGURE_BY_DOI = {
    "10.1007/s12021-019-09431-0": "12021_2019_9431_Fig2_HTML.png",
    "10.3389/fneur.2020.551921": "fneur-11-551921-g0001.webp",
    "10.3389/fneur.2021.604984": "fneur-12-604984-g0001.webp",
    "10.1007/s13365-024-01195-x": "13365_2024_1195_Fig1_HTML.png",
    "10.1007/s13365-025-01290-7": "13365_2025_1290_Fig2_HTML.png",
    "10.1007/s11481-021-10042-3": "11481_2021_10042_Figa_HTML.webp",
    "10.1186/s12883-025-04249-7": "12883_2025_4249_Fig1_HTML.png",
    "10.1007/s11606-025-10042-6": "nihpp-rs6136690v1-f0001.jpg",
    "10.1109/nebec.2015.7117155": "7117155-fig-3-source-small.gif",
    "10.1038/s41419-018-0369-4": "41419_2018_369_Fig8_HTML.jpg",
    "10.1093/ajcn/nqab038": "1-s2.0-S0002916522003380-gr1.jpg",
    "10.1093/infdis/jiae460": "ArticleViewerPreview@2.00126334-202408150-00011.F1.jpeg",
}

REAL_FIGURE_BY_TITLE = {
    "dietary intake is associated with neuropsychological impairment in women with hiv": "1-s2.0-S0002916522003380-gr1.jpg",
    "tnfalpha and il 1beta modify the mirna cargo of astrocyte shed extracellular vesicles to regulate neurotrophic signaling in neurons": "41419_2018_369_Fig8_HTML.jpg",
}

VISUALLY_ACCEPTED_PDF_CROPS = {
    "2012-interactions-of-fluorescein-isothiocyanate-labeled-poloxamer-p188-with-cultured-cells",
    "2019-lipidomic-characterization-of-extracellular-vesicles-in-human-serum",
    "2019-role-of-human-induced-pluripotent-stem-cell-derived-spinal-cord-astrocytes-in-the-functional-maturation-of-motor-neurons-in-a-multielectrode-array-system",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


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


def copy_real_figure(fields: dict[str, str], bundle: Path) -> tuple[str, str] | None:
    doi = fields.get("doi", "").lower()
    title_key = normalize(fields.get("title", ""))
    source_name = REAL_FIGURE_BY_DOI.get(doi) or REAL_FIGURE_BY_TITLE.get(title_key)
    if not source_name:
        return None
    source = ASSET_SOURCE / source_name
    if not source.exists():
        return None
    target = bundle / f"paper-figure-thumbnail{source.suffix.lower()}"
    shutil.copy2(source, target)
    return target.name, source.name


def reject_text_heavy_crop(index_path: Path, fields: dict[str, str], front: str, body: str, title: str) -> None:
    current_thumb = fields.get("thumbnail", "")
    current_path = index_path.parent / current_thumb
    if current_thumb.startswith("paper-figure-thumbnail") and current_path.exists():
        current_path.unlink()
    fallback = "extracted-figure-page-1.png" if (index_path.parent / "extracted-figure-page-1.png").exists() else fields.get("thumbnail", "")
    write_front(index_path, front, body, {
        "thumbnail": fallback,
        "thumbnail_alt": f"Publication preview for {title}" if title else "Publication preview",
        "extracted_figure": "",
        "extracted_figure_source_pdf": "",
        "extracted_figure_page": "",
        "extracted_figure_confidence": "",
    })


def main() -> None:
    entries = []
    for index_path in sorted(PUB_DIR.glob("*/index.md")):
        fields, front, body = read_front(index_path)
        if fields.get("tier") == "report":
            continue
        slug = index_path.parent.name
        title = fields.get("title", "")
        alt = f"Figure from {title}" if title else "Figure from publication"

        copied = copy_real_figure(fields, index_path.parent)
        if copied:
            thumbnail, source = copied
            write_front(index_path, front, body, {
                "thumbnail": thumbnail,
                "thumbnail_alt": alt,
                "extracted_figure": thumbnail,
                "extracted_figure_source_pdf": source,
                "extracted_figure_page": "",
                "extracted_figure_confidence": "0.95",
            })
            entries.append({
                "title": title,
                "slug": slug,
                "status": "existing_figure_used",
                "extracted_figure": thumbnail,
                "source_asset": source,
                "confidence": 0.95,
                "thumbnail_updated": True,
            })
            continue

        current_thumb = fields.get("thumbnail", "")
        current_path = index_path.parent / current_thumb
        if current_thumb.startswith("paper-figure-thumbnail") and current_path.exists():
            if slug not in VISUALLY_ACCEPTED_PDF_CROPS:
                reject_text_heavy_crop(index_path, fields, front, body, title)
                entries.append({
                    "title": title,
                    "slug": slug,
                    "status": "manual_needed",
                    "reason": "automated PDF crop was text-heavy; retained the previous publication preview pending manual figure selection",
                    "confidence": 0,
                })
                continue
            entries.append({
                "title": title,
                "slug": slug,
                "status": "retained_existing_crop",
                "extracted_figure": current_thumb,
                "confidence": fields.get("extracted_figure_confidence", ""),
                "thumbnail_updated": False,
            })
            continue

        pdf = fields.get("url_pdf", "")
        if not pdf:
            entries.append({"title": title, "slug": slug, "status": "manual_needed", "reason": "no associated PDF or matched figure asset", "confidence": 0})
            continue
        pdf_path = index_path.parent / pdf
        if not pdf_path.exists():
            entries.append({"title": title, "slug": slug, "status": "manual_needed", "source_pdf": str(pdf_path), "reason": "PDF path missing", "confidence": 0})
            continue

        entries.append({"title": title, "slug": slug, "status": "manual_needed", "source_pdf": pdf, "reason": "no pre-existing publisher figure and automated PDF crop was not visually accepted", "confidence": 0})
        continue

    write_yaml(REPORT, {
        "method": "Existing publisher/paper figure assets were preferred by DOI/title. Three visually useful PDF-derived crops from the local bundles were retained after contact-sheet QA. Text-heavy automated crops were rejected and those papers were left on their prior publication preview pending manual figure selection.",
        "entries": entries,
    })


if __name__ == "__main__":
    main()
