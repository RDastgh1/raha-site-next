#!/usr/bin/env python3
"""Curate highlighted publication explainer fields without changing metadata."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS = ROOT / "content" / "publication"
REPORT = ROOT / "data" / "publications" / "content_quality_report.yaml"


CURATED = {
    "2025-brace-ing-for-the-future-establishing-ipad-based-norms-for-cognitive-function-in-the-macs-wihs-combined-cohort-study-preprint": {
        "source_quality": "high: PDF text available; abstract, methods, results, and conclusions extracted",
        "card_significance": "Establishes regression-based iPad cognitive norms for BRACE in the MACS/WIHS Combined Cohort Study.",
        "why_this_matters": "Digital cognitive testing is becoming central to large cohort studies, but interpretation depends on norms that reflect the population being studied. This BRACE paper turns an iPad-based cognitive screener into a more useful research instrument by deriving regression-based norms in MACS/WIHS participants without HIV who were comparable to participants with HIV. For collaborators and reviewers, the importance is practical: the work makes cognitive scores more interpretable across age, education, HIV status, and biological sex in a large, diverse cohort.",
        "key_findings": [
            "The study analyzed BRACE performance from 2,937 MACS/WIHS Combined Cohort Study participants, including 1,063 people without HIV and 1,874 people with HIV.",
            "BRACE measured performance on tablet-based Trail Making, Stroop-Color, and Visual-Spatial Learning tasks.",
            "Regression-based norms were derived from people without HIV; an age-plus-education model was selected to support generalizable interpretation without race-based correction.",
            "Cognitive performance was largely comparable between people with and without HIV; statistically significant differences were small in magnitude.",
            "Age, education, diabetes, and cannabis use were more informative for BRACE performance than many HIV-specific clinical variables after standardization."
        ],
        "plain_language_summary": "BRACE is an iPad-based way to measure cognitive performance. This paper asks how BRACE scores should be interpreted in a large HIV cohort, rather than treating raw scores as self-explanatory. By creating norms from demographically comparable people without HIV, the study gives researchers a clearer baseline for evaluating cognition in people with HIV and for following cognitive health over time."
    },
    "2024-identifying-and-distinguishing-cognitive-profiles-among-virally-suppressed-people-with-hiv": {
        "source_quality": "high: PDF text available; abstract and results extracted",
        "card_significance": "Identifies six cognitive profiles among virally suppressed people with HIV and the factors that distinguish them.",
        "why_this_matters": "The paper moves beyond the question of whether cognitive impairment is present in people with HIV and asks what forms it takes. That distinction matters for trainees, clinicians, and funders because heterogeneous cognitive profiles imply different mechanisms, different risks, and different intervention targets. The work also shows how dimensionality reduction, clustering, and predictive modeling can make neuropsychological data more interpretable.",
        "key_findings": [
            "The analysis included 704 virally suppressed people with HIV from the HIV Neurobehavioral Research Program.",
            "A dimension-reduction and clustering pipeline identified six cognitive profiles: unimpaired, verbal learning and memory weakness, executive function and learning weakness, motor/processing speed/executive weakness, impaired learning and recall with broader weaknesses, and global deficits.",
            "Learning and memory deficits were common across affected profiles.",
            "Self-reported mood symptoms and cognitive or functional complaints were the most consistent correlates of profile membership.",
            "The heterogeneity of profiles supports personalized risk reduction and therapeutic strategies rather than one-size-fits-all cognitive classification."
        ],
        "plain_language_summary": "Even when HIV is virally suppressed, cognitive difficulties do not look the same for everyone. This study grouped people by patterns of neuropsychological performance and found several distinct cognitive profiles. The results suggest that a person’s symptoms, mood, and day-to-day functional complaints can help interpret which kind of cognitive pattern they may be experiencing."
    },
    "2023-machine-learning-approaches-to-understand-cognitive-phenotypes-in-people-with-hiv": {
        "source_quality": "high: PDF text and abstract available",
        "card_significance": "Frames machine learning as a tool for discovering cognitive biotypes in people with HIV.",
        "why_this_matters": "This review is a field-building paper. It explains why cognitive disorders in people with HIV should not be treated as a single uniform outcome, and it lays out what machine learning can and cannot do for cognitive phenotyping. Its value is in connecting methodological choices to the infrastructure the field needs: harmonized data, meaningful metadata, careful confound handling, external validation, and interdisciplinary interpretation.",
        "key_findings": [
            "The paper reviews machine learning approaches for identifying cognitive phenotypes and biotypes in people with HIV.",
            "It emphasizes the Research Domain Criteria framework as a way to study mechanisms that cut across traditional diagnostic categories.",
            "The review highlights the need for common data elements, high-quality longitudinal cohorts, and harmonization across studies.",
            "It argues that validation, interpretability, and handling of confounds are essential before machine-learning models can inform clinical management.",
            "The paper positions cognitive phenotyping as a collaborative problem spanning neuropsychology, infectious disease, data science, and computational modeling."
        ],
        "plain_language_summary": "People with HIV can experience different patterns of cognitive change, and those patterns may have different causes. This paper explains how machine learning can help find those patterns, while also warning that algorithms are only useful when the data are well measured, harmonized, and validated. It is less a single-model paper than a roadmap for doing computational cognitive phenotyping responsibly."
    },
    "2020-meanalyzer-a-spike-train-analysis-tool-for-multi-electrode-arrays": {
        "source_quality": "moderate: DOI metadata available; no local PDF or abstract was available",
        "card_significance": "Introduces MEAnalyzer as reproducible software for spike train analysis in multi-electrode array experiments.",
        "why_this_matters": "MEAnalyzer is important because it treats analysis software as a scientific output, not merely a supporting detail. Multi-electrode array experiments generate dense spike-train data, and reproducible interpretation depends on transparent tools for detecting, summarizing, and visualizing activity. For collaborators and trainees, the paper provides an entry point into electrophysiology workflows where the analysis system itself is part of the research contribution.",
        "key_findings": [
            "The paper presents MEAnalyzer as a software tool for analyzing spike trains from multi-electrode array data.",
            "The work supports reproducible electrophysiology analysis by packaging common processing and visualization tasks into a reusable tool.",
            "The publication makes scientific software visible as a citable research product.",
            "Within this site, MEAnalyzer anchors the software-systems thread and connects experimental neural data to reusable computational infrastructure."
        ],
        "plain_language_summary": "Multi-electrode arrays record activity from many electrodes at once, producing spike-train data that can be difficult to analyze consistently. MEAnalyzer provides software support for that analysis. The broader point of the paper is that well-designed tools can make neural data analysis more transparent, reusable, and easier for other researchers to inspect."
    },
    "2025-blood-brain-barrier-disruption-in-long-covid-and-cognitive-correlates-a-cross-sectional-mri-study": {
        "source_quality": "high: PDF text available; abstract and findings extracted",
        "card_significance": "Uses non-contrast MRI to study blood-brain barrier permeability and cognition in Long COVID.",
        "why_this_matters": "Long COVID has made neuropsychiatric symptoms clinically visible, but mechanisms remain difficult to measure. This paper evaluates blood-brain barrier permeability with a non-contrast MRI approach and relates those measurements to cognitive performance. The work matters because it links patient-reported neurological burden to a measurable brain-imaging biomarker that could be followed in future mechanistic or intervention studies.",
        "key_findings": [
            "The study compared 97 participants with Long COVID and neuropsychiatric symptoms with 31 recovered controls.",
            "Blood-brain barrier permeability was measured using WEPCAST MRI, a non-contrast method estimating the permeability-surface-area product of arterially labeled water entering the brain.",
            "Cognitive performance was summarized into eight factor scores using principal components analysis.",
            "The findings indicate subtle but persistent blood-brain barrier disruption more than two years after infection.",
            "The results suggest a possible relationship between barrier integrity and motor dysfunction, supporting further work on BBB measures as long-term biomarkers of neuropsychiatric complications."
        ],
        "plain_language_summary": "This study asks whether Long COVID symptoms are associated with measurable changes in the blood-brain barrier, the system that helps regulate what enters the brain from the bloodstream. Using MRI rather than an injected contrast agent, the study found evidence of persistent barrier disruption in people with Long COVID. The results suggest one biological pathway that may help explain lasting neurological symptoms."
    },
    "2023-the-baltimore-declaration-toward-the-exploration-of-organoid-intelligence": {
        "source_quality": "moderate: PDF text available; declaration format limits empirical findings",
        "card_significance": "Defines organoid intelligence as an emerging discipline requiring technical, ethical, and community infrastructure.",
        "why_this_matters": "The Baltimore Declaration is not a conventional empirical paper; it is a consensus-oriented statement about how a new field should develop. Its significance is infrastructural. It names organoid intelligence as a research direction that will require advances in stem-cell biology, bioengineering, interfaces, machine learning, data systems, and ethics. That makes the paper relevant to anyone thinking about how scientific communities create standards before a field becomes technically mature.",
        "key_findings": [
            "The declaration frames organoid intelligence as the use of brain organoids and related systems to study learning, memory, biological computation, and brain-machine interfaces.",
            "It identifies major technical needs, including improved organoid engineering, input-output interfaces, feedback systems, and computational methods for interpreting organoid behavior.",
            "It argues that ethical questions should be anticipated alongside technical development rather than treated as an afterthought.",
            "The paper positions organoid intelligence as a collaborative field that depends on shared standards, interdisciplinary governance, and scientific infrastructure."
        ],
        "plain_language_summary": "This paper lays out a vision for organoid intelligence: research that uses brain organoids and engineered systems to study learning, computation, and brain-like behavior. Because the field is still emerging, the declaration focuses on what must be built around the science: technical standards, ethical safeguards, shared language, and collaboration across disciplines."
    },
    "2021-patterns-and-predictors-of-cognitive-function-among-virally-suppressed-women-with-hiv": {
        "source_quality": "high: PDF text and abstract available",
        "card_significance": "Uses self-organizing maps and random forests to characterize cognitive profiles in virally suppressed women with HIV.",
        "why_this_matters": "This paper is central to the computational phenotyping arc because it focuses specifically on women with HIV, a group often underrepresented in mixed-sex neuroHIV analyses. It shows that viral suppression does not eliminate cognitive heterogeneity, and that women’s cognitive profiles can be organized into interpretable patterns rather than treated as a single impairment category. The work also demonstrates how machine learning can surface modifiable or clinically meaningful correlates of profile membership.",
        "key_findings": [
            "The study analyzed neuropsychological data from 929 virally suppressed women with HIV and 717 women without HIV from the Women’s Interagency HIV Study.",
            "Seventeen neuropsychological performance metrics were used to identify high-dimensional cognitive patterns.",
            "Among virally suppressed women with HIV, the analysis identified an unimpaired group plus profiles involving sequencing, processing speed, learning and recognition, and learning and memory weaknesses.",
            "Random forest models were used to identify sociodemographic, behavioral, clinical, and female-specific factors associated with cognitive profile membership.",
            "The findings emphasize profile heterogeneity and point toward potentially modifiable factors that may contribute to impaired cognitive patterns."
        ],
        "plain_language_summary": "This study looked for patterns in cognitive test performance among women with HIV whose virus was suppressed. Instead of asking only whether cognition was impaired, the analysis identified different kinds of cognitive profiles. That makes the findings more useful for understanding why cognitive difficulties vary across individuals and which risk factors may matter for each pattern."
    },
    "2026-metabolomic-levels-mediate-the-link-between-socioeconomic-factors-and-changes-in-declarative-memory-in-women-with-and-without-hiv": {
        "source_quality": "high: PDF text available; structured abstract and results extracted",
        "card_significance": "Links socioeconomic conditions, metabolomic profiles, and longitudinal declarative memory change in women with and without HIV.",
        "why_this_matters": "This paper connects social determinants of health to biological pathways and cognitive aging. Rather than studying income, employment, metabolites, and memory as separate domains, it tests whether metabolomic levels partially mediate the relationship between socioeconomic conditions and changes in declarative memory. For funders and collaborators, the study is a strong example of translational data science: social context, molecular measurement, and longitudinal cognition are analyzed in one framework.",
        "key_findings": [
            "The analysis included 324 women from the Women’s Interagency HIV Study, including 225 women with HIV.",
            "Fifteen metabolites were associated with longitudinal learning change and 16 with memory change after false-discovery-rate correction.",
            "Top metabolites included serotonin, taurine, and niacinamide.",
            "Observed effect sizes were generally similar by HIV serostatus.",
            "Mediation analyses suggested that metabolite levels explained part of the relationship between employment, income, and learning change."
        ],
        "plain_language_summary": "This study asks how social and economic conditions may become biologically embedded in ways that affect memory over time. In a cohort of women with and without HIV, the authors found metabolites related to changes in learning and memory. Some of those metabolite patterns helped explain links between employment, income, and memory performance."
    },
    "2026-longitudinal-effects-of-polypharmacy-on-cognitive-function-in-people-with-hiv": {
        "source_quality": "limited: DOI metadata only; no local PDF and abstract field incomplete",
        "card_significance": "Examines how polypharmacy relates to cognitive function over time in people with HIV.",
        "why_this_matters": "Polypharmacy is a practical clinical problem for people aging with HIV, where medication burden may intersect with comorbidities, viral history, and cognitive vulnerability. This paper belongs in the highlighted set because it turns medication exposure into a longitudinal cognitive risk question. The current local source content is limited, so the summary is intentionally conservative until the full abstract or PDF is added.",
        "key_findings": [
            "The paper studies longitudinal relationships between polypharmacy and cognitive function in people with HIV.",
            "Its focus is clinically actionable: medication burden is a potentially modifiable exposure.",
            "The publication connects cognitive outcomes to real-world treatment complexity in aging and chronic HIV care.",
            "A full local PDF or complete abstract should be added before writing more detailed findings about model results, effect sizes, or specific cognitive domains."
        ],
        "plain_language_summary": "People with HIV often manage multiple medications for HIV and other health conditions. This paper examines whether that medication burden is related to cognitive function over time. The available local metadata is not yet detailed enough to summarize the results beyond that central research question."
    },
    "2024-tryptophan-kynurenine-pathway-activation-and-cognition-in-virally-suppressed-women-with-hiv": {
        "source_quality": "limited: DOI metadata only; no local PDF and abstract field incomplete",
        "card_significance": "Studies whether tryptophan-kynurenine pathway activation is associated with cognition in virally suppressed women with HIV.",
        "why_this_matters": "The tryptophan-kynurenine pathway is a biologically plausible link between immune activation, metabolism, and cognition. This paper is highlighted because it brings a targeted biomarker pathway into the cognitive-health program for virally suppressed women with HIV. Since the local source contains only limited metadata, the current narrative avoids overclaiming specific results until the PDF or complete abstract is available.",
        "key_findings": [
            "The paper focuses on tryptophan-kynurenine pathway activation in virally suppressed women with HIV.",
            "It connects metabolomic or immune-metabolic biomarkers to cognitive outcomes.",
            "The study extends the broader women-with-HIV cognitive phenotyping program into a mechanistic biomarker domain.",
            "A full local PDF or abstract is needed before adding pathway-specific results, cognitive-domain findings, or effect estimates."
        ],
        "plain_language_summary": "This paper examines whether activity in the tryptophan-kynurenine pathway, a metabolic pathway tied to inflammation and immune signaling, is related to cognition among virally suppressed women with HIV. The page is currently conservative because the local source file does not yet include the complete abstract or paper text."
    }
}


def yaml_scalar(value: str) -> list[str]:
    escaped = value.replace('"', '\\"')
    return [f'"{escaped}"']


def yaml_list(values: list[str]) -> list[str]:
    lines = []
    for value in values:
        escaped = value.replace('"', '\\"')
        lines.append(f'  - "{escaped}"')
    return lines


def replace_field(lines: list[str], field: str, value) -> list[str]:
    output = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        if line.startswith(f"{field}:"):
            replaced = True
            output.append(f"{field}:")
            if isinstance(value, list):
                output.extend(yaml_list(value))
            else:
                output[-1] = f"{field}: {yaml_scalar(value)[0]}"
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line and not next_line.startswith(" ") and not next_line.startswith("- "):
                    break
                i += 1
            continue
        output.append(line)
        i += 1
    if not replaced:
        if isinstance(value, list):
            output.append(f"{field}:")
            output.extend(yaml_list(value))
        else:
            output.append(f"{field}: {yaml_scalar(value)[0]}")
    return output


def update_page(slug: str, fields: dict) -> None:
    path = PUBLICATIONS / slug / "index.md"
    text = path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise RuntimeError(f"Missing front matter: {path}")
    front = parts[1].strip("\n").splitlines()
    body = parts[2]
    for field in [
        "card_significance",
        "why_this_matters",
        "key_findings",
        "plain_language_summary",
    ]:
        front = replace_field(front, field, fields[field])
    front = replace_field(front, "research_significance", "")
    front = replace_field(front, "research_story", "")
    new_text = "---\n" + "\n".join(front).rstrip() + "\n---\n"
    path.write_text(new_text)


def write_report() -> None:
    lines = [
        'phase: "Iteration 5 publication content quality pass"',
        'scope: "Highlighted publications only"',
        'notes:',
        '  - "Publication pages now render only Why this matters, Key findings, Plain-language summary, and Research ecosystem."',
        '  - "Research significance and Research story sections were removed from the rendered page model."',
        '  - "Card significance statements are publication-specific and avoid generic ecosystem language."',
        'items:',
    ]
    for slug, fields in CURATED.items():
        title = (PUBLICATIONS / slug / "index.md").read_text().split('title: "', 1)[1].split('"', 1)[0]
        lines.extend([
            "  -",
            f'    slug: "{slug}"',
            f'    title: "{title.replace(chr(34), chr(92)+chr(34))}"',
            f'    source_quality: "{fields["source_quality"]}"',
            f'    card_significance: "{fields["card_significance"].replace(chr(34), chr(92)+chr(34))}"',
        ])
    REPORT.write_text("\n".join(lines) + "\n")


def main() -> None:
    for slug, fields in CURATED.items():
        update_page(slug, fields)
    write_report()
    print(f"Curated {len(CURATED)} highlighted publications")
    print(REPORT)


if __name__ == "__main__":
    main()
