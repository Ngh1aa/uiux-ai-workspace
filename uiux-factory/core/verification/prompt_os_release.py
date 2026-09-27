from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.benchmarks.prompt_os_v1 import PromptOSProfileBenchmark


EXPECTED_PROFILES = {
    "pixel_faithful",
    "preserve_and_extend",
    "redesign",
    "original_design",
}
EXPECTED_OUTPUTS = [
    "00-PROJECT-CONTEXT.md",
    "01-RESEARCH-PROMPT.md",
    "02-FULL-BUILD-SPEC.md",
    "03-IMPLEMENTATION-PROMPT.md",
    "04-QA-REMEDIATION-PROMPT.md",
]
REQUIRED_CAPABILITIES = {
    "spec_first_prompt_pack",
    "frozen_full_build_spec",
    "profile_aware_spec_writer",
    "reference_evidence_extraction",
    "motion_interaction_sampling",
    "evidence_provenance",
    "reference_aware_visual_qa",
    "root_cause_repair_loop",
    "four_profile_benchmark",
}


class PromptOSV1ReleaseVerifier:
    """Fail-closed verifier for the machine-declared Prompt OS v1 capability surface."""

    def __init__(self, factory_root: Path):
        self.factory_root = Path(factory_root).resolve()
        self.workspace_root = self.factory_root.parent
        self.compiler_root = self.workspace_root / "skills_UIUX" / "prompt-compiler"
        self.manifest_path = self.compiler_root / "prompt-os-v1.json"
        self.benchmark_fixture = self.factory_root / "benchmarks" / "prompt_os_v1_profiles.json"

    def _required_paths(self) -> dict[str, Path]:
        return {
            "release_manifest": self.manifest_path,
            "release_doc": self.compiler_root / "PROMPT-OS-V1.md",
            "spec_first_contract": self.compiler_root / "SPEC-FIRST-EXECUTION.md",
            "profile_router": self.compiler_root / "PROFILE-ROUTING.md",
            "reference_visual_policy": self.compiler_root / "REFERENCE-AWARE-VISUAL-QA.md",
            "benchmark_doc": self.compiler_root / "PROMPT-OS-V1-BENCHMARK.md",
            "profile_classifier": self.factory_root / "core" / "contracts" / "spec_profile.py",
            "reference_evidence_schema": self.factory_root / "core" / "contracts" / "reference_evidence_schema.py",
            "evidence_provenance_schema": self.factory_root / "core" / "contracts" / "evidence_provenance_schema.py",
            "reference_visual_qa_schema": self.factory_root / "core" / "contracts" / "reference_visual_qa_schema.py",
            "reference_extractor": self.factory_root / "core" / "actions" / "analyze_references.py",
            "motion_sampler": self.factory_root / "core" / "actions" / "analyze_references_with_motion.py",
            "provenance_wrapper": self.factory_root / "core" / "actions" / "analyze_references_with_provenance.py",
            "spec_writer": self.factory_root / "core" / "agents" / "spec_writer.py",
            "profile_prompt_pack": self.factory_root / "core" / "actions" / "create_profile_aware_prompt_pack.py",
            "reference_visual_qa": self.factory_root / "core" / "verification" / "reference_aware_visual_qa.py",
            "quality_loop": self.factory_root / "core" / "orchestration" / "quality_loop.py",
            "development_manager": self.factory_root / "core" / "manager" / "development_manager.py",
            "benchmark_fixture": self.benchmark_fixture,
        }

    @staticmethod
    def _flow_order_source_ok(manager_path: Path) -> bool:
        source = manager_path.read_text(encoding="utf-8")
        ordered = [
            '"specification_compile"',
            '"implementation"',
            '"browser_qa"',
            '"visual_qa"',
            '"repair"',
        ]
        positions = [source.find(token) for token in ordered]
        return all(position >= 0 for position in positions) and positions == sorted(positions)

    def verify(self) -> dict[str, Any]:
        checks: dict[str, bool] = {}
        details: dict[str, Any] = {}

        required = self._required_paths()
        missing = [name for name, path in required.items() if not path.is_file()]
        checks["required_paths_present"] = not missing
        details["missing_paths"] = missing

        if not self.manifest_path.is_file():
            return {
                "schema_version": "prompt-os-release-verification.v1",
                "version": "UNKNOWN",
                "passed": False,
                "checks": checks,
                "details": details,
            }

        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        details["manifest_version"] = manifest.get("version")
        checks["version_is_1_0_0"] = manifest.get("version") == "1.0.0"
        checks["profile_set_exact"] = set(manifest.get("profiles", [])) == EXPECTED_PROFILES
        checks["canonical_outputs_exact"] = manifest.get("canonical_outputs") == EXPECTED_OUTPUTS

        capabilities = manifest.get("capabilities", {})
        checks["capabilities_declared"] = all(capabilities.get(name) is True for name in REQUIRED_CAPABILITIES)
        undeclared = sorted(REQUIRED_CAPABILITIES - set(capabilities))
        details["missing_capability_keys"] = undeclared

        pipeline = manifest.get("pipeline", [])
        expected_tail = ["specification_compile", "implementation", "browser_qa", "visual_qa", "repair"]
        try:
            tail_positions = [pipeline.index(stage) for stage in expected_tail]
            checks["manifest_pipeline_order"] = tail_positions == sorted(tail_positions)
        except ValueError:
            checks["manifest_pipeline_order"] = False

        manager_path = required["development_manager"]
        checks["runtime_pipeline_order"] = manager_path.is_file() and self._flow_order_source_ok(manager_path)

        benchmark = PromptOSProfileBenchmark(self.benchmark_fixture).run()
        checks["four_profile_benchmark"] = benchmark["passed"] is True and benchmark["case_count"] == 4
        details["benchmark"] = benchmark

        source_guards = {
            "reference_not_clone": "evidence, not permission to clone",
            "rendered_pixels_required": "actual rendered",
        }
        skill_path = self.compiler_root / "SKILL.md"
        skill_text = skill_path.read_text(encoding="utf-8") if skill_path.is_file() else ""
        checks["reference_not_clone_guard"] = (
            source_guards["reference_not_clone"] in (self.compiler_root / "REFERENCE-AWARE-VISUAL-QA.md").read_text(encoding="utf-8")
        )
        checks["frozen_spec_contract"] = "freeze `02-FULL-BUILD-SPEC.md`" in skill_text

        passed = bool(checks) and all(checks.values())
        return {
            "schema_version": "prompt-os-release-verification.v1",
            "version": manifest.get("version", "UNKNOWN"),
            "passed": passed,
            "checks": checks,
            "details": details,
        }
