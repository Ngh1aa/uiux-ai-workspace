from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.evidence_contract_schema import (
    EvidenceOutcome,
    EvidenceReference,
    EvidenceSummary,
    PrototypeAcceptanceReport,
    RequirementDefinition,
    RequirementResult,
)
from core.contracts.visual_critic_schema import VisualCriticResult


REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "verification"
    / "prototype-output-requirements.v1.json"
)


class RequirementRegistry:
    def __init__(self, path: Path = REGISTRY_PATH) -> None:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        self.version = str(payload["registry_version"])
        self.rules = [RequirementDefinition.model_validate(item) for item in payload["rules"]]
        ids = [rule.id for rule in self.rules]
        if len(ids) != len(set(ids)):
            raise ValueError("Requirement registry contains duplicate IDs.")


class EvidenceContractEvaluator:
    """Convert QA artifacts into truthful, provenance-bound requirement outcomes."""

    EVALUATOR_VERSION = "2.1.0"
    DEDICATED_REPORTS = {
        "interaction_trace": "interaction-state-report.json",
        "interaction_timing": "interaction-state-report.json",
        "state_crawler": "interaction-state-report.json",
        "preferred_touch_targets": "touch-target-metrics.json",
        "content_stress": "content-stress-report.json",
        "squint_critic": "squint-review.json",
        "blind_five_second": "blind-five-second-review.json",
    }

    def __init__(self, registry: RequirementRegistry | None = None) -> None:
        self.registry = registry or RequirementRegistry()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @classmethod
    def project_digest(cls, project_dir: Path) -> str:
        root = Path(project_dir).resolve()
        digest = hashlib.sha256()
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if ".git" in path.parts:
                continue
            relative = path.relative_to(root).as_posix().encode("utf-8")
            digest.update(relative)
            digest.update(b"\0")
            digest.update(cls._sha256(path).encode("ascii"))
            digest.update(b"\n")
        return digest.hexdigest()

    def _evidence_ref(
        self,
        path: Path,
        *,
        run_id: str,
        project_digest: str,
        kind: str,
        note: str | None = None,
    ) -> EvidenceReference:
        return EvidenceReference(
            kind=kind,
            path=str(path),
            sha256=self._sha256(path) if path.exists() and path.is_file() else None,
            run_id=run_id,
            project_digest=project_digest,
            evaluator=self.__class__.__name__,
            evaluator_version=self.EVALUATOR_VERSION,
            note=note,
        )

    @staticmethod
    def _issue_categories(critic: VisualCriticResult) -> set[str]:
        return {issue.category for issue in critic.issues}

    def _semantic_result(
        self,
        rule: RequirementDefinition,
        critic: VisualCriticResult | None,
        critic_path: Path | None,
        *,
        run_id: str,
        project_digest: str,
    ) -> RequirementResult:
        if critic is None or critic_path is None:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.UNTESTED,
                applicable=None,
                rationale="No VisualCritic artifact was supplied.",
            )
        if critic.review_mode != "vision" or critic.semantic_review is None:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.CANT_TELL,
                applicable=True,
                evidence=[self._evidence_ref(critic_path, run_id=run_id, project_digest=project_digest, kind="visual-critic")],
                rationale="VisualCritic did not provide screenshot-grounded semantic vision evidence.",
            )

        categories = self._issue_categories(critic)
        mapped_failures = {
            "UNDERSTANDING-004": {"domain-fit", "page-role", "semantic-coverage"},
            "UNDERSTANDING-009": {"domain-fit", "page-role", "generic-ai"},
            "UX-001": {"decision-object", "hierarchy"},
            "UX-003": {"page-role"},
            "UX-004": {"hierarchy", "composition-variety"},
            "UX-005": {"decision-object"},
            "UX-009": {"page-role", "decision-object"},
            "UX-010": {"hierarchy"},
            "VISUAL-002": {"hierarchy"},
            "VISUAL-004": {"hierarchy"},
            "VISUAL-008": {"composition-variety", "spacing"},
            "VISUAL-009": {"composition"},
            "VISUAL-011": {"composition-variety", "page-role"},
            "VISUAL-012": {"media", "domain-fit"},
            "VISUAL-013": {"media"},
            "VISUAL-014": {"distinctiveness", "brand-distinctiveness", "generic-ai"},
            "RESPONSIVE-002": {"responsive", "media", "page-role"},
            "CRITIQUE-005": {"distinctiveness", "generic-ai"},
        }
        failure_set = mapped_failures.get(rule.id)
        evidence = [self._evidence_ref(critic_path, run_id=run_id, project_digest=project_digest, kind="visual-critic")]
        if failure_set is None:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.CANT_TELL,
                applicable=True,
                evidence=evidence,
                rationale="Semantic vision evidence exists, but this requirement does not yet have a dedicated deterministic mapping.",
            )
        hit = sorted(categories.intersection(failure_set))
        if hit:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.FAILED,
                applicable=True,
                evidence=evidence,
                rationale="VisualCritic reported blocking evidence in categories: " + ", ".join(hit),
            )
        if not critic.gates.semantic_visual_review_passed:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.CANT_TELL,
                applicable=True,
                evidence=evidence,
                rationale="Semantic visual review ran but did not satisfy its evidence gate.",
            )
        return RequirementResult(
            requirement_id=rule.id,
            outcome=EvidenceOutcome.PASSED,
            applicable=True,
            evidence=evidence,
            rationale="Screenshot-grounded VisualCritic evidence passed the mapped requirement policy without a blocking category.",
        )

    def _browser_result(
        self,
        rule: RequirementDefinition,
        browser: BrowserQAResult | None,
        browser_path: Path | None,
        *,
        run_id: str,
        project_digest: str,
    ) -> RequirementResult:
        if browser is None or browser_path is None:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.UNTESTED,
                applicable=None,
                rationale="No BrowserQA artifact was supplied.",
            )
        evidence = [self._evidence_ref(browser_path, run_id=run_id, project_digest=project_digest, kind="browser-report")]
        if rule.evaluator == "browser_target_smoke":
            passed = browser.gates.control_target_smoke_passed
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if passed else EvidenceOutcome.FAILED,
                applicable=True,
                evidence=evidence,
                rationale="Advanced BrowserQA control-target smoke gate " + ("passed." if passed else "failed."),
            )
        if rule.evaluator == "browser_contrast_smoke":
            passed = browser.gates.elementary_visual_sanity_passed
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if passed else EvidenceOutcome.FAILED,
                applicable=True,
                evidence=evidence,
                rationale="Advanced BrowserQA catastrophic-contrast smoke gate " + ("passed." if passed else "failed."),
            )
        if rule.evaluator == "browser_viewports":
            names = {viewport.name for viewport in browser.viewports}
            required = {"desktop-1440", "tablet-768", "mobile-390"}
            passed = required.issubset(names) and browser.gates.screenshots_created
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.PASSED if passed else EvidenceOutcome.FAILED,
                applicable=True,
                evidence=evidence,
                rationale=("Representative desktop/tablet/mobile screenshots were captured." if passed else "Required representative viewport evidence is incomplete."),
            )
        return RequirementResult(
            requirement_id=rule.id,
            outcome=EvidenceOutcome.CANT_TELL,
            applicable=True,
            evidence=evidence,
            rationale="Browser evidence exists, but the dedicated evaluator for this requirement has not been implemented yet.",
        )

    def _reference_plan_result(
        self,
        rule: RequirementDefinition,
        run_dir: Path,
        *,
        run_id: str,
        project_digest: str,
    ) -> RequirementResult:
        path = run_dir / "reference-benchmark-plan.json"
        if not path.exists():
            return RequirementResult(requirement_id=rule.id, outcome=EvidenceOutcome.UNTESTED, applicable=True, rationale="reference-benchmark-plan.json is missing.")
        evidence = [self._evidence_ref(path, run_id=run_id, project_digest=project_digest, kind="reference-plan")]
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return RequirementResult(requirement_id=rule.id, outcome=EvidenceOutcome.FAILED, applicable=True, evidence=evidence, rationale="Reference plan is unreadable or invalid JSON.")
        website_type = str(payload.get("website_type", "")).strip()
        if website_type and website_type not in {"generic", "unknown"}:
            return RequirementResult(requirement_id=rule.id, outcome=EvidenceOutcome.PASSED, applicable=True, evidence=evidence, rationale=f"Website archetype resolved as {website_type!r}.")
        return RequirementResult(requirement_id=rule.id, outcome=EvidenceOutcome.CANT_TELL, applicable=True, evidence=evidence, rationale="Reference plan exists but does not resolve a specific website archetype.")

    def _artifact_claim_result(
        self,
        rule: RequirementDefinition,
        run_dir: Path,
        *,
        run_id: str,
        project_digest: str,
    ) -> RequirementResult:
        candidates = []
        for item in rule.required_evidence:
            if item.startswith(("browser ", "playwright ", "computed ", "interaction ", "blurred ", "style-", "reference comparison", "visual critique", "content-", "touch-", "motion ")):
                continue
            path = run_dir / item
            if path.exists() and path.is_file():
                candidates.append(self._evidence_ref(path, run_id=run_id, project_digest=project_digest, kind="artifact"))
        if not candidates:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.UNTESTED,
                applicable=None,
                rationale="No structured evidence artifact exists for this requirement.",
            )
        return RequirementResult(
            requirement_id=rule.id,
            outcome=EvidenceOutcome.CANT_TELL,
            applicable=True,
            evidence=candidates,
            rationale="Supporting artifact exists, but artifact presence alone is not proof that this subjective requirement passed.",
        )

    def _human_review_result(
        self,
        rule: RequirementDefinition,
        run_dir: Path,
        *,
        run_id: str,
        project_digest: str,
    ) -> RequirementResult:
        path = run_dir / "human-review.json"
        if not path.exists():
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.CANT_TELL,
                applicable=True,
                rationale="Independent human review has not been recorded yet.",
            )
        evidence = [self._evidence_ref(path, run_id=run_id, project_digest=project_digest, kind="human-review")]
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return RequirementResult(requirement_id=rule.id, outcome=EvidenceOutcome.FAILED, applicable=True, evidence=evidence, rationale="human-review.json is invalid.")
        approved = payload.get("approved") is True and bool(str(payload.get("reviewer", "")).strip())
        return RequirementResult(
            requirement_id=rule.id,
            outcome=EvidenceOutcome.PASSED if approved else EvidenceOutcome.FAILED,
            applicable=True,
            evidence=evidence,
            rationale=("Independent human review recorded approval." if approved else "Human review artifact exists but does not contain reviewer identity plus approved=true."),
        )

    def _dedicated_report_result(
        self,
        rule: RequirementDefinition,
        run_dir: Path,
        *,
        run_id: str,
        project_digest: str,
    ) -> RequirementResult:
        filename = self.DEDICATED_REPORTS.get(str(rule.evaluator or ""))
        if not filename:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.UNTESTED,
                applicable=None,
                rationale=f"No dedicated report mapping exists for evaluator {rule.evaluator!r}.",
            )
        path = run_dir / filename
        if not path.is_file():
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.UNTESTED,
                applicable=None,
                rationale=f"Dedicated evaluator report {filename} has not been generated.",
            )
        report_evidence = [self._evidence_ref(path, run_id=run_id, project_digest=project_digest, kind=str(rule.evaluator or "dedicated-evaluator"))]
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.FAILED,
                applicable=True,
                evidence=report_evidence,
                rationale=f"Dedicated evaluator report {filename} is invalid JSON.",
            )
        bound_digest = str(payload.get("project_digest", ""))
        if not bound_digest or bound_digest != project_digest:
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.UNTESTED,
                applicable=None,
                evidence=report_evidence,
                rationale="Dedicated evaluator evidence is stale or unbound to the current project digest.",
            )
        row = (payload.get("requirements") or {}).get(rule.id)
        if not isinstance(row, dict):
            return RequirementResult(
                requirement_id=rule.id,
                outcome=EvidenceOutcome.UNTESTED,
                applicable=None,
                evidence=report_evidence,
                rationale=f"Dedicated evaluator report does not contain a result for {rule.id}.",
            )
        try:
            outcome = EvidenceOutcome(str(row.get("outcome", "untested")))
        except ValueError:
            outcome = EvidenceOutcome.CANT_TELL
        evidence = list(report_evidence)
        for raw in row.get("evidence_files", []):
            candidate = Path(str(raw))
            if not candidate.is_absolute():
                candidate = run_dir / candidate
            candidate = candidate.resolve()
            if candidate.is_file():
                evidence.append(
                    self._evidence_ref(
                        candidate,
                        run_id=run_id,
                        project_digest=project_digest,
                        kind=f"{rule.evaluator}-artifact",
                    )
                )
        if outcome == EvidenceOutcome.PASSED and not evidence:
            outcome = EvidenceOutcome.CANT_TELL
        return RequirementResult(
            requirement_id=rule.id,
            outcome=outcome,
            applicable=row.get("applicable"),
            test_targets=[str(item) for item in row.get("test_targets", [])],
            evidence=evidence,
            rationale=str(row.get("rationale", "Dedicated evaluator returned no rationale.")),
        )

    def _stale_dedicated_report_count(self, run_dir: Path, project_digest: str) -> int:
        stale = 0
        for filename in set(self.DEDICATED_REPORTS.values()):
            path = run_dir / filename
            if not path.is_file():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if str(payload.get("project_digest", "")) != project_digest:
                stale += 1
        return stale

    def evaluate(
        self,
        *,
        run_id: str,
        run_dir: Path,
        project_dir: Path,
        browser_report_path: Path | None = None,
        visual_critic_path: Path | None = None,
    ) -> PrototypeAcceptanceReport:
        run_dir = Path(run_dir).resolve()
        project_dir = Path(project_dir).resolve()
        digest = self.project_digest(project_dir)

        browser = None
        browser_path = Path(browser_report_path).resolve() if browser_report_path else None
        if browser_path and browser_path.exists():
            browser = BrowserQAResult.model_validate_json(browser_path.read_text(encoding="utf-8"))

        critic = None
        critic_path = Path(visual_critic_path).resolve() if visual_critic_path else None
        if critic_path and critic_path.exists():
            critic = VisualCriticResult.model_validate_json(critic_path.read_text(encoding="utf-8"))

        results: list[RequirementResult] = []
        for rule in self.registry.rules:
            if rule.evaluator == "semantic_visual":
                result = self._semantic_result(rule, critic, critic_path, run_id=run_id, project_digest=digest)
            elif rule.evaluator in {"browser_target_smoke", "browser_contrast_smoke", "browser_viewports"}:
                result = self._browser_result(rule, browser, browser_path, run_id=run_id, project_digest=digest)
            elif rule.evaluator == "reference_plan":
                result = self._reference_plan_result(rule, run_dir, run_id=run_id, project_digest=digest)
            elif rule.evaluator == "artifact_claim":
                result = self._artifact_claim_result(rule, run_dir, run_id=run_id, project_digest=digest)
            elif rule.evaluator == "human_review":
                result = self._human_review_result(rule, run_dir, run_id=run_id, project_digest=digest)
            elif rule.evaluator in self.DEDICATED_REPORTS:
                result = self._dedicated_report_result(rule, run_dir, run_id=run_id, project_digest=digest)
            else:
                result = RequirementResult(
                    requirement_id=rule.id,
                    outcome=EvidenceOutcome.UNTESTED,
                    applicable=None,
                    rationale=f"Dedicated evaluator {rule.evaluator!r} has not been implemented yet.",
                )
            results.append(result)

        by_id = {rule.id: rule for rule in self.registry.rules}
        machine_blockers = sum(
            1
            for result in results
            if by_id[result.requirement_id].machine_gate
            and result.outcome not in {EvidenceOutcome.PASSED, EvidenceOutcome.INAPPLICABLE}
        )
        final_blockers = sum(
            1
            for result in results
            if by_id[result.requirement_id].final_gate
            and result.outcome not in {EvidenceOutcome.PASSED, EvidenceOutcome.INAPPLICABLE}
        )
        counts = {outcome: sum(result.outcome == outcome for result in results) for outcome in EvidenceOutcome}
        summary = EvidenceSummary(
            total=len(results),
            passed=counts[EvidenceOutcome.PASSED],
            failed=counts[EvidenceOutcome.FAILED],
            inapplicable=counts[EvidenceOutcome.INAPPLICABLE],
            cant_tell=counts[EvidenceOutcome.CANT_TELL],
            untested=counts[EvidenceOutcome.UNTESTED],
            machine_blockers=machine_blockers,
            final_blockers=final_blockers,
        )
        machine_status = "passed" if machine_blockers == 0 else "blocked"
        manual_pending = any(
            by_id[result.requirement_id].verification_mode.value == "manual"
            and result.outcome not in {EvidenceOutcome.PASSED, EvidenceOutcome.INAPPLICABLE}
            for result in results
        )
        final_status = (
            "blocked"
            if machine_status == "blocked"
            else ("human_review_required" if manual_pending else ("approved" if final_blockers == 0 else "blocked"))
        )
        stale_count = self._stale_dedicated_report_count(run_dir, digest)
        return PrototypeAcceptanceReport(
            registry_version=self.registry.version,
            run_id=run_id,
            project_dir=str(project_dir),
            project_digest=digest,
            generated_at=datetime.now(timezone.utc).isoformat(),
            requirements=results,
            summary=summary,
            machine_status=machine_status,
            final_status=final_status,
            stale_evidence_count=stale_count,
            limitations=[
                "Rules without dedicated evaluators remain untested; they are never auto-passed from prose or artifact presence.",
                "Manual human review remains cantTell until human-review.json is supplied.",
                "WCAG 2.2 AA target-size smoke remains a separate 24 CSS px check; the 44 CSS px evaluator is a preferred prototype quality gate.",
                "Blind five-second evidence is an AI screenshot-comprehension proxy, not participant usability research.",
            ],
        )
