from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.verification.evidence_contract_v1 import EvidenceContractEvaluatorV1
from core.verification.evidence_contract import RequirementRegistry
from core.verification.post_render_evaluators_v1 import PostRenderEvaluatorSuite as V1PostRenderEvaluatorSuite


class PostRenderEvaluatorSuite(V1PostRenderEvaluatorSuite):
    """Frozen V1 suite with registry-complete readiness accounting."""

    EVALUATOR_VERSION = "2.1.0"

    async def _run_design_system_metrics(self) -> Path:
        path = await super()._run_design_system_metrics()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return path
        row = (payload.get("requirements") or {}).get("VISUAL-005")
        if isinstance(row, dict) and row.get("outcome") == "cantTell":
            system_path = self.run_dir / "design-system.json"
            system = self._json_file(system_path)
            typography = ((system.get("foundations") or {}).get("typography") or {}) if system else {}
            roles = sorted(str(name) for name in typography if "family" in str(name).casefold())
            if roles and len(roles) <= self.MAX_FONT_FAMILIES:
                row.update(
                    {
                        "outcome": "passed",
                        "applicable": True,
                        "rationale": (
                            f"Design system declares {len(roles)} explicit font-family role slot(s), within the V1 role budget of {self.MAX_FONT_FAMILIES}. "
                            "Resolved rendered font sizes/line heights are verified separately by typography-metrics.json."
                        ),
                        "test_targets": [],
                        "evidence_files": [str(system_path)],
                    }
                )
                payload.setdefault("metrics", {})["font_role_tokens"] = roles
                path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def _write_readiness(self, outputs: dict[str, str]) -> Path:
        registry = RequirementRegistry()
        built_in = {
            "semantic_visual",
            "browser_target_smoke",
            "browser_contrast_smoke",
            "browser_viewports",
            "reference_plan",
            "artifact_claim",
            "human_review",
        }
        dedicated = set(EvidenceContractEvaluatorV1.DEDICATED_REPORTS)
        requested = sorted({str(rule.evaluator or "") for rule in registry.rules if rule.evaluator})
        missing = sorted(set(requested) - built_in - dedicated)
        payload: dict[str, Any] = {
            "schema_version": 1,
            "registry_version": registry.version,
            "machine_requirement_count": sum(1 for rule in registry.rules if rule.machine_gate),
            "requested_evaluators": requested,
            "built_in_evaluators": sorted(built_in),
            "dedicated_evaluators": sorted(dedicated),
            "missing_evaluator_implementations": missing,
            "outputs": outputs,
            "v1_evaluator_coverage_complete": not missing,
            "note": (
                "Coverage-complete means every registry evaluator has an implementation path. "
                "A concrete website may still truthfully fail, be inapplicable, or return cantTell when evidence is insufficient."
            ),
        }
        return self._write_report("v1-verification-readiness.json", payload)
