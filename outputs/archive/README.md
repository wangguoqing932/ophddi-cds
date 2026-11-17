# Archive — superseded versions (not part of the submission)

Everything under `outputs/archive/` is retained for provenance and audit only.
**No file here is part of the final submission package.** The current files are:

- manuscript source: `outputs/paper/manuscript.en.md`
- submission package: `outputs/deliverables/frontiers/`
- response letters: `outputs/submission/response_to_reviewers_r1.*`, `..._r2.*`

Archived on 2026-11-13, after the final consistency gate (`92/92 PASS`) and the
reference audit (45/45 Zotero, 44/44 Crossref-verified non-arXiv entries).

| Folder | What it holds | Why it is kept |
|---|---|---|
| `manuscript_pre_versions/` | Seven `_manuscript.pre_*.md` snapshots taken before each compression/polish step (pre-5000, pre-6000, pre-compress, pre-Frontiers, pre-numbered, pre-polish, pre-rebalance) | Shows how the text evolved; none is a submitted version |
| `paper_fragments/` | The earlier `outputs/paper/manuscript.md`, old `cover_letter.md`, `figure_prompts.md`, `figure_table_qc_report.md`, and the old `review/`, `sections/`, `supplementary/` working folders | Superseded drafts and section fragments |
| `reference_research/` | `citation_pool.json`, `new_ref*.json`, `refs_final.json`, `refs_pubmed.json` | Intermediate reference-candidate lists; final verified table is `outputs/audits/reference_verification_table.md` |
| `old_figures/` | `_previous_20261017/` (figures before the October redesign), `_pristine/` (pre-edit originals), `_qc/` (QC renders), `figure6_redraw_prompt.md` (brief used to commission the current Figure 6) | Earlier figure generations; current figures are in `outputs/figures/` and `outputs/deliverables/frontiers/` |
| `old_predictions/` | `_prepromptfix/` predictions from before the prompt correction | Superseded baseline run; the numbers used in the paper come from `outputs/multiseed_per_dataset*/` |
| `bmc_submission/` | The earlier BMC Ophthalmology submission package (manuscript, cover letter, declarations, highlights, journal guidelines, response) | Previous journal attempt, never submitted through this package |
| `qa_pages/` | Rendered page PNGs used for layout checks (page 01–55, `fig6/`, `r1/`) | Visual QA record for the 50-page manuscript and 44-page supplement |
| `figures_qa/` | 67 ad-hoc page/figure check screenshots (`_audit_*`, `_check_*`, `_fig6*`, `_final_*`, `figure2_check.jpg`) plus three text-size crops | Only evidence of the visual checks; not referenced by the manuscript |
| `scratch_audits/` | One-off audit scripts and outputs (`_independent_core.py`, `_diff_manuscript.py`, `_di_script.js`, head extracts, `_pagecheck/`) | Working notes from the audit rounds |

`bmc_submission/ethics/Ethics_Approval_K202509-29.pdf` is a scanned approval for an unrelated
refractive-error study; it does not cover this work and is retained only as provenance. The
current submission reports no human-subjects research and no formal ethics determination, so
no approval document is included in the Frontiers package.

Restore rule: if an archived file is ever needed, copy it out — do not edit in place,
and do not add archive paths to build scripts. The build and gate scripts read only
`outputs/paper/`, `outputs/deliverables/`, `outputs/submission/`, `outputs/audits/`,
`outputs/tables/`, `outputs/figures/`, `configs/` and `data/`.
