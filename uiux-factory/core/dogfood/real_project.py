from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from core.benchmarks.regression_corpus import BenchmarkCorpus
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.browser_evidence import PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.browser_observation import PlaywrightBrowserObservationAdapter
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.safe_read import SafeReader
from core.runtime.flow_os.skill_sections import read_skill_section
from core.runtime.flow_os.vision_director import VisionCreativeDirectorAdapter


DEFAULT_VIEWPORTS = [
    {"name": "desktop", "width": 1440, "height": 1000},
    {"name": "tablet", "width": 768, "height": 1024},
    {"name": "mobile", "width": 390, "height": 844},
]

NOVA_DOMAIN_ALIASES = {
    "financial-services": "financial-services",
    "consumer_fintech_personal_banking": "financial-services",
}

OPTIONAL_PROFILE_FIELDS = ("product_archetype", "validation_lane")


class RealProjectDogfoodError(RuntimeError):
    """Raised when a pinned real-project dogfood invariant is not satisfied."""


def _git_sha(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=15,
        shell=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value if len(value) == 40 else None


def _load_json(reader: SafeReader, path: str) -> dict[str, Any]:
    payload = json.loads(reader.read_text(path).content)
    if not isinstance(payload, dict):
        raise RealProjectDogfoodError(f"{path} must contain a JSON object")
    return payload


def _find_capability(index: dict[str, Any], skill: str) -> str:
    for row in list(index.get("routed_skills", [])):
        if not isinstance(row, dict) or str(row.get("skill", "")) != skill:
            continue
        sections = row.get("sections", [])
        if not isinstance(sections, list) or not sections:
            break
        first = sections[0]
        if isinstance(first, dict) and str(first.get("capability", "")).strip():
            return str(first["capability"])
    raise RealProjectDogfoodError(f"no retrievable A8.5 section capability for routed skill {skill}")


def _normalize_nova_domain(source_domain: str) -> str:
    normalized = NOVA_DOMAIN_ALIASES.get(str(source_domain).strip())
    if normalized is None:
        supported = ", ".join(sorted(NOVA_DOMAIN_ALIASES))
        raise RealProjectDogfoodError(
            f"unsupported Nova domain taxonomy {source_domain!r}; supported source values: {supported}"
        )
    return normalized


class RealProjectDogfoodRunner:
    """Deterministic read-only dogfood lane over a real checked-out UI project.

    A13 deliberately does not fake autonomous model work. It verifies the parts of the
    Factory that can be truthfully exercised in zero-cost CI: source-truth ingestion,
    canonical Flow routing, section-level skill retrieval, stage resume continuity,
    real multi-viewport browser evidence, model-readable browser observation, the A10
    vision trust boundary, and the versioned A12 benchmark manifest.
    """

    def __init__(self, *, skills_root: Path, factory_root: Path, project_root: Path) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.factory_root = Path(factory_root).resolve()
        self.project_root = Path(project_root).resolve()
        if not self.skills_root.is_dir():
            raise RealProjectDogfoodError(f"skills root does not exist: {self.skills_root}")
        if not self.factory_root.is_dir():
            raise RealProjectDogfoodError(f"factory root does not exist: {self.factory_root}")
        if not self.project_root.is_dir():
            raise RealProjectDogfoodError(f"project root does not exist: {self.project_root}")
        self.reader = SafeReader(self.project_root)
        self.policy = json.loads(
            (self.skills_root / "runtime" / "runtime-policy.json").read_text(encoding="utf-8")
        )

    def _project_shape(self) -> dict[str, Any]:
        has_package = (self.project_root / "package.json").is_file()
        static_entrypoints = [
            name
            for name in ("index.html", "app.html", "prototype.html")
            if (self.project_root / name).is_file()
        ]
        if has_package:
            kind = "package_project"
        elif {"index.html", "app.html"}.issubset(static_entrypoints):
            kind = "static_html"
        else:
            kind = "unknown"
        return {
            "kind": kind,
            "has_package_json": has_package,
            "static_entrypoints": static_entrypoints,
        }

    def _target_findings(self, shape: dict[str, Any], profile: dict[str, Any]) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        workflow = ".github/workflows/nova-cloud-qa.yml"
        if (self.project_root / workflow).is_file():
            text = self.reader.read_text(workflow).content
            if not shape["has_package_json"] and ("npm ci" in text or "npm install" in text):
                findings.append(
                    {
                        "id": "stale-package-install",
                        "severity": "P1",
                        "summary": "Target workflow installs npm dependencies although the checked-out project has no package.json.",
                    }
                )
            compact = " ".join(text.split())
            if "run.py\" qa" in compact or "run.py qa" in compact or "run.py' qa" in compact:
                findings.append(
                    {
                        "id": "stale-factory-cli",
                        "severity": "P1",
                        "summary": "Target workflow calls the removed legacy `run.py qa` Factory CLI surface.",
                    }
                )

        source_domain = str(profile.get("domain", "")).strip()
        normalized_domain = _normalize_nova_domain(source_domain)
        if source_domain != normalized_domain:
            findings.append(
                {
                    "id": "legacy-domain-taxonomy",
                    "severity": "P2",
                    "summary": (
                        f"Nova profile uses legacy domain taxonomy {source_domain!r}; "
                        f"A13 explicitly normalizes it to Flow domain {normalized_domain!r}."
                    ),
                }
            )
        missing_optional = [
            key for key in OPTIONAL_PROFILE_FIELDS if not str(profile.get(key, "")).strip()
        ]
        if missing_optional:
            findings.append(
                {
                    "id": "partial-profile-taxonomy",
                    "severity": "P2",
                    "summary": (
                        "Nova profile predates optional normalized taxonomy fields: "
                        + ", ".join(missing_optional)
                        + ". A13 does not invent them."
                    ),
                }
            )
        return findings

    def _profile(self) -> dict[str, Any]:
        profile = _load_json(self.reader, ".uiux-profile.json")
        source_domain = str(profile.get("domain", "")).strip()
        if not source_domain:
            raise RealProjectDogfoodError(".uiux-profile.json missing required field: domain")
        _normalize_nova_domain(source_domain)
        return profile

    def run(
        self,
        *,
        base_url: str,
        route: str = "/app.html?screen=home",
        expected_target_sha: str | None = None,
        report_path: Path | None = None,
    ) -> dict[str, Any]:
        shape = self._project_shape()
        profile = self._profile()
        project_context = self.reader.read_text("PROJECT-CONTEXT.md")
        target_sha = _git_sha(self.project_root)
        if expected_target_sha and target_sha != expected_target_sha:
            raise RealProjectDogfoodError(
                f"dogfood target SHA mismatch: expected {expected_target_sha}, got {target_sha or '(not a git checkout)'}"
            )

        source_domain = str(profile["domain"]).strip()
        flow_domain = _normalize_nova_domain(source_domain)
        missing_optional = [
            key for key in OPTIONAL_PROFILE_FIELDS if not str(profile.get(key, "")).strip()
        ]
        overrides: dict[str, Any] = {
            "intent": "redesign",
            "change_surface": "PRODUCT",
            "website_type": "application",
            "domain": flow_domain,
            "mode": "interactive-prototype",
            "risk": "medium",
            "features": ["dashboard", "motion"],
        }
        for key in OPTIONAL_PROFILE_FIELDS:
            value = str(profile.get(key, "")).strip()
            if value:
                overrides[key] = value

        harness = ProviderNeutralAgentHarness(self.skills_root, self.project_root)
        manager = ManagedFlowController(harness)
        managed = manager.start_from_goal(
            "Redesign and dogfood the existing Nova mobile-first fintech money-control product using its real source truth, responsive rendered evidence and visual-review readiness; do not release.",
            authority="read_only",
            overrides=overrides,
        )
        if managed.flow.id != "professional-website-redesign":
            raise RealProjectDogfoodError(
                f"Nova PRODUCT redesign routed to unexpected flow: {managed.flow.id}"
            )
        research = next((stage for stage in managed.flow.stages if stage.id == "research"), None)
        if research is None:
            raise RealProjectDogfoodError("professional website flow has no research stage")
        if "financial-product-intelligence" not in research.skills:
            raise RealProjectDogfoodError("Nova financial-services routing omitted financial-product-intelligence")

        explicit_sources = ["PROJECT-CONTEXT.md", ".uiux-profile.json"]
        stage_state = manager.start_stage(managed, explicit_sources=explicit_sources)
        loaded_sources = [str(item) for item in stage_state.context.get("loaded_sources", [])]
        if loaded_sources != explicit_sources:
            raise RealProjectDogfoodError(
                f"research source context drift: expected {explicit_sources!r}, got {loaded_sources!r}"
            )

        section_index_path = self.project_root / ".uiux-agent-runs" / stage_state.run_id / "skill-section-index.json"
        section_index = json.loads(section_index_path.read_text(encoding="utf-8"))
        capability = _find_capability(section_index, "financial-product-intelligence")
        section = read_skill_section(
            self.project_root,
            self.skills_root,
            capability,
            self.policy,
        )
        if section["skill"] != "financial-product-intelligence" or len(str(section["sha256"])) != 64:
            raise RealProjectDogfoodError("A8.5 financial skill section retrieval was not grounded")

        resumed = manager.resume(managed.manager_run_id)
        resumed_stage = manager.start_stage(resumed, explicit_sources=explicit_sources)
        if resumed_stage.run_id != stage_state.run_id:
            raise RealProjectDogfoodError("A8.4 resume continuity created a new same-revision specialist run")

        qa_root = self.factory_root / "qa"
        sha_label = (target_sha or "fixture")[:12]
        evidence_dir = qa_root / "artifacts" / f"a13-nova-{sha_label}"
        if evidence_dir.exists():
            shutil.rmtree(evidence_dir)
        browser = PlaywrightBrowserEvidenceAdapter(qa_root, self.policy)
        records = browser.capture(
            base_url,
            [route],
            artifacts_dir=evidence_dir,
            viewports=list(DEFAULT_VIEWPORTS),
        )
        viewport_names = {
            str(record.data.get("viewport", {}).get("name", ""))
            for record in records
            if isinstance(record.data.get("viewport"), dict)
        }
        expected_viewports = {item["name"] for item in DEFAULT_VIEWPORTS}
        if len(records) != len(DEFAULT_VIEWPORTS) or viewport_names != expected_viewports:
            raise RealProjectDogfoodError(
                f"A13 viewport coverage mismatch: records={len(records)}, viewports={sorted(viewport_names)}"
            )
        failed_browser = [record.id for record in records if record.status != "PASS"]
        if failed_browser:
            raise RealProjectDogfoodError("Nova browser evidence failed: " + ", ".join(failed_browser))

        observation = PlaywrightBrowserObservationAdapter(qa_root, self.policy).observe(
            evidence_dir,
            route=route,
        )
        if observation.get("trusted") is not False or observation.get("advisory_only") is not True:
            raise RealProjectDogfoodError("A9 browser observation trust boundary drifted")
        if observation.get("browser_evidence_status") != "PASS":
            raise RealProjectDogfoodError("A9 model-readable observation did not inherit a passing browser render")

        vision = VisionCreativeDirectorAdapter(evidence_dir, self.policy).review(records, analyzer=None)
        if vision.get("status") != "NOT_RUN" or vision.get("trusted") is not False:
            raise RealProjectDogfoodError("A10 zero-cost vision boundary manufactured a verdict")
        if int(vision.get("coverage", {}).get("viewports", 0)) != len(DEFAULT_VIEWPORTS):
            raise RealProjectDogfoodError("A10 did not receive real desktop/tablet/mobile screenshot coverage")

        corpus = BenchmarkCorpus.load(self.factory_root / "benchmarks" / "corpus" / "uiux-product-v1.json")
        manifest = corpus.manifest()
        if manifest["case_count"] < 8 or len(str(manifest["content_hash"])) != 64:
            raise RealProjectDogfoodError("A12 benchmark corpus manifest is not valid")

        checks = {
            "source_truth_loaded": bool(project_context.content.strip()) and bool(profile),
            "source_profile_grounded": bool(source_domain) and flow_domain == "financial-services",
            "static_project_detected": shape["kind"] == "static_html",
            "canonical_flow_routed": managed.flow.id == "professional-website-redesign",
            "financial_skill_routed": "financial-product-intelligence" in research.skills,
            "explicit_sources_bound": loaded_sources == explicit_sources,
            "section_level_jit_grounded": section["skill"] == "financial-product-intelligence",
            "same_revision_resume": resumed_stage.run_id == stage_state.run_id,
            "browser_render_pass": not failed_browser,
            "browser_observation_advisory": observation.get("trusted") is False,
            "responsive_evidence_coverage": viewport_names == expected_viewports,
            "vision_zero_cost_truthful": vision.get("status") == "NOT_RUN",
            "benchmark_manifest_bound": manifest["case_count"] >= 8,
            "target_sha_bound": not expected_target_sha or target_sha == expected_target_sha,
        }
        report = {
            "schema_version": 1,
            "phase": "A13",
            "target": "Ngh1aa/Nova",
            "target_sha": target_sha,
            "expected_target_sha": expected_target_sha,
            "project_shape": shape,
            "profile": {
                "source_domain": source_domain,
                "normalized_flow_domain": flow_domain,
                "product_archetype": str(profile.get("product_archetype", "")).strip() or None,
                "validation_lane": str(profile.get("validation_lane", "")).strip() or None,
                "missing_optional_fields": missing_optional,
                "normalization_rule": (
                    "Explicit A13 compatibility mapping from Nova's source taxonomy to canonical Flow taxonomy; "
                    "missing optional fields remain null and are not invented."
                ),
            },
            "runtime_task_context": {
                "domain": managed.task_context.get("domain"),
                "product_archetype": managed.task_context.get("product_archetype"),
                "validation_lane": managed.task_context.get("validation_lane"),
            },
            "flow": {
                "id": managed.flow.id,
                "revision": managed.flow.revision,
                "research_stage_run_id": stage_state.run_id,
                "financial_skill_source": research.jit_skill_sources.get("financial-product-intelligence"),
            },
            "jit_section": {
                "skill": section["skill"],
                "section_id": section["section_id"],
                "sha256": section["sha256"],
                "chars": section["chars"],
            },
            "browser": {
                "route": route,
                "evidence_count": len(records),
                "viewports": sorted(viewport_names),
                "status": "PASS",
                "observation_id": observation.get("observation_id"),
                "observation_trusted": observation.get("trusted"),
            },
            "vision": {
                "status": vision.get("status"),
                "trusted": vision.get("trusted"),
                "viewports": vision.get("coverage", {}).get("viewports"),
                "reason": "No configured vision analyzer in zero-cost CI; no aesthetic PASS is manufactured.",
            },
            "benchmark": {
                "corpus_id": manifest["corpus_id"],
                "version": manifest["version"],
                "content_hash": manifest["content_hash"],
                "case_count": manifest["case_count"],
                "scoring_status": "NOT_RUN",
                "reason": "A13 binds the canonical corpus manifest but does not pretend Nova is every A12 benchmark case.",
            },
            "provider_reasoning": {
                "status": "NOT_RUN",
                "reason": "A13 CI is provider-neutral and carries no external model credentials; no autonomous reasoning claim is fabricated.",
            },
            "human_review": {"status": "pending", "verdict": None},
            "release": {"status": "NOT_ATTEMPTED"},
            "target_findings": self._target_findings(shape, profile),
            "checks": checks,
            "passed": all(checks.values()),
            "truth_boundary": (
                "A13 PASS means deterministic Factory integration passed on the pinned real Nova checkout. "
                "It is not a provider-quality, aesthetic-human-review, merge, deploy or release verdict."
            ),
        }
        if report_path is not None:
            output = Path(report_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return report
