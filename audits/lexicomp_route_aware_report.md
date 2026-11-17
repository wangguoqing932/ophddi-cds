# Lexicomp route-aware comparison (42 L1 cases)

**Resource:** Lexicomp Drug Interactions, accessed through the UpToDate interface provided by OpenMed  
**Version:** UpToDate 2018; application version 1.1  
**URL:** http://167.99.184.127/d/di.htm  
**Accessed:** 2026-11-11

## 1. Coverage and rating distribution

- Cases: **42**; ophthalmic-specific Lexicomp entry: **35**; generic entry only: **7** (apraclonidine, bromfenac, voriconazole).
- Lexicomp ratings: **X** 1, **D** 0, **C** 15, **B** 1, **none** 25.
- Reference labels: **high** 13, **medium** 19, **low** 10.
- Cascade labels: **high** 9, **medium** 18, **low** 15.

## 2. Five-to-three-level mapping

Primary mapping: **X/D → high; C → medium; B/A/no interaction → low**. This follows the Lexicomp definitions (X avoid, D consider modification, C monitor, B no action, A no known interaction) and the manuscript's grade definitions. Because C is a broad 'monitor' category that can include severe mechanisms, a sensitivity analysis maps **C → high**.

### 2.1 Primary mapping, all 42 cases

| Reference \ Lexicomp | high | medium | low |
|---|---:|---:|---:|
| high | 0 | 8 | 5 |
| medium | 1 | 7 | 11 |
| low | 0 | 0 | 10 |

- Exact agreement: **17/42 (0.405; 95% CI 0.270–0.555)**; κ **0.129**.
- High-risk sensitivity: **0/13 (0.000)**; specificity **28/29 (0.966)**.

### 2.2 Sensitivity mapping (C → high), all 42 cases

- Exact agreement: **18/42 (0.429)**; κ **0.222**.
- High-risk sensitivity: **8/13 (0.615)**; specificity **21/29 (0.724)**.

### 2.3 Binary 'any actionable interaction' (C/D/X vs A/B/no interaction)

- Lexicomp actionable: **16/42**; reference non-low: **32/42**.
- Sensitivity for non-low: **16/32 (0.500)**; specificity **10/10 (1.000)**.
- Exact: **26/42 (0.619)**; κ **0.323**.

### 2.4 Ophthalmic-specific entries only (n = 35)

- Exact agreement under the primary mapping: **15/35 (0.429)**; high-risk sensitivity **0/10 (0.000)**; specificity **25/25 (1.000)**.
- Binary actionable: sensitivity **15/27 (0.556)**; specificity **8/8 (1.000)**.

### 2.5 Cascade vs Lexicomp (primary mapping)

- Exact agreement: **21/42 (0.500)**; κ **0.195**.

## 3. Route-specific versus systemic entries

Among **35** pairs with both an ophthalmic and a systemic entry, **21** were discordant. In every discordant pair the ophthalmic entry was lower; **18** had no interaction at the ophthalmic entry but C/D/X at the systemic entry, and **3** were C vs D.

| Case | Ophthalmic entry | Risk | Systemic entry | Risk |
|---|---|---|---|---|
| G08 | Ketorolac (Ophthalmic) | none | Ketorolac (Systemic) | D |
| G19 | Moxifloxacin (Ophthalmic) | none | Moxifloxacin (Systemic) | X |
| G142 | Timolol (Ophthalmic) | C | Timolol (Systemic) | D |

## 4. Interpretation

The comparison has three implications. First, Lexicomp's product-level entries are genuinely route-aware: in 21 of 35 pairs the ophthalmic entry returned a lower rating than the systemic entry, and in 18 pairs it returned no interaction at all where the systemic entry returned C, D or X. This direction is consistent with the exposure premise of the manuscript.

Second, Lexicomp's five-level scale is not a severity-equivalent gold standard for the three-level grade. Its C category ('monitor therapy') spans both reference-high and reference-medium pairs: 8 of 13 reference-high pairs and 7 of 19 reference-medium pairs were rated C. Under the pre-specified mapping, exact agreement is therefore modest, and high-risk sensitivity is low; under a binary 'any actionable interaction' definition, Lexicomp flags 16 of 42 pairs and captures 16 of 32 reference non-low pairs without flagging any of the 10 reference-low pairs.

Third, the direction of the discordance is informative. For topical NSAID + anticoagulant pairs (ketorolac or flurbiprofen with warfarin), Lexicomp's ophthalmic entry returns no interaction while its systemic entry returns D. That is exactly the product-level blind spot the manuscript is designed to address: absence of an interaction in a product-level database is not evidence of absent systemic exposure. The cascade flags these pairs as medium, and the reference labels two of them as high; the disagreement should be read as a difference in exposure modelling, not as proof that either resource is wrong.

## 5. Caveats

- The accessible instance is **UpToDate 2018 via OpenMed**, not a current licensed Lexicomp subscription. Ratings may have changed since 2018.
- Seven cases (apraclonidine, bromfenac, voriconazole) had no ophthalmic-specific entry; the generic ingredient entry was used and flagged. A sensitivity analysis restricted to the 35 ophthalmic-specific cases is reported above.
- Lexicomp ratings are proprietary and are not redistributed in the public release; the raw extraction is retained locally for audit.
- The 42-case reference labels are a subset of the frozen author-derived L1 reference set and were not separately adjudicated; they are not an independent gold standard. Agreement with them measures alignment with the manuscript's exposure model, not clinical truth.
