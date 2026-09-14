"""kg_layer.py — Precise knowledge graph from entity registries + rule engine. Zero API calls, 100% coverage."""

import csv
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

class PreciseKG:
    """Serves structured entity data and rule-matched context for any drug pair."""
    
    def __init__(self):
        # Load entity A registry
        self.a_registry = {}
        with open(ROOT / "data" / "seed" / "entities_a.csv", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                name = row["primary_name"].lower()
                self.a_registry[name] = {
                    "id": row["topical_ophthalmic_medications_id"],
                    "name": row["primary_name"],
                    "class": row.get("category", ""),
                    "flags": [f.strip() for f in row.get("flags", "").split("|") if f.strip()],
                    "mechanisms": [m.strip() for m in row.get("active_mechanisms", "").split("|") if m.strip()] if row.get("active_mechanisms") else [],
                }
        
        # Load entity B registry
        self.b_registry = {}
        with open(ROOT / "data" / "seed" / "entities_b.csv", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                name = row["generic_name"].lower()
                flags = [f.strip() for f in row.get("flags", "").split("|") if f.strip()]
                self.b_registry[name] = {
                    "id": row["entity_b_id"],
                    "name": row["generic_name"],
                    "class": row.get("drug_class", ""),
                    "flags": flags,
                    "pathways": [p.strip() for p in row.get("metabolic_pathways", "").split("|") if p.strip()] if row.get("metabolic_pathways") else [],
                    "nti": "narrow_therapeutic_index" in flags,
                    "ti_tier": row.get("therapeutic_index_tier", ""),
                }
        
        # Load rules
        with open(ROOT / "configs" / "rules.yaml", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f)
        
        # Load combo drug notes
        combo_path = ROOT / "data" / "combo_notes.json"
        self.combo_notes = json.loads(combo_path.read_text(encoding="utf-8")) if combo_path.exists() else {}
    
    # ── Entity lookup ──
    def get_ophthalmic(self, drug_name: str) -> dict | None:
        return self.a_registry.get(drug_name.lower())
    
    def get_systemic(self, drug_name: str) -> dict | None:
        return self.b_registry.get(drug_name.lower())
    
    # ── Context builders ──
    def entity_profile(self, drug_name: str, side: str = "A") -> str:
        """Human-readable entity profile."""
        if side == "A":
            e = self.get_ophthalmic(drug_name)
            if not e:
                return f"[{drug_name}]: Not found in ophthalmic drug registry."
            
            flags_str = ", ".join(e["flags"])
            
            # Absorption level
            abs_level = "unknown"
            abs_desc = ""
            for f in e["flags"]:
                if "systemic_absorption_" in f:
                    abs_level = f.replace("systemic_absorption_", "")
                    abs_desc = {"high": " >50% bioavailability", "medium": " 10-50% bioavailability", 
                                "low": " <10% bioavailability"}.get(abs_level, "")
            
            lines = [
                f"[{e['name']}] ophthalmic | class: {e['class']}",
                f"  Systemic absorption from eye drops: {abs_level}{abs_desc}",
                f"  All flags: {flags_str}",
            ]
            if e["mechanisms"]:
                lines.append(f"  Mechanisms: {', '.join(e['mechanisms'])}")
            return "\n".join(lines)
        
        else:  # side B
            e = self.get_systemic(drug_name)
            if not e:
                return f"[{drug_name}]: Not found in systemic drug registry."
            
            flags_str = ", ".join(e["flags"])
            lines = [
                f"[{e['name']}] systemic | class: {e['class']}",
                f"  Flags: {flags_str}",
            ]
            if e["pathways"]:
                lines.append(f"  Metabolic pathways: {', '.join(e['pathways'])}")
            if e["nti"]:
                lines.append(f"  ⚠️ NARROW THERAPEUTIC INDEX drug (tier: {e['ti_tier']})")
            return "\n".join(lines)
    
    def matched_rules(self, oph_name: str, sys_name: str) -> str:
        """Rules whose flags match this drug pair."""
        oph = self.get_ophthalmic(oph_name)
        sys_ = self.get_systemic(sys_name)
        
        if not oph or not sys_:
            return "Cannot match rules: one or both drugs not in registry."
        
        oph_flags = set(oph["flags"])
        sys_flags = set(sys_["flags"])
        
        matched = []
        for rule in self.rules.get("rules", []):
            a_f = set(rule.get("entity_a_flags", []))
            b_f = set(rule.get("entity_b_flags", []))
            if rule.get("match") == "all":
                # ALL required flags must be present (AND semantics)
                a_ok = a_f <= oph_flags if a_f else True
                b_ok = b_f <= sys_flags if b_f else True
            else:
                # ANY single flag suffices (OR semantics, default)
                a_ok = bool(a_f & oph_flags)
                b_ok = bool(b_f & sys_flags)
            if a_ok and b_ok:
                matched.append(
                    f"  [{rule['id']}] severity={rule['severity']}: "
                    f"{rule.get('rationale', '')[:200]}\n"
                    f"    Recommendation: {rule.get('recommendation', '')[:150]}"
                )
        
        if not matched:
            return "No specific interaction rules matched for this drug pair based on flag intersection."
        
        return "INTERACTION RULES TRIGGERED:\n" + "\n".join(matched[:8])
    
    def deterministic_level(self, oph_name: str, sys_name: str) -> tuple[str | None, list[str]]:
        """Cascade-stage deterministic verdict (v1: rule layer only).

        Returns (level, matched_rule_ids):
          - MAX severity over matched rules, or
          - 'low' when the G19 hard constraint applies (low absorption + no rules), or
          - (None, []) when no rule matched and no hard constraint (LLM stage handles it).
        """
        level, matched_ids, _ = self.deterministic_level_v2(oph_name, sys_name, use_matrix=False)
        return level, matched_ids

    def deterministic_level_v2(self, oph_name: str, sys_name: str, use_matrix: bool = True) -> tuple[str | None, list[str], dict]:
        """Architecture-v2 cascade verdict.

        L1: exact rule layer (MAX-MATCH over 40 rules; match:all/any semantics)
        L2: class-matrix layer (class pair × absorption scaling + upgrades)  [when use_matrix]
        L3: G19 hard constraint (low/very-low absorption + no rule, no matrix signal)
        default: low (no known class interaction) — traceable, not a gap

        Returns (level, matched_rule_ids, info) where info explains the decision path.
        """
        oph = self.get_ophthalmic(oph_name)
        sys_ = self.get_systemic(sys_name)
        if not oph or not sys_:
            return None, [], {"path": "unknown_drug"}

        oph_flags = set(oph["flags"])
        sys_flags = set(sys_["flags"])
        sev_rank = {"high": 3, "medium": 2, "low": 1}

        # ── L1 exact rules (citation-verified precise layer) ──
        best, matched_ids = None, []
        for rule in self.rules.get("rules", []):
            a_f = set(rule.get("entity_a_flags", []))
            b_f = set(rule.get("entity_b_flags", []))
            if rule.get("match") == "all":
                a_ok = a_f <= oph_flags if a_f else True
                b_ok = b_f <= sys_flags if b_f else True
            else:
                a_ok = bool(a_f & oph_flags)
                b_ok = bool(b_f & sys_flags)
            # Optional class scoping: rules that only apply to a specific class
            # (e.g. corticosteroid, not corticosteroid_weak) — keeps the finer
            # class-matrix cells from being overridden by flag-generic rules.
            if a_ok and rule.get("a_class") and self._class_of_a(oph["name"]) != rule["a_class"]:
                a_ok = False
            if a_ok and b_ok:
                matched_ids.append(rule["id"])
                sv = sev_rank[rule["severity"]]
                if best is None or sv > sev_rank[best]:
                    best = rule["severity"]

        # ── L2 class matrix (cascade takes MAX of rule layer and matrix layer) ──
        matrix_level = None
        matrix_info = {}
        if use_matrix:
            cell = self._class_matrix_lookup(oph, sys_, oph_flags)
            if cell and cell.get("level") in ("high", "medium", "low"):
                lvl = cell["level"]
                absl = next((f for f in oph_flags if "systemic_absorption_" in f), None)
                scale = self._matrix_scale.get(absl or "none", "keep")
                if scale == "force_low":
                    lvl = "low"
                elif scale == "keep":
                    lvl = self._apply_upgrade(oph, sys_, cell["level"], oph_flags)
                matrix_level = lvl
                matrix_info = {"cell": cell, "absorption": absl}

        if best is not None and matrix_level is not None:
            lvl = best if sev_rank[best] >= sev_rank[matrix_level] else matrix_level
            path = "rule" if lvl == best else "matrix"
            return lvl, matched_ids, {"path": path, "rules": matched_ids, **matrix_info}
        if best is not None:
            return best, matched_ids, {"path": "rule", "rules": matched_ids}
        if matrix_level is not None:
            return matrix_level, matched_ids, {"path": "matrix", **matrix_info}

        # ── L3 G19 ──
        if "systemic_absorption_low" in oph_flags or "systemic_absorption_very_low" in oph_flags:
            return "low", matched_ids, {"path": "g19", "absorption": "low_or_very_low"}

        # default: no known class interaction -> low (traceable)
        return "low", matched_ids, {"path": "default_low", "note": "no known class interaction"}

    # ── v2 helpers ──
    @property
    def _matrix(self) -> dict:
        if not hasattr(self, "_matrix_data"):
            import json
            p = ROOT / "configs" / "class_matrix.yaml"
            if p.exists():
                self._matrix_data = yaml.safe_load(p.read_text(encoding="utf-8"))
            else:
                self._matrix_data = {"matrix": {}, "upgrades": {}, "default_cell": {}}
        return self._matrix_data

    @property
    def _class_map(self) -> dict:
        if not hasattr(self, "_class_map_data"):
            import json
            p = ROOT / "configs" / "drug_classes.yaml"
            if p.exists():
                self._class_map_data = yaml.safe_load(p.read_text(encoding="utf-8"))
            else:
                self._class_map_data = {"class_of": {"entity_a": {}, "entity_b": {}}}
        return self._class_map_data

    @property
    def _matrix_scale(self) -> dict:
        return self._matrix.get("absorption_scale", {})

    def _class_of_a(self, name: str) -> str:
        m = self._class_map.get("class_of", {}).get("entity_a", {})
        return m.get(name) or m.get(name.lower()) or "other"

    def _class_of_b(self, name: str) -> str:
        m = self._class_map.get("class_of", {}).get("entity_b", {})
        return m.get(name) or m.get(name.lower()) or "other"

    def _class_matrix_lookup(self, oph: dict, sys_: dict, oph_flags: set) -> dict | None:
        ac = self._class_of_a(oph["name"])
        bc = self._class_of_b(sys_["name"])
        cell = self._matrix.get("matrix", {}).get(ac, {}).get(bc)
        if cell is None:
            cell = dict(self._matrix.get("default_cell", {}))
        cell = dict(cell)
        cell["a_class"], cell["b_class"] = ac, bc
        return cell

    def _apply_upgrade(self, oph: dict, sys_: dict, level: str, oph_flags: set) -> str:
        """Raise base matrix level via upgrades (scoped to the A-class + flags)."""
        if level == "high":
            return level
        bc = self._class_of_b(sys_["name"])
        ac = self._class_of_a(oph["name"])
        for up in self._matrix.get("upgrades", {}).values():
            if up.get("a_class") and ac != up["a_class"]:
                continue
            if bc not in up.get("b_classes", []):
                continue
            need = set(up.get("requires_flags", []))
            if need and not need <= oph_flags:
                continue
            if up.get("to") == "high":
                return "high"
        return level

    def full_kg_context(self, oph_name: str, sys_name: str) -> str:
        """Complete structured context for a drug pair."""
        parts = []
        parts.append("=== DRUG PROFILES (Precise Knowledge Graph) ===")
        
        # Check for combination drug notes
        oph = self.get_ophthalmic(oph_name)
        if oph and oph["id"] in self.combo_notes:
            parts.append(f"⚠️ COMBINATION PRODUCT: {self.combo_notes[oph['id']]}")
        
        parts.append(self.entity_profile(oph_name, "A"))
        parts.append(self.entity_profile(sys_name, "B"))
        parts.append("\n=== MATCHED RULES ===")
        parts.append(self.matched_rules(oph_name, sys_name))
        
        # Add G19-style hard constraint for low-absorption + no rules
        if oph and ("systemic_absorption_low" in oph["flags"] or "systemic_absorption_very_low" in oph["flags"]):
            matched = self.matched_rules(oph_name, sys_name)
            if "No specific interaction rules matched" in matched:
                parts.append("\n⚠️ HARD CONSTRAINT: Ophthalmic drug has LOW systemic absorption and NO interaction rules matched. Risk assessment MUST be 'low'. Do NOT extrapolate from systemic-route data.")
        
        return "\n".join(parts)
