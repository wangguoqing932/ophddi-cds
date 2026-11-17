# PubMed scoping scan for the high-risk disagreement pairs

**Question:** can the “new data” needed for L1/L3/L6 be found on PubMed?

**Method:** for each of the 13 high-risk disagreement pairs, two PubMed queries were run on 2026-11-13:
1. both drug names in title/abstract **plus** an ophthalmic/topical/eye/ocular/intravitreal term;
2. both drug names in title/abstract only.

This is a scoping scan, not a systematic review. A count of 0 means no PubMed record matched the query; it does not prove that no case exists, because titles/abstracts may omit one drug or the route.

| Case | Pair | Class | Ophthalmic-filtered | Pair only | Relevant ophthalmic outcome record? |
|---|---|---|---:|---:|---|
| D3-001 | Timolol + Theophylline | unsupported_undergrading | 0 | 6 | no |
| D3-004 | Timolol + Epinephrine | unsupported_undergrading | 104 | 184 | no |
| D3-006 | Scopolamine + Topiramate | unsupported_undergrading | 0 | 8 | no |
| D3-014 | Timolol + Spironolactone | unsupported_undergrading | 0 | 2 | no |
| D3-018 | Carteolol + Diazepam | unsupported_undergrading | 0 | 1 | no |
| D3-026 | Apraclonidine + Linezolid | ddinter_high_default_path | 0 | 0 | no |
| D3-029 | Betaxolol + Clonidine | ddinter_high_default_path | 5 | 21 | no |
| D3-033 | Homatropine + Topiramate | ddinter_high_default_path | 0 | 0 | no |
| D3-080 | Aflibercept + Leflunomide | ddinter_high_default_path | 0 | 1 | no |
| D3-035 | Apraclonidine + Midazolam | system_overgrading | 0 | 0 | no |
| D3-038 | Apraclonidine + Loperamide | system_overgrading | 0 | 0 | no |
| D3-057 | Tacrolimus + Ibuprofen | system_overgrading | 1 | 10 | no |
| D3-063 | Bromfenac + Enalapril | system_overgrading | 0 | 0 | no |

## What the scan shows

- **Most pairs have no ophthalmic-filtered PubMed record at all** (10 of 13 with 0).
- The non-zero hits are mostly pharmacology, reviews or animal/in-vitro work, not case reports of the pair in patients.
- The largest count (timolol + epinephrine, 104) is inflated by generic glaucoma/drug-class literature; the top titles are not reports of the interaction.
- No record provides an **independent severity adjudication** of our 30 audit cases, and none provides a **development-free test set** for the 118 L1 cases.

## Implication for the residual limitations

| Item | Can PubMed supply it? | Why |
|---|---|---|
| L1 independent adjudication / development-free test set | **No** | PubMed indexes publications, not blinded case-level grades for our case set; a new adjudication still needs non-author reviewers |
| L3 blinded expert panel | **No** | Published panels rate their own cases, not our 12; a new panel is still needed |
| L6 outcome-linked calibration | **Partly, weakly** | Case reports and pharmacovigilance studies can supply outcome signals for some pairs, but they are sparse, biased and cannot substitute for prospective calibration |

## What PubMed can support

- A **literature outcome signal** table for the pairs that do have case reports (e.g. timolol + verapamil/diltiazem bradycardia, topical beta-blocker + oral CCB). This would be a new curation, not a new test set.
- Methodological references for severity grading and DDI alert evaluation.
- It cannot replace L1/L3, and it cannot turn L6 into an outcome-validated claim.

Raw results: `outputs/audits/pubmed_outcome_scan.json`; script: `outputs/audits/pubmed_outcome_scan.py`.
