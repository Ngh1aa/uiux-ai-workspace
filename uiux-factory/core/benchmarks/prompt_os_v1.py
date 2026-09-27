from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.design_context_schema import ReferenceBoard
from core.contracts.spec_profile import infer_spec_profile
from core.verification.reference_aware_visual_qa import ReferenceAwareVisualQA


class PromptOSProfileBenchmark:
    """Deterministic four-profile benchmark for the spec-first Prompt OS pipeline.

    The benchmark intentionally uses missing deep visual evidence so each profile's conservative
    fallback policy is observable without network/provider dependencies.
    """

    def __init__(self, fixture_path: Path):
        self.fixture_path = Path(fixture_path).resolve()
        payload = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        self.schema_version = payload.get("schema_version", "")
        self.cases = payload.get("cases", [])

    @staticmethod
    def _browser_report(workdir: Path) -> Path:
        report = BrowserQAResult.model_validate(
            {
                "status": "passed",
                "project_slug": "benchmark",
                "project_dir": str(workdir),
                "base_url": "http://127.0.0.1:4173",
                "routes": ["/"],
                "viewports": [{"name": "desktop", "width": 1440, "height": 1000}],
                "evidence": [],
                "gates": {
                    "routes_discovered": True,
                    "screenshots_created": True,
                    "no_page_errors": True,
                    "no_console_errors": True,
                    "no_horizontal_overflow": True,
                    "internal_links_valid": True,
                    "semantic_smoke_passed": True,
                    "image_alt_smoke_passed": True,
                    "accessible_name_smoke_passed": True,
                    "control_target_smoke_passed": True,
                    "focus_visibility_smoke_passed": True,
                    "elementary_visual_sanity_passed": True,
                    "ready_for_visual_critic": True,
                },
            }
        )
        path = workdir / "browser-report.json"
        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _reference_board(workdir: Path) -> Path:
        path = workdir / "reference-dna.json"
        path.write_text(ReferenceBoard().model_dump_json(indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _spec(workdir: Path, profile: str) -> Path:
        path = workdir / "02-FULL-BUILD-SPEC.md"
        path.write_text(
            "# Benchmark — Full Build Spec\n\n"
            "## Specification profile\n\n"
            f"- Profile: `{profile}`\n\n"
            "## 0. Mission\n\n"
            "Benchmark the frozen profile contract without hidden chat context.\n",
            encoding="utf-8",
        )
        return path

    def run_case(self, case: dict[str, Any], workdir: Path) -> dict[str, Any]:
        payload = {
            "goal": case["goal"],
            "reference_analysis": case.get("reference_analysis", ""),
        }
        profile = infer_spec_profile(payload)
        spec = self._spec(workdir, profile)
        result = ReferenceAwareVisualQA.evaluate(
            browser_report_path=self._browser_report(workdir),
            reference_analysis_path=self._reference_board(workdir),
            full_spec_path=spec,
        )

        checks = {
            "profile": profile == case["expected_profile"],
            "visual_mode": result.mode == case["expected_visual_mode"],
            "missing_evidence_status": result.status == case["expected_missing_evidence_status"],
            "missing_evidence_blocking": result.blocking is case["expected_missing_evidence_blocking"],
            "no_example_leakage": "mostar" not in spec.read_text(encoding="utf-8").lower(),
        }
        return {
            "id": case["id"],
            "profile": profile,
            "visual_mode": result.mode,
            "status": result.status,
            "blocking": result.blocking,
            "checks": checks,
            "passed": all(checks.values()),
        }

    def run(self, output_path: Path | None = None) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        with tempfile.TemporaryDirectory(prefix="prompt-os-benchmark-") as tmp:
            root = Path(tmp)
            for index, case in enumerate(self.cases):
                case_dir = root / f"case-{index + 1:02d}"
                case_dir.mkdir(parents=True, exist_ok=True)
                rows.append(self.run_case(case, case_dir))

        result = {
            "schema_version": self.schema_version,
            "fixture": str(self.fixture_path),
            "case_count": len(rows),
            "passed_count": sum(1 for row in rows if row["passed"]),
            "failed_count": sum(1 for row in rows if not row["passed"]),
            "passed": bool(rows) and all(row["passed"] for row in rows),
            "cases": rows,
        }
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result
