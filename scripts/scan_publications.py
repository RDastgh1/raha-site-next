#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from import_publications import ROOT, ascii_norm, slugify, write_placeholder, write_yaml


PUB_DIR = ROOT / "content" / "publication"
REPORT = ROOT / "data" / "publications" / "publication_scan_report.yaml"
USER_AGENT = "raha-site-next-publication-scan/1.0 (mailto:example@example.com)"


AUTHOR_QUERIES = [
    "Raha Dastgheyb",
    "Raha M Dastgheyb",
    "Raha M. Dastgheyb",
    "Dastgheyb R",
    "Dastgheyb RM",
]


@dataclass
class Candidate:
    source: str
    title: str
    year: str
    publication: str
    publication_type: str
    authors: list[str]
    doi: str = ""
    pubmed: str = ""
    url: str = ""


def get_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise
            time.sleep(2.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def get_json(url: str) -> dict:
    return json.loads(get_text(url))


def normalize_name(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" .", ".")
    value = re.sub(r"\b([A-Z])\b(?!\.)", r"\1.", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def has_raha_author(authors: list[str]) -> bool:
    normalized = [ascii_norm(author) for author in authors]
    return any(
        "dastgheyb" in author and (
            "raha" in author
            or re.search(r"\br\b", author)
            or "rm" in author
        )
        for author in normalized
    )


def existing_records() -> tuple[set[str], set[str], set[str]]:
    dois: set[str] = set()
    titles: set[str] = set()
    slugs: set[str] = set()
    for path in PUB_DIR.glob("*/index.md"):
        slugs.add(path.parent.name)
        text = path.read_text(encoding="utf-8")
        doi_match = re.search(r'(?m)^doi:\s*"([^"]+)"', text)
        title_match = re.search(r'(?m)^title:\s*"([^"]+)"', text)
        if doi_match and doi_match.group(1):
            dois.add(doi_match.group(1).lower())
        if title_match:
            titles.add(ascii_norm(title_match.group(1)))
    return dois, titles, slugs


def pubmed_candidates() -> list[Candidate]:
    ids: set[str] = set()
    for query in AUTHOR_QUERIES:
        term = f'("{query}"[Author] OR "{query}"[All Fields])'
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
            {"db": "pubmed", "term": term, "retmode": "json", "retmax": 100}
        )
        data = get_json(url)
        ids.update(data.get("esearchresult", {}).get("idlist", []))
        time.sleep(0.45)
    if not ids:
        return []

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(sorted(ids)), "retmode": "xml"}
    )
    root = ET.fromstring(get_text(url))
    candidates: list[Candidate] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID") or ""
        title_node = article.find(".//ArticleTitle")
        title = "".join(title_node.itertext()).strip() if title_node is not None else ""
        journal = article.findtext(".//Journal/Title") or article.findtext(".//ISOAbbreviation") or ""
        year = (
            article.findtext(".//JournalIssue/PubDate/Year")
            or article.findtext(".//ArticleDate/Year")
            or ""
        )
        doi = ""
        for aid in article.findall(".//ArticleIdList/ArticleId"):
            if (aid.attrib.get("IdType") or "").lower() == "doi":
                doi = (aid.text or "").strip()
                break
        authors = []
        for author in article.findall(".//AuthorList/Author"):
            given = author.findtext("ForeName") or author.findtext("Initials") or ""
            family = author.findtext("LastName") or ""
            collective = author.findtext("CollectiveName") or ""
            name = normalize_name(f"{given} {family}".strip() or collective)
            if name:
                authors.append(name)
        if title and has_raha_author(authors):
            candidates.append(
                Candidate(
                    source="PubMed",
                    title=title,
                    year=year,
                    publication=journal,
                    publication_type="article",
                    authors=authors,
                    doi=doi,
                    pubmed=pmid,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                )
            )
    return candidates


def crossref_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[str] = set()
    for query in AUTHOR_QUERIES[:3]:
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
            {"query.author": query, "rows": 25, "sort": "published", "order": "desc"}
        )
        data = get_json(url)
        for item in data.get("message", {}).get("items", []):
            doi = (item.get("DOI") or "").strip().lower()
            title = " ".join(item.get("title") or []).strip()
            if not title or (doi and doi in seen):
                continue
            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                literal = author.get("name", "")
                name = normalize_name(f"{given} {family}".strip() or literal)
                if name:
                    authors.append(name)
            if not has_raha_author(authors):
                continue
            issued = (((item.get("issued") or {}).get("date-parts") or [[""]])[0] or [""])[0]
            item_type = item.get("type", "")
            publication_type = "inproceedings" if "proceedings" in item_type else "article"
            venue = " ".join(item.get("container-title") or []).strip()
            candidates.append(
                Candidate(
                    source="CrossRef",
                    title=title,
                    year=str(issued) if issued else "",
                    publication=venue,
                    publication_type=publication_type,
                    authors=authors,
                    doi=doi,
                    url=item.get("URL", ""),
                )
            )
            if doi:
                seen.add(doi)
        time.sleep(0.2)
    return candidates


def candidate_key(candidate: Candidate) -> str:
    return candidate.doi.lower() or ascii_norm(candidate.title)


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    by_key: dict[str, Candidate] = {}
    source_rank = {"PubMed": 2, "CrossRef": 1}
    for candidate in candidates:
        key = candidate_key(candidate)
        current = by_key.get(key)
        if not current or source_rank.get(candidate.source, 0) > source_rank.get(current.source, 0):
            by_key[key] = candidate
    return list(by_key.values())


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_publication(candidate: Candidate, slug: str) -> None:
    path = PUB_DIR / slug
    path.mkdir(parents=True, exist_ok=False)
    thumbnail = write_placeholder(slug, candidate.title)
    lines = [
        "---",
        f'bibtex_key: {yaml_quote(slug.replace("-", "_"))}',
        f'slug: {yaml_quote(slug)}',
        f'title: {yaml_quote(candidate.title)}',
        f"date: {candidate.year or '1900'}-01-01",
        f'year: {yaml_quote(candidate.year)}',
        f'publication_type: {yaml_quote(candidate.publication_type)}',
        f'publication: {yaml_quote(candidate.publication)}',
        "authors:",
    ]
    lines.extend([f"  - {yaml_quote(author)}" for author in candidate.authors])
    lines.extend(
        [
            f'doi: {yaml_quote(candidate.doi)}',
            f'pubmed: {yaml_quote(candidate.pubmed)}',
            'url_pdf: ""',
            'url_code: ""',
            'url_dataset: ""',
            f'url_doi: {yaml_quote(f"https://doi.org/{candidate.doi}" if candidate.doi else candidate.url)}',
            'tier: "archive"',
            "featured: false",
            f'thumbnail: {yaml_quote(thumbnail)}',
            'visual_abstract: ""',
            'abstract: ""',
            'extracted_figure: ""',
            'extracted_figure_source_pdf: ""',
            'extracted_figure_page: ""',
            'extracted_figure_confidence: ""',
            'plain_language_summary: "Newly imported publication candidate from a structured publication scan. Add a manually curated plain-language summary."',
            'why_this_matters: "Newly imported publication candidate from a structured publication scan. Add manual scientific context after review."',
            'research_significance: ""',
            'research_story: ""',
            "key_findings:",
            '  - "Summarize the primary empirical or methodological finding after manual review."',
            "related_software:",
            "  []",
            "related_research:",
            "  []",
            "related_talks:",
            "  []",
            "related_datasets:",
            "  []",
            "related_community:",
            "  []",
            "tags:",
            f"  - {yaml_quote(candidate.publication_type)}",
            f'thumbnail_alt: {yaml_quote(f"Publication preview for {candidate.title}")}',
            "---",
            "",
            "## Review Notes",
            "",
            "This record was imported automatically from a high-confidence publication scan and should receive manual summary/relationship curation.",
        ]
    )
    (path / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (path / "cite.bib").write_text(
        "@article{"
        + slug.replace("-", "_")
        + ",\n"
        + f"  title={{{candidate.title}}},\n"
        + f"  author={{{' and '.join(candidate.authors)}}},\n"
        + f"  journal={{{candidate.publication}}},\n"
        + f"  year={{{candidate.year}}},\n"
        + f"  doi={{{candidate.doi}}}\n"
        + "}\n",
        encoding="utf-8",
    )


def main() -> None:
    existing_dois, existing_titles, existing_slugs = existing_records()
    candidates = dedupe_candidates(pubmed_candidates() + crossref_candidates())
    imported = []
    duplicates = []
    ambiguous = []
    for candidate in sorted(candidates, key=lambda c: (c.year, c.title), reverse=True):
        title_norm = ascii_norm(candidate.title)
        slug = slugify(f"{candidate.year}-{candidate.title}" if candidate.year else candidate.title)
        is_duplicate = (candidate.doi and candidate.doi.lower() in existing_dois) or title_norm in existing_titles or slug in existing_slugs
        record = {
            "title": candidate.title,
            "year": candidate.year,
            "source": candidate.source,
            "doi": candidate.doi,
            "pubmed": candidate.pubmed,
            "publication": candidate.publication,
            "publication_type": candidate.publication_type,
            "url": candidate.url,
        }
        if is_duplicate:
            duplicates.append(record)
            continue
        high_confidence = bool(candidate.doi) and has_raha_author(candidate.authors) and candidate.publication_type in {"article", "inproceedings"}
        if high_confidence:
            write_publication(candidate, slug)
            existing_slugs.add(slug)
            existing_titles.add(title_norm)
            if candidate.doi:
                existing_dois.add(candidate.doi.lower())
            imported.append({**record, "slug": slug})
        else:
            ambiguous.append({**record, "reason": "Missing DOI, weak author identity, or unsupported publication type"})
    write_yaml(
        REPORT,
        {
            "scan": {
                "sources": ["PubMed author search", "CrossRef author search", "manual broad web search recommended for ambiguous additions"],
                "author_queries": AUTHOR_QUERIES,
            },
            "imported": imported,
            "duplicates": duplicates,
            "ambiguous": ambiguous,
        },
    )
    print(f"Imported {len(imported)} new records")
    print(f"Duplicates {len(duplicates)}")
    print(f"Ambiguous {len(ambiguous)}")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
