# Journal Guidelines Snapshot — BMC Bioinformatics

- **Target journal**: BMC Bioinformatics (source: `.planner.config.json` → `target_journal_primary`)
- **Retrieved**: 2026-10-05, online
- **Sources**:
  - `https://link.springer.com/journal/12859/submission-guidelines` (general submission guidelines)
  - `https://link.springer.com/journal/12859/submission-guidelines/research-article` (Research article guidelines)

> An earlier version of this snapshot used the local checklist as a fallback because
> `bmcbioinformatics.biomedcentral.com` was unreachable from this environment. The host
> became reachable, both pages above were retrieved, and every limit below is quoted from
> them.

## Requirements as published (Research article)

- **Abstract**: "should not exceed 350 words"; minimize abbreviations; "do not cite
  references in the abstract"; must include the separate sections **Background**,
  **Results**, **Conclusions**.
- **Keywords**: three to ten.
- **Structure**: Background, Methods, Results, Discussion, Conclusions, Declarations.
  The journal uses *Background*, not *Introduction*.
- **Declarations** (mandatory, all subheadings): Ethics approval and consent to
  participate; Consent for publication; Availability of data and materials; Competing
  interests; Funding; Authors' contributions; Acknowledgements; (Authors' information,
  optional). Sections that do not apply must still appear with "Not applicable".
- **Availability of data and materials**: required section name. Data in a repository
  must follow the journal's fixed sentence with a persistent identifier; data supplied as
  additional files must use "The dataset(s) supporting the conclusions of this article
  is(are) included within the article (and its additional file(s))." BioMed Central
  endorses the Force 11 Data Citation Principles and requires publicly available datasets
  to be referenced in the reference list with an accession number or DOI. **Software must
  state**: project name, project home page, archived version (DOI or unique identifier,
  e.g. Zenodo), operating system(s), programming language, other requirements, licence,
  and any restrictions on non-academic use.
- **Main manuscript text**: double-line spacing; line and page numbering; SI units; no
  page breaks; editable file formats (DOC/DOCX/RTF/TeX).
- **References**: only published, in-press or preprint items; unpublished data and
  personal communications belong in the text, not the reference list; journal
  abbreviations follow Index Medicus/MEDLINE; use footnotes, not endnotes.
- **LLM use**: must be documented in the Methods section.
- **Figures**: numbered in order of first mention and uploaded in that order;
  multi-panel figures labelled a, b, c.

No main-text word limit is stated on the Research article page.

## Compliance check — 0 automated failure(s)

| Item | Requirement | Manuscript | Status |
|---|---|---|---|
| Abstract length | <= 350 words | 348 words | PASS |
| Abstract citations | must not cite references | none | PASS |
| Abstract structure | separate Background / Results / Conclusions | structured | PASS |
| Keywords | 3-10 | 6 | PASS |
| Section naming | Background (BMC convention); 'Introduction' not used | Background | PASS |
| Declarations heading | one 'Declarations' section | present | PASS |
| Declaration subheadings | all 7 BMC subheadings under 'Declarations' | 7/7 present | PASS |
| Data availability naming | 'Availability of data and materials' | correct subheading | PASS |
| Figures | numbered in order of first mention | 5 figures, ordered | PASS |
| Tables | Arabic numerals in sequence | 6 tables | PASS |
| Main text limit | no explicit word limit on the Research article page | 0 words | PASS |
| Line and page numbering | required | set in the .docx (footer line + w:lnNumType) | PASS |
| Double-line spacing | double | DOUBLE (2) in the .docx | PASS |
| LLM use | documented in Methods | documented in Section 2.7 | PASS |
| Software fields | project name / home page / archived version / OS / language / requirements / licence | all present | PASS |

## Requires manual verification

| Item | Requirement | Manuscript | Status |
|---|---|---|---|
| Reference style | journal abbreviations per Index Medicus/MEDLINE | Vancouver-style, abbreviated | manual |

## What to fix before submission


