# OphDDI-CDS — Frontiers in Pharmacology submission package

Prepared for submission to **Frontiers in Pharmacology** (Original Research).

Ethics: no patients or patient-level data were used; the only human-participant data collection was an anonymous professional-opinion exercise, so no formal ethics submission was required and consent beyond agreeing to take part was not required.

## Word and display-item counts (Frontiers requires these on the first page)

| Item | Count |
|---|---|
| Abstract | 346 words |
| Main text (Introduction through Conclusions, excluding abstract, references, declarations and figure captions) | 8,184 words |
| Figures | 6 (Figures 1–5 drawn on a shared 180 mm canvas; Figure 6 is the author-supplied raster at 147.3 mm) |
| Tables | 7 (main text, three-line); 19 supplementary tables (S1–S19; S5b and S18b are subtables) |
| References | 45 (numbered in order of appearance) |

Frontiers allows up to 12,000 words for Original Research; the manuscript is within the limit.

**Revision note (R1+R2, 11 November 2026).** This package is the combined Reviewer-1 and Reviewer-2 revision. The primary analysis now uses the frozen labels (101/118, 0.856); the corrected labels (104/118, 0.881) are a sensitivity analysis, and the ungated analysis (103/118, 0.873) is reported in Table S19. The absorption tiers were reconciled (12 high, 20 medium, 59 low, 11 very low, 7 minimal, 4 none), the rules were audited (Table S9), and the engine now flags the 176 default-path pairs (9.1%) as unassessed. Tables 3 and 5 and Figures 1-3 were regenerated. The final revision gates the NSAID-antihypertensive rule on absorption (primary), reports the ungated analysis as a sensitivity analysis (Table S19), and rebuilds every affected number. The R2 revision adds the rule/matrix construction protocol (Text S10, Tables S9/S14), grade definitions (Table 6), patient-factor mapping (Table S15), source-tier definitions (Table S16), exposure-risk mechanism table (Table S17), a route-aware DDInter comparison (Table 7, Table S18), a Lexicomp comparison (Table S18b) and the workflow figure (Figure 6).

## Files to upload

| # | File | Role | Notes |
|---|---|---|---|
| 1 | `manuscript.docx` | Main manuscript | Editable Word file; figures and tables embedded at the end, captions with each item |
| 2 | `Supplementary_Material.docx` | Supplementary material | Texts S1–S10 and Tables S1–S19 (including S5b and S18b) |
| 3 | `figure1_architecture.png` … `figure6_workflow.png` | Figures | 300–400 dpi at final size; TIFF versions also provided |
| 4 | `cover_letter.md` / `.docx` | Cover letter | Journal-specific |
| 5 | `scope_statement.md` | Scope statement | 200 words, required at submission, not published |
| Related | `manuscript_marked_changes.docx` / `.pdf` | Redline manuscript | Word-level red marking; changed table units marked red |
| Related | `Supplementary_Material_marked_changes.docx` / `.pdf` | Redline supplement | Word-level text marking; changed table rows red, unchanged rows black |

Figures are also supplied as PDF/TIFF in `outputs/figures/`. Frontiers accepts TIF/TIFF, JPEG and EPS; the deposited TIFFs are 300–400 dpi.

## Format compliance notes

- **Reference style:** numbered in order of appearance, author–year details and DOIs included.
- **Sections:** Introduction / Materials and methods / Results / Discussion / Conclusions, plus Declarations. Subheadings use three numeric levels.
- **Abstract:** single paragraph, 346 words, no references, no figures or tables cited.
- **Figures:** panels would be labelled (A), (B) where a figure has panels; Figure 1 is a single-panel schematic. Captions appear with each figure at the end of the manuscript.
- **Tables:** placed at the end, caption immediately before each table, empty line before and after.
- **Smallest type in figures:** all figures were redrawn on a 180 mm canvas with an 8.0 pt floor; the smallest type is 8.0 pt at final size.
- **AI disclosure:** stated in the Generative AI paragraph of the Declarations and in Materials and methods.

## Deviations from the earlier BMC-era package (historical)

The current submission is to **Frontiers in Pharmacology**; the BMC-era package is archived in `outputs/archive/bmc_submission/` and is not part of this submission.

1. The expert case-level ratings are in Supplementary Table S3; the main text cites Figure 3 and that table.
2. The expert grade review is reported in one Results subsection of about 600 words (including the frozen-subset mapping, the correction timeline and the displayed-versus-engine distinction), one Discussion paragraph, and single clauses in Limitations and Conclusions. The full protocol and per-case data remain in the supplement, so the claim is still auditable.
3. `outputs/submission/` now contains only the two final response letters (`response_to_reviewers_r1.*`, `..._r2.*`) and the ethics documents. The BMC-era files were moved to `outputs/archive/bmc_submission/` and must not be uploaded.

## Figure type-size status

Frontiers requires the smallest text in a figure to be no less than 8 pt at final size.

| Figure | Print width | Min type | Status |
|---|---|---|---|
| Figure 1 | 180.1 mm | 8.0 pt | compliant |
| Figure 2 | 182.3 mm | 8.0 pt | compliant (re-laid out: legend moved below, labels vertical) |
| Figure 3 | 180.1 mm | 8.0 pt | compliant (re-laid out: panel titles shortened, legend below) |
| Figure 4 | 180.3 mm | 8.0 pt | compliant (right panel rebuilt as bars; case count corrected) |
| Figure 5 | 176.7 mm | 8.0 pt | compliant |
| Figure 6 | 147.3 mm (5.2 in in the manuscript) | ~7 pt | author-supplied raster; 300 dpi TIFF/PDF; below the 8 pt guideline, retained at the author's supplied design |

Figures 1–5 were redrawn on a 180 mm canvas with an 8 pt floor. Figure 6 is a raster
supplied by the author; its smallest text is approximately 7 pt at 147.3 mm (about
6.3 pt at the 5.2 in width used in the manuscript), which is below the Frontiers
8 pt guideline and may be queried at the production check. All TIFFs are RGB,
LZW-compressed, at 300 dpi.

## Corrections made while preparing this package

- **Figure 4 panel (b)** previously claimed eight demo cases with a 3/3/2 split; the deposited data contain six cases (3 high, 2 medium, 1 low). The panel title and the figure legend now match `outputs/data_outputs/demo_cases.jsonl`.
- **Table 1 / Supplementary Table S4**: the DrugBank identifier count for systemic agents was 218 and is actually 232 (every row carries a `DBxxxxx` record in `label_source`).
- **Supplementary Table S7** was empty in the previous package; it is now rebuilt from `outputs/tables/table3_performance.md`.
- **`pyproject.toml`** declared `requires-python >= 3.10` while the code uses `StrEnum` and `datetime.UTC`; corrected to `>=3.11`.

## Author decisions applied in this version

| Item | Decision | Effect in the manuscript |
|---|---|---|
| Ethics | No patients or patient-level data; anonymous professional-opinion exercise | "Ethics approval and consent to participate are not applicable"; the competent committee is named but no submission was required; consent beyond participation was not required |
| Expert 2's source form | Not discussed | The verifiability caveat is removed; ratings are described as deposited transcripts |
| T1 labels (G01–G20) | Literature annotation, not a separate human adjudication | Described as annotated from named sources (FDA labels, Stockley's, BNF, Drugs.com) with per-case evidence in `provenance.evidence` |
| Repository archive | Tagged and archived | Release tag `v3.0-frontiers`; DOI `10.5281/zenodo.23439606`; this revision will be deposited as a new version of the same record |

