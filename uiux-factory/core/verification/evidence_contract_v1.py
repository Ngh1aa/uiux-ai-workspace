from __future__ import annotations

import json
import re
from pathlib import Path

from core.contracts.evidence_contract_schema import EvidenceOutcome, RequirementDefinition, RequirementResult
from core.verification.evidence_contract import EvidenceContractEvaluator


class EvidenceContractEvaluatorV1(EvidenceContractEvaluator):
    """Frozen V1 registry evaluator with complete machine-evaluator routing.

    Artifact claims are validated by requirement-specific content checks instead
    of treating file presence as proof. Unknown or ambiguous evidence remains
    ``cantTell`` and therefore cannot silently pass the machine gate.
    """

    EVALUATOR_VERSION = "3.0.0"
    DEDICATED_REPORTS = {
        **EvidenceContractEvaluator.DEDICATED_REPORTS,
        "design_system_metrics": "design-system-metrics.json",
        "typography_metrics": "typography-metrics.json",
        "motion_metrics": "motion-accessibility-report.json",
        "reduced_motion_test": "motion-accessibility-report.json",
        "artifact_and_trace": "journey-report.json",
        "style_word_critic": "style-word-review.json",
        "reference_comparison": "reference-comparison-review.json",
    }

    @staticmethod
    def _text(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    @staticmethod
    def _json(path: Path) -> dict:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _resolved(value: str) -> bool:
        text = str(value or "").strip().strip("`*_ -")
        return bool(text) and text.casefold() not in {
            "unknown",
            "needs_validation",
            "needs validation",
            "n/a",
            "none",
            "null",
        }

    @classmethod
    def _extract_style_words(cls, text: str) -> list[str]:
        section = re.search(
            r"##\s*(?:Style Adjectives|Style Words)\s*\n(.*?)(?=\n##\s|\Z)",
            text,
            flags=re.I | re.S,
        )
        values: list[str] = []
        if section:
            for line in section.group(1).splitlines():
                match = re.match(r"\s*(?:[-*]|\d+[.)])\s*(?:\*\*)?([^*\n—:]{2,50})", line)
                if match:
                    values.append(match.group(1).strip().strip("`*_ "))
        if not values:
            line = re.search(r"(?:style adjectives|style words)\s*:\s*([^\n]+)", text, flags=re.I)
            if line:
                values = [item.strip().strip("`*_ ") for item in re.split(r"[,;/]", line.group(1)) if item.strip()]
        return list(dict.fromkeys(value for value in values if value))

    def _refs(self, rule: RequirementDefinition, run_dir: Path, *, run_id: str, project_digest: str):
        refs = []
        for item in rule.required_evidence:
            path = run_dir / item
            if path.is_file():
                refs.append(self._evidence_ref(path, run_id=run_id, project_digest=project_digest, kind="artifact"))
        return refs

    def _artifact_claim_result(
        self,
        rule: RequirementDefinition,
        run_dir: Path,
        *,
        run_id: str,
        project_digest: str,
    ) -> RequirementResult:
        evidence = self._refs(rule, run_dir, run_id=run_id, project_digest=project_digest)
        if rule.id == "UNDERSTANDING-001":
            text = self._text(run_dir / "ux-ia.md") + "\n" + self._text(run_dir / "research.md")
            match = re.search(r"(?:Primary audience|Target audience|Audience)\s*:\s*([^\n]+)", text, flags=re.I)
            passed = bool(match and self._resolved(match.group(1)))
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if passed else EvidenceOutcome.CANT_TELL,
                applicable=True,
                evidence=evidence,
                rationale=("A concrete audience/context statement is documented." if passed else "Audience artifacts exist but no concrete non-placeholder audience/context could be verified."),
            )

        if rule.id == "UNDERSTANDING-002":
            art = self._text(run_dir / "art-direction.md")
            match = re.search(r"(?:##\s*First Impression|First impression\s*:)(.*?)(?=\n##\s|\Z)", art, flags=re.I | re.S)
            passed = bool(match and self._resolved(match.group(1).strip().splitlines()[0] if match.group(1).strip() else ""))
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if passed else EvidenceOutcome.CANT_TELL,
                applicable=True,
                evidence=evidence,
                rationale=("A concrete intended first-impression statement is documented." if passed else "art-direction.md does not expose a concrete First Impression contract."),
            )

        if rule.id == "UNDERSTANDING-005":
            words = self._extract_style_words(self._text(run_dir / "art-direction.md"))
            passed = len(words) == 3 and len({word.casefold() for word in words}) == 3
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if passed else EvidenceOutcome.FAILED,
                applicable=True,
                evidence=evidence,
                test_targets=words,
                rationale=(f"Exactly three distinct style adjectives are documented: {', '.join(words)}." if passed else f"Exactly three distinct explicit style adjectives are required; found {len(words)}."),
            )

        if rule.id == "UNDERSTANDING-006":
            contract_path = run_dir / "demo-path-contract.json"
            contract = self._json(contract_path)
            if contract_path.is_file():
                evidence.append(self._evidence_ref(contract_path, run_id=run_id, project_digest=project_digest, kind="demo-path-contract"))
            steps = contract.get("steps") or []
            unresolved = contract.get("unresolved") or []
            passed = len(steps) >= 2 and not unresolved
            outcome = EvidenceOutcome.PASSED if passed else (EvidenceOutcome.CANT_TELL if steps else EvidenceOutcome.UNTESTED)
            return RequirementResult(
                requirement_id=rule.id,
                outcome=outcome,
                applicable=True,
                evidence=evidence,
                test_targets=[str(value) for value in unresolved],
                rationale=("A structured entry-to-completion demo-path contract is resolved." if passed else "The demo path is missing, too short, or contains unresolved planned routes."),
            )

        if rule.id == "UNDERSTANDING-007":
            art = self._text(run_dir / "art-direction.md")
            match = re.search(r"##\s*Visual Signature\s*\n(.*?)(?=\n##\s|\Z)", art, flags=re.I | re.S)
            signature = match.group(1).strip() if match else ""
            passed = self._resolved(signature)
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if passed else EvidenceOutcome.CANT_TELL,
                applicable=True,
                evidence=evidence,
                rationale=("A concrete Visual Signature/signature moment is documented." if passed else "No concrete Visual Signature/signature moment could be verified."),
            )

        if rule.id == "UNDERSTANDING-008":
            research = self._text(run_dir / "research.md")
            context = self._json(run_dir / "design-context.json")
            content_terms = re.search(r"\b(asset|assets|media|image|imagery|content|copy|logo|photo|video)\b", research, flags=re.I)
            reality_recorded = bool(context) and bool(content_terms)
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if reality_recorded else EvidenceOutcome.CANT_TELL,
                applicable=True,
                evidence=evidence,
                rationale=("Research and design context explicitly record content/media reality or gaps." if reality_recorded else "Content/media reality is not explicit enough across research.md and design-context.json."),
            )

        if rule.id == "VISUAL-001":
            system = self._json(run_dir / "design-system.json")
            foundations = system.get("foundations") or {}
            colors = foundations.get("colors") or {}
            semantic = foundations.get("semantic_colors") or {}
            names = {str(name).casefold() for name in colors} | {str(name).casefold() for name in semantic}
            has_brand = any(token in name for name in names for token in ("brand", "primary", "accent"))
            has_neutral = any(token in name for name in names for token in ("text", "surface", "background", "neutral"))
            has_semantic = bool(semantic) or any(token in name for name in names for token in ("error", "success", "warning", "info"))
            if not system:
                outcome = EvidenceOutcome.UNTESTED
                rationale = "design-system.json is missing or unreadable."
            elif has_brand and has_neutral and has_semantic:
                outcome = EvidenceOutcome.PASSED
                rationale = "Design system defines brand/supporting, neutral/text/surface and semantic colour roles."
            else:
                outcome = EvidenceOutcome.FAILED
                rationale = "Design system exists but does not expose enough explicit brand, neutral and semantic colour roles."
            return RequirementResult(requirement_id=rule.id, outcome=outcome, applicable=True, evidence=evidence, rationale=rationale)

        if rule.id == "CRITIQUE-003":
            path = run_dir / "decoration-review.json"
            payload = self._json(path)
            if path.is_file():
                evidence.append(self._evidence_ref(path, run_id=run_id, project_digest=project_digest, kind="decoration-review"))
            row = (payload.get("requirements") or {}).get("CRITIQUE-003") if payload else None
            if isinstance(row, dict):
                try:
                    outcome = EvidenceOutcome(str(row.get("outcome", "cantTell")))
                except ValueError:
                    outcome = EvidenceOutcome.CANT_TELL
                return RequirementResult(
                    requirement_id=rule.id,
                    outcome=outcome,
                    applicable=row.get("applicable", True),
                    evidence=evidence,
                    test_targets=[str(value) for value in row.get("test_targets", [])],
                    rationale=str(row.get("rationale", "Decoration review returned no rationale.")),
                )
            return RequirementResult(requirement_id=rule.id, outcome=EvidenceOutcome.UNTESTED, applicable=None, evidence=evidence, rationale="decoration-review.json has not been generated.")

        return super()._artifact_claim_result(rule, run_dir, run_id=run_id, project_digest=project_digest)
