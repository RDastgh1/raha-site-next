#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIB = ROOT / "data" / "publications" / "publications.bib"
DEFAULT_PUBLICATIONS = ROOT / "content" / "publication"
DEFAULT_ASSET_SOURCE = ROOT.parent / "publications"
DEFAULT_STATIC_MEDIA = ROOT / "static" / "media" / "publications"
DEFAULT_ASSET_MEDIA = ROOT / "assets" / "media" / "publications"

REAL_FIGURE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
PDF_EXTS = {".pdf"}

HIGHLIGHTED_TITLES = [
    "BRACE-ing for the future: Establishing iPad-based norms for cognitive function in the MACS/WIHS Combined Cohort Study",
    "Identifying and distinguishing cognitive profiles among virally suppressed people with HIV",
    "Machine learning approaches to understand cognitive phenotypes in people with HIV",
    "MEAnalyzer-a spike train analysis tool for multi electrode arrays",
    "Blood-Brain barrier disruption in long COVID and cognitive correlates: A cross-sectional MRI study",
    "The Baltimore declaration toward the exploration of organoid intelligence",
    "Patterns and predictors of cognitive function among virally suppressed women with HIV",
    "Metabolomic levels mediate the link between socioeconomic factors and changes in declarative memory in women with and without HIV",
    "Longitudinal effects of polypharmacy on cognitive function in people with HIV",
    "Tryptophan-Kynurenine Pathway Activation and Cognition in Virally Suppressed Women With HIV",
]

PLACEHOLDER_TEXT = {
    "",
    "Add a concise, manually curated explanation of why this paper matters.",
    "Add a readable summary for collaborators, trainees, and interdisciplinary visitors.",
    "Add scientific context, interpretation, and links to related systems.",
}


@dataclass
class Entry:
    kind: str
    key: str
    block: str
    fields: dict[str, str]


def normalize_text(value: str) -> str:
    value = value.replace("{", "").replace("}", "")
    value = value.replace("\\&", "&").replace("--", "-")
    value = re.sub(r"\$\\alpha\$", "alpha", value)
    value = re.sub(r"\$\\beta\$", "beta", value)
    return re.sub(r"\s+", " ", value).strip()


def ascii_norm(value: str) -> str:
    value = normalize_text(value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "untitled-publication"


def yaml_quote(value: str) -> str:
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value}"'


def yaml_list(values: list[str], indent: int = 0) -> list[str]:
    prefix = " " * indent
    if not values:
        return [f"{prefix}[]"]
    return [f"{prefix}- {yaml_quote(v)}" for v in values]


def parse_bibtex(path: Path) -> list[Entry]:
    text = path.read_text(encoding="utf-8")
    starts = list(re.finditer(r"@([A-Za-z]+)\s*\{\s*([^,]+),", text))
    entries: list[Entry] = []

    for index, match in enumerate(starts):
        start = match.start()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[start:end].strip()
        fields: dict[str, str] = {}
        for field_match in re.finditer(r"\n\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*([{\"])", block):
            name = field_match.group(1).lower()
            opener = field_match.group(2)
            value_start = field_match.end()
            if opener == "{":
                depth = 1
                pos = value_start
                while pos < len(block) and depth:
                    if block[pos] == "{":
                        depth += 1
                    elif block[pos] == "}":
                        depth -= 1
                    pos += 1
                raw = block[value_start : pos - 1]
            else:
                pos = block.find('"', value_start)
                raw = block[value_start:pos] if pos != -1 else block[value_start:]
            fields[name] = normalize_text(raw)
        entries.append(Entry(match.group(1).lower(), match.group(2).strip(), block, fields))
    return entries


def read_existing_manual(path: Path) -> tuple[dict[str, str], str] | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    front = parts[1]
    body = parts[2].lstrip()
    fields: dict[str, str] = {}
    for line in front.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields, body


def score_asset(title_norm: str, asset_norm: str) -> tuple[float, str]:
    if not title_norm or not asset_norm:
        return 0.0, "empty"
    title_tokens = set(title_norm.split())
    asset_tokens = set(asset_norm.split())
    overlap = len(title_tokens & asset_tokens)
    union = max(len(title_tokens | asset_tokens), 1)
    jaccard = overlap / union
    if title_norm in asset_norm:
        return 0.99, "title contained in asset filename"
    if asset_norm in title_norm and len(asset_norm) > 24:
        return 0.92, "asset filename contained in title"
    if title_norm[:70] and title_norm[:70] in asset_norm:
        return 0.9, "title prefix matches asset filename"
    return jaccard, "token overlap"


def asset_candidates(entries: list[Entry], asset_source: Path) -> dict[str, dict[str, list[dict[str, str | float]]]]:
    assets = [p for p in asset_source.glob("*") if p.is_file()] if asset_source.exists() else []
    normalized_assets = [(p, ascii_norm(p.stem)) for p in assets]
    report: dict[str, dict[str, list[dict[str, str | float]]]] = {}
    for entry in entries:
        title_norm = ascii_norm(entry.fields.get("title", ""))
        pdfs: list[dict[str, str | float]] = []
        figures: list[dict[str, str | float]] = []
        for asset, asset_norm in normalized_assets:
            score, reason = score_asset(title_norm, asset_norm)
            if score < 0.34:
                continue
            item = {
                "file": str(asset),
                "score": round(score, 3),
                "reason": reason,
                "auto_assign": score >= 0.86,
            }
            if asset.suffix.lower() in PDF_EXTS:
                pdfs.append(item)
            elif asset.suffix.lower() in REAL_FIGURE_EXTS:
                figures.append(item)
        pdfs.sort(key=lambda x: float(x["score"]), reverse=True)
        figures.sort(key=lambda x: float(x["score"]), reverse=True)
        report[entry.key] = {"pdf_candidates": pdfs[:5], "figure_candidates": figures[:5]}
    return report


def infer_relationships(entry: Entry) -> dict[str, list[str]]:
    title = ascii_norm(entry.fields.get("title", ""))
    relationships = {
        "software": [],
        "research": [],
        "talks": [],
        "datasets": [],
        "community": [],
    }
    if "meanalyzer" in title or "multi electrode" in title or "multielectrode" in title:
        relationships["software"].append("meanalyzer")
        relationships["research"].append("software-systems")
    if any(term in title for term in ["machine learning", "phenotype", "phenotypes", "profiles", "cognitive trajectory"]):
        relationships["research"].append("computational-phenotyping")
        relationships["software"].append("computational-phenotyping-pipelines")
        relationships["talks"].append("biomedical-data-science-brain-health")
    if any(term in title for term in ["biomarker", "plasma", "proteomic", "metabolic", "neurofilament", "glial"]):
        relationships["research"].append("biomarker-systems")
        relationships["software"].append("biomarker-analytics-systems")
    if any(term in title for term in ["harmonization", "ipad", "brace"]):
        relationships["research"].append("reproducible-infrastructure")
        relationships["software"].append("dashboards-reporting-frameworks")
    if any(term in title for term in ["hiv", "neurocognitive", "cognitive"]):
        relationships["research"].append("translational-neuroinformatics")
    for key in relationships:
        relationships[key] = sorted(set(relationships[key]))
    return relationships



def title_matches_highlighted(title: str, highlighted_title: str) -> bool:
    left = ascii_norm(title).replace(" preprint", "")
    right = ascii_norm(highlighted_title)
    return left == right or left.startswith(right) or right in left


def highlighted_order(entries: list[Entry]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for position, highlighted_title in enumerate(HIGHLIGHTED_TITLES, start=1):
        matches = [e for e in entries if title_matches_highlighted(e.fields.get("title", ""), highlighted_title)]
        if matches:
            entry = matches[0]
            items.append({"title": highlighted_title, "key": entry.key, "order": str(position)})
        else:
            items.append({"title": highlighted_title, "key": "", "order": str(position), "status": "unresolved"})
    return items


def generated_annotation(entry: Entry, relationships: dict[str, list[str]]) -> dict[str, str | list[str]]:
    title = entry.fields.get("title", "This publication")
    year = entry.fields.get("year", "")
    venue = venue_for(entry)
    lower = ascii_norm(title)
    area = "translational brain health research"
    if "meanalyzer" in lower or "electrode" in lower:
        area = "scientific software for electrophysiology analysis"
    elif "phenotype" in lower or "profile" in lower or "machine learning" in lower:
        area = "computational phenotyping and cognitive subgroup discovery"
    elif "blood brain barrier" in lower or "long covid" in lower:
        area = "translational analysis of Long COVID and cognitive outcomes"
    elif "baltimore declaration" in lower or "organoid" in lower:
        area = "community standards and scientific infrastructure for organoid intelligence"
    elif "metabolomic" in lower or "tryptophan" in lower or "kynurenine" in lower:
        area = "biomarker systems and cognitive health"
    elif "polypharmacy" in lower:
        area = "longitudinal cognitive risk modeling"
    context = f"Published in {venue}" if venue else "This publication"
    if year:
        context += f" in {year}"
    return {
        "plain_language_summary": f"{context} contributes to {area}. It is included here as part of a connected research program linking data, methods, and reusable scientific infrastructure.",
        "why_this_matters": f"This paper helps define a research thread in {area}, providing context for how computational and translational evidence can be organized into reusable scientific systems.",
        "research_significance": f"The work supports the broader program of connecting heterogeneous biomedical data with interpretable analysis, reproducible workflows, and research outputs that collaborators can inspect and extend.",
        "research_story": f"Within the site ecosystem, this paper connects to {', '.join(relationships.get('research') or ['the research architecture'])} and helps show how individual studies accumulate into a systems-level research agenda.",
        "key_findings": [
            "Summarize the primary empirical or methodological finding after manual review.",
            "Identify the cohort, system, or data modality most central to the paper.",
            "Connect the finding to related software, research areas, datasets, or talks where relevant.",
        ],
    }


def preserve_or_generate(existing_fields: dict[str, str], key: str, generated: str) -> str:
    current = existing_fields.get(key, "").strip().strip('"')
    if current and current not in PLACEHOLDER_TEXT:
        return current
    return generated

def tier_for(entry: Entry, highlighted_titles: set[str], selected: set[str]) -> str:
    if any(title_matches_highlighted(entry.fields.get("title", ""), t) for t in highlighted_titles):
        return "highlighted"
    if entry.key in selected:
        return "selected"
    return "archive"


def venue_for(entry: Entry) -> str:
    return entry.fields.get("journal") or entry.fields.get("booktitle") or entry.fields.get("publisher") or entry.fields.get("organization") or ""


def authors_for(entry: Entry) -> list[str]:
    authors = entry.fields.get("author", "")
    if not authors:
        return []
    return [normalize_text(a) for a in re.split(r"\s+and\s+", authors)]


def copy_auto_asset(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(src, dest)
    return dest.name


def write_placeholder(slug: str, title: str) -> str:
    static_path = DEFAULT_STATIC_MEDIA / "generated" / f"{slug}.svg"
    asset_path = DEFAULT_ASSET_MEDIA / "generated" / f"{slug}.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img" aria-label="{title}">
  <defs>
    <radialGradient id="g1" cx="35%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#62d8ef" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#07111d" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="g2" cx="68%" cy="52%" r="45%">
      <stop offset="0%" stop-color="#9c77d8" stop-opacity="0.46"/>
      <stop offset="100%" stop-color="#07111d" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur"><feGaussianBlur stdDeviation="0.7"/></filter>
  </defs>
  <rect width="1200" height="675" fill="#06101c"/>
  <rect width="1200" height="675" fill="url(#g1)"/>
  <rect width="1200" height="675" fill="url(#g2)"/>
  <g fill="none" stroke="#62d8ef" stroke-opacity="0.22">
    <path d="M80 420 C260 250 410 530 590 340 S900 220 1130 330"/>
    <path d="M40 500 C290 390 380 210 610 285 S880 500 1160 190"/>
    <path d="M140 225 C390 120 530 420 790 270 S990 170 1180 240"/>
  </g>
  <g filter="url(#blur)">
    <circle cx="315" cy="370" r="4" fill="#62d8ef"/>
    <circle cx="350" cy="335" r="3" fill="#62d8ef"/>
    <circle cx="390" cy="390" r="2.5" fill="#eef7fb"/>
    <circle cx="735" cy="280" r="4" fill="#9c77d8"/>
    <circle cx="790" cy="310" r="3" fill="#62d8ef"/>
    <circle cx="830" cy="255" r="2.5" fill="#eef7fb"/>
    <circle cx="620" cy="450" r="3.5" fill="#62d8ef"/>
  </g>
  <text x="64" y="595" fill="#eef7fb" opacity="0.74" font-family="Arial, sans-serif" font-size="28" letter-spacing="4">PUBLICATION PORTAL</text>
</svg>
"""
    for path in [static_path, asset_path]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg, encoding="utf-8")
    return f"media/publications/generated/{slug}.svg"


def initial_selected(entries: list[Entry], highlighted: set[str]) -> list[str]:
    keys = []
    for entry in entries:
        title = ascii_norm(entry.fields.get("title", ""))
        if entry.key in highlighted:
            continue
        if any(term in title for term in [
            "patterns and predictors",
            "biopsychosocial phenotypes",
            "development of a refined harmonization",
            "international application",
            "plasma neurofilament",
            "blood brain barrier",
            "cognitive predictors",
            "mental health phenotypes",
        ]):
            keys.append(entry.key)
    return sorted(set(keys), key=keys.index)


def write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def emit(value: object, indent: int = 0) -> list[str]:
        pad = " " * indent
        if isinstance(value, dict):
            lines: list[str] = []
            for key, child in value.items():
                if isinstance(child, (dict, list)):
                    lines.append(f"{pad}{key}:")
                    lines.extend(emit(child, indent + 2))
                else:
                    lines.append(f"{pad}{key}: {scalar(child)}")
            return lines
        if isinstance(value, list):
            if not value:
                return [f"{pad}[]"]
            lines = []
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{pad}-")
                    lines.extend(emit(item, indent + 2))
                else:
                    lines.append(f"{pad}- {scalar(item)}")
            return lines
        return [f"{pad}{scalar(value)}"]

    def scalar(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if value is None:
            return '""'
        return yaml_quote(str(value))

    path.write_text("\n".join(emit(data)) + "\n", encoding="utf-8")


def generate(args: argparse.Namespace) -> None:
    entries = parse_bibtex(args.bib)
    asset_report = asset_candidates(entries, args.asset_source)
    highlighted_items = highlighted_order(entries)
    highlighted_titles = set(HIGHLIGHTED_TITLES)
    highlighted_keys = {item["key"] for item in highlighted_items if item.get("key")}
    selected = initial_selected(entries, highlighted_keys)
    used_slugs: Counter[str] = Counter()
    duplicate_titles: dict[str, list[str]] = defaultdict(list)
    ecosystem: dict[str, dict[str, list[str]]] = {}
    imported: list[dict[str, object]] = []
    missing_doi: list[str] = []
    missing_pdf: list[str] = []
    missing_figures: list[str] = []
    missing_visual_abstracts: list[str] = []
    missing_year: list[str] = []
    metadata_warnings: list[dict[str, str]] = []

    args.out_dir.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        title = entry.fields.get("title", "Untitled publication")
        year = entry.fields.get("year", "")
        base_slug = slugify(f"{year}-{title}" if year else title)
        used_slugs[base_slug] += 1
        slug = base_slug if used_slugs[base_slug] == 1 else f"{base_slug}-{used_slugs[base_slug]}"
        bundle = args.out_dir / slug
        index_path = bundle / "index.md"
        cite_path = bundle / "cite.bib"
        bundle.mkdir(parents=True, exist_ok=True)

        duplicate_titles[ascii_norm(title)].append(entry.key)
        relationships = infer_relationships(entry)
        ecosystem[entry.key] = relationships

        candidates = asset_report.get(entry.key, {})
        pdf_candidates = candidates.get("pdf_candidates", [])
        figure_candidates = candidates.get("figure_candidates", [])
        pdf = ""
        thumbnail = ""
        figure = ""
        if pdf_candidates and pdf_candidates[0]["auto_assign"]:
            pdf_src = Path(str(pdf_candidates[0]["file"]))
            pdf = copy_auto_asset(pdf_src, bundle / pdf_src.name)
        else:
            missing_pdf.append(entry.key)
        if figure_candidates and figure_candidates[0]["auto_assign"]:
            fig_src = Path(str(figure_candidates[0]["file"]))
            figure = copy_auto_asset(fig_src, bundle / fig_src.name)
            thumbnail = figure
        else:
            missing_figures.append(entry.key)
            thumbnail = write_placeholder(slug, title)

        if not entry.fields.get("doi"):
            missing_doi.append(entry.key)
        if not year:
            missing_year.append(entry.key)
        if not figure:
            missing_visual_abstracts.append(entry.key)

        if not entry.fields.get("title"):
            metadata_warnings.append({"key": entry.key, "warning": "missing title"})
        if not entry.fields.get("author"):
            metadata_warnings.append({"key": entry.key, "warning": "missing author"})

        existing = read_existing_manual(index_path)
        existing_fields, existing_body = existing if existing else ({}, "")
        tier = tier_for(entry, highlighted_titles, set(selected))
        authors = authors_for(entry)
        generated = generated_annotation(entry, relationships)
        pub_date = f"{year}-01-01" if year else "1900-01-01"

        front: list[str] = [
            "---",
            f'bibtex_key: {yaml_quote(entry.key)}',
            f"slug: {yaml_quote(slug)}",
            f"title: {yaml_quote(title)}",
            f"date: {pub_date}",
            f"year: {yaml_quote(year)}",
            f"publication_type: {yaml_quote(entry.kind)}",
            f"publication: {yaml_quote(venue_for(entry))}",
            "authors:",
            *yaml_list(authors, 2),
            f"doi: {yaml_quote(existing_fields.get('doi', '').strip('\"') or entry.fields.get('doi', ''))}",
            f"pubmed: {yaml_quote(existing_fields.get('pubmed', '').strip('\"') or entry.fields.get('pmid') or entry.fields.get('pubmed') or '')}",
            f"url_pdf: {yaml_quote(existing_fields.get('url_pdf', '').strip('\"') or pdf)}",
            f"url_code: {yaml_quote(existing_fields.get('url_code', '').strip('\"') or entry.fields.get('url_code', ''))}",
            f"url_dataset: {yaml_quote(existing_fields.get('url_dataset', '').strip('\"') or entry.fields.get('url_dataset', ''))}",
            f"url_doi: {yaml_quote(existing_fields.get('url_doi', '').strip('\"') or entry.fields.get('url', ''))}",
            f"tier: {yaml_quote(tier)}",
            f"featured: {'true' if tier == 'highlighted' else 'false'}",
            f"thumbnail: {yaml_quote(existing_fields.get('thumbnail', '').strip('\"') or thumbnail)}",
            f"visual_abstract: {yaml_quote(existing_fields.get('visual_abstract', '').strip('\"') if existing_fields.get('visual_abstract') else '')}",
            f"abstract: {yaml_quote(existing_fields.get('abstract', '').strip('\"') if existing_fields.get('abstract') else '')}",
            f"extracted_figure: {yaml_quote(existing_fields.get('extracted_figure', '').strip('\"') if existing_fields.get('extracted_figure') else '')}",
            f"extracted_figure_source_pdf: {yaml_quote(existing_fields.get('extracted_figure_source_pdf', '').strip('\"') if existing_fields.get('extracted_figure_source_pdf') else '')}",
            f"extracted_figure_page: {yaml_quote(existing_fields.get('extracted_figure_page', '').strip('\"') if existing_fields.get('extracted_figure_page') else '')}",
            f"extracted_figure_confidence: {yaml_quote(existing_fields.get('extracted_figure_confidence', '').strip('\"') if existing_fields.get('extracted_figure_confidence') else '')}",
            f"plain_language_summary: {yaml_quote(preserve_or_generate(existing_fields, 'plain_language_summary', str(generated['plain_language_summary'])))}",
            f"why_this_matters: {yaml_quote(preserve_or_generate(existing_fields, 'why_this_matters', str(generated['why_this_matters'])))}",
            f"research_significance: {yaml_quote(preserve_or_generate(existing_fields, 'research_significance', str(generated['research_significance'])))}",
            f"research_story: {yaml_quote(preserve_or_generate(existing_fields, 'research_story', str(generated['research_story'])))}",
            "key_findings:",
            *yaml_list(generated['key_findings'], 2),
            "related_software:",
            *yaml_list(relationships["software"], 2),
            "related_research:",
            *yaml_list(relationships["research"], 2),
            "related_talks:",
            *yaml_list(relationships["talks"], 2),
            "related_datasets:",
            *yaml_list(relationships["datasets"], 2),
            "related_community:",
            *yaml_list(relationships["community"], 2),
            "tags:",
            *yaml_list(relationships["research"] or [entry.kind], 2),
            "---",
            "",
        ]

        if existing_body:
            body = existing_body
        else:
            body = "\n".join([
                "## Why this paper matters",
                "",
                str(generated["why_this_matters"]),
                "",
                "## Key findings",
                "",
                *[f"- {item}" for item in generated["key_findings"]],
                "",
                "## Research significance",
                "",
                str(generated["research_significance"]),
                "",
                "## Research story",
                "",
                str(generated["research_story"]),
                "",
                "## Plain-language summary",
                "",
                str(generated["plain_language_summary"]),
                "",
                "## Commentary",
                "",
                "Add manual scientific context, interpretation, and links to related systems.",
                "",
                "## Figures and visual abstracts",
                "",
                "Add publication figures, visual abstracts, and explanatory graphics to this bundle.",
                "",
            ])

        index_path.write_text("\n".join(front) + body, encoding="utf-8")
        cite_path.write_text(entry.block + "\n", encoding="utf-8")
        imported.append({
            "key": entry.key,
            "slug": slug,
            "title": title,
            "year": year,
            "tier": tier,
            "pdf_assigned": bool(pdf),
            "figure_assigned": bool(figure),
            "thumbnail": thumbnail,
        })

    duplicate_groups = [
        {"normalized_title": key, "keys": keys}
        for key, keys in duplicate_titles.items()
        if key and len(keys) > 1
    ]

    write_yaml(ROOT / "data" / "highlighted_publications.yaml", {
        "items": [
            {"title": item["title"], "key": item.get("key", ""), "order": item["order"], "note": "Title-driven highlighted publication set"}
            for item in highlighted_items
        ]
    })
    write_yaml(ROOT / "data" / "selected_publications.yaml", {
        "items": [{"key": key, "note": "Initial selected publication set"} for key in selected]
    })
    write_yaml(ROOT / "data" / "research_ecosystem.yaml", {"publications": ecosystem})
    write_yaml(ROOT / "data" / "publications" / "asset_matching_report.yaml", {
        "source_asset_folder": str(args.asset_source),
        "assignment_policy": "Only candidates with score >= 0.86 are auto-assigned; ambiguous candidates are report-only.",
        "entries": asset_report,
    })
    write_yaml(ROOT / "data" / "publications" / "ingestion_report.yaml", {
        "source_bib": str(args.bib),
        "total_entries": len(entries),
        "type_counts": dict(Counter(e.kind for e in entries)),
        "imported": imported,
        "duplicates_detected": duplicate_groups,
        "missing_doi": missing_doi,
        "missing_pdfs": missing_pdf,
        "missing_figures": missing_figures,
        "missing_visual_abstracts": missing_visual_abstracts,
        "missing_year": missing_year,
        "metadata_warnings": metadata_warnings,
    })

    report_page = ROOT / "content" / "publication" / "ingestion-report" / "index.md"
    report_page.parent.mkdir(parents=True, exist_ok=True)
    report_page.write_text(
        "---\n"
        "title: \"Publication Ingestion Report\"\n"
        "summary: \"Report generated from the canonical BibTeX import.\"\n"
        "tier: \"report\"\n"
        "---\n\n"
        "This page summarizes the current publication import. The machine-readable report lives in "
        "`data/publications/ingestion_report.yaml`, and proposed asset matches live in "
        "`data/publications/asset_matching_report.yaml`.\n\n"
        f"- Total BibTeX entries: {len(entries)}\n"
        f"- Duplicate title groups: {len(duplicate_groups)}\n"
        f"- Missing DOI fields: {len(missing_doi)}\n"
        f"- Missing or unassigned PDFs: {len(missing_pdf)}\n"
        f"- Missing or unassigned figures: {len(missing_figures)}\n"
        f"- Missing visual abstracts: {len(missing_visual_abstracts)}\n"
        f"- Missing years: {len(missing_year)}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import BibTeX publications into Hugo page bundles.")
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_PUBLICATIONS)
    parser.add_argument("--asset-source", type=Path, default=DEFAULT_ASSET_SOURCE)
    generate(parser.parse_args())


if __name__ == "__main__":
    main()
