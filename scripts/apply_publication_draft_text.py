#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from import_publications import ROOT


PUB_DIR = ROOT / "content" / "publication"
PLACEHOLDER_PHRASES = [
    "Add a concise, manually curated explanation of why this paper matters.",
    "Add a readable summary for collaborators, trainees, and interdisciplinary visitors.",
    "Add scientific context, interpretation, and links to related systems.",
]


def front_value(front: str, key: str) -> str:
    lines = front.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            value = line.split(":", 1)[1].strip().strip('"')
            return value
        if line.startswith(f"{key}:") and i + 1 < len(lines):
            return lines[i + 1].strip().strip('"')
    return ""


def front_list(front: str, key: str) -> list[str]:
    lines = front.splitlines()
    values = []
    active = False
    for line in lines:
        if line.startswith(f"{key}:"):
            active = True
            continue
        if active and line.startswith("  - "):
            values.append(line.replace("  - ", "", 1).strip().strip('"'))
            continue
        if active and line and not line.startswith(" "):
            break
    return values


def main() -> None:
    for index_path in PUB_DIR.glob("*/index.md"):
        text = index_path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        front = parts[1]
        body = parts[2].lstrip()
        if not any(phrase in body for phrase in PLACEHOLDER_PHRASES):
            continue
        why = front_value(front, "why_this_matters")
        summary = front_value(front, "plain_language_summary")
        significance = front_value(front, "research_significance")
        story = front_value(front, "research_story")
        findings = front_list(front, "key_findings")
        new_body = [
            "## Why this paper matters",
            "",
            why,
            "",
            "## Key findings",
            "",
            *[f"- {item}" for item in findings],
            "",
            "## Research significance",
            "",
            significance,
            "",
            "## Research story",
            "",
            story,
            "",
            "## Plain-language summary",
            "",
            summary,
            "",
            "## Commentary",
            "",
            "Add manual scientific context, interpretation, and links to related systems.",
            "",
            "## Figures and visual abstracts",
            "",
            "Add publication figures, visual abstracts, and explanatory graphics to this bundle.",
            "",
        ]
        index_path.write_text("---" + front + "---\n" + "\n".join(new_body), encoding="utf-8")


if __name__ == "__main__":
    main()
