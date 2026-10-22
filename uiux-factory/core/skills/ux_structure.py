"""Validate UX structure records (ux-structure-and-flow-design, U1 to U6).

Checks structural completeness and honest labelling. It never proves usability,
participant behaviour or the order in which work actually happened.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from core.runtime.flow_os.safe_read import SafeReader
from core.skills.design_decisions import StrictModel

EvidenceLabel = Literal["EVIDENCED", "HYPOTHESIS", "UNKNOWN"]
ReviewSource = Literal["agent-heuristic", "human"]
NavModel = Literal["tab-bar", "top-nav", "hub-primary-action", "stepper", "hierarchy-search", "contextual", "hybrid"]
Verdict = Literal["READY", "READY_WITH_RISKS", "NOT_READY"]

STEP_BUDGET = 7
MIN_SCENARIOS = 5
MAX_CONTRACT_CHARS = 512_000


def _nonblank(*values: str) -> bool:
    return all(isinstance(value, str) and value.strip() for value in values)


class Labelled(StrictModel):
    text: str = Field(min_length=1, max_length=2000)
    label: EvidenceLabel
    evidence_ref: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def evidenced_needs_ref(self):
        if not self.text.strip():
            raise ValueError("labelled fields must not be whitespace")
        if self.label == "EVIDENCED" and not (self.evidence_ref or "").strip():
            raise ValueError(f"EVIDENCED input needs evidence_ref: {self.text[:60]!r}")
        return self


class Problem(StrictModel):
    statement: Labelled
    outcome_metric: str = Field(min_length=1, max_length=1000, description="metric or the literal UNKNOWN")


class TopTask(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    task: str = Field(min_length=1, max_length=500)
    job: str = Field(min_length=1, max_length=1000, description="When <situation>, I want to <motivation>, so I can <outcome>.")
    frequency: int = Field(ge=1, le=4, description="rare 1, monthly 2, weekly 3, daily 4")
    consequence: int = Field(ge=1, le=3, description="low 1, medium 2, high 3")
    scenario: str = Field(min_length=1, max_length=1000)
    success_signal: str = Field(min_length=1, max_length=500)
    label: EvidenceLabel

    @property
    def score(self) -> int:
        return self.frequency * self.consequence


class FailurePath(StrictModel):
    trigger: str = Field(min_length=1, max_length=500)
    recovery: str = Field(min_length=1, max_length=1000)
    keeps_user_input: bool
    returns_to: str = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def concrete(self):
        if not _nonblank(self.trigger, self.recovery, self.returns_to):
            raise ValueError("failure paths need a concrete trigger, recovery and return point")
        return self


class Flow(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    task_id: str
    entry_points: list[str] = Field(min_length=1, max_length=10)
    happy_path: list[str] = Field(min_length=2, max_length=40, description="ordered screen ids or step names")
    alternative_paths: list[list[str]] = Field(default_factory=list, max_length=10)
    failure_paths: list[FailurePath] = Field(min_length=1, max_length=20)
    over_budget_reason: str | None = Field(default=None, min_length=1, max_length=1000)
    diagram_ref: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def budget(self):
        if len(self.happy_path) > STEP_BUDGET and not (self.over_budget_reason or "").strip():
            raise ValueError(
                f"flow {self.id}: happy path has {len(self.happy_path)} steps (> {STEP_BUDGET}); "
                "simplify or record over_budget_reason")
        return self


class Screen(StrictModel):
    """Field names match visual-design-direction pages[].ux so records can be exported."""
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,60}$")
    route: str = Field(min_length=1, max_length=500)
    flows: list[str] = Field(min_length=1, max_length=20)
    entry_state: str = Field(min_length=1, max_length=1000)
    user_goal: str = Field(min_length=1, max_length=1000, description="the user question on arrival, in their words")
    information_priority: list[str] = Field(min_length=1, max_length=12)
    primary_action: str = Field(min_length=1, max_length=300)
    destination: str = Field(min_length=1, max_length=1000)
    feedback: str = Field(min_length=1, max_length=1000)
    recovery: str = Field(min_length=1, max_length=1000)
    required_states: list[str] = Field(min_length=1, max_length=20)
    walkthrough_observation: str | None = Field(default=None, min_length=1, max_length=3000)

    @model_validator(mode="after")
    def concrete(self):
        if not _nonblank(self.entry_state, self.user_goal, self.primary_action, self.destination,
                         self.feedback, self.recovery, *self.information_priority, *self.required_states):
            raise ValueError(f"screen {self.id}: fields must describe concrete decisions, not whitespace")
        return self


class Navigation(StrictModel):
    model: NavModel
    reason: str = Field(min_length=1, max_length=1500)
    persistent: list[str] = Field(default_factory=list, max_length=8)
    hidden: list[str] = Field(default_factory=list, max_length=30)


class Scenario(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    description: str = Field(min_length=1, max_length=1000)
    varies: list[Literal["first-time", "returning", "hurried", "failure", "accessibility", "situational", "edge-content", "interruption", "low-confidence"]] = Field(min_length=1, max_length=6)


class Finding(StrictModel):
    """Unlike pages[].ux findings, an open blocker is representable here: it yields NOT_READY."""
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    screen_id: str
    scenario_ids: list[str] = Field(min_length=1, max_length=10)
    observation: str = Field(min_length=1, max_length=2000)
    severity: Literal["blocker", "major", "minor"]
    status: Literal["open", "resolved"]
    fix: str = Field(min_length=1, max_length=2000)
    retest: str | None = Field(default=None, min_length=1, max_length=2000)

    @model_validator(mode="after")
    def retested(self):
        if self.status == "resolved" and not (self.retest or "").strip():
            raise ValueError(f"finding {self.id}: resolved findings need a concrete retest observation")
        return self


class Walkthrough(StrictModel):
    review_source: ReviewSource
    scenarios: list[Scenario] = Field(min_length=1, max_length=12)
    findings: list[Finding] = Field(default_factory=list, max_length=200)


class VerdictRecord(StrictModel):
    status: Verdict
    open_majors: list[str] = Field(default_factory=list, max_length=50, description="finding ids")
    hypotheses_to_validate: list[str] = Field(default_factory=list, max_length=30)
    next_validation: str = Field(min_length=1, max_length=1000)


class UXStructure(StrictModel):
    schema_version: Literal["1.0"]
    product: str = Field(min_length=1, max_length=300)
    problem: Problem
    audiences: list[Labelled] = Field(min_length=1, max_length=6)
    top_tasks: list[TopTask] = Field(min_length=1, max_length=12)
    flows: list[Flow] = Field(min_length=1, max_length=40)
    screens: list[Screen] = Field(min_length=1, max_length=100)
    navigation: Navigation
    walkthrough: Walkthrough
    verdict: VerdictRecord

    @model_validator(mode="after")
    def unique_ids(self):
        for name, items in (("top_tasks", self.top_tasks), ("flows", self.flows), ("screens", self.screens),
                            ("scenarios", self.walkthrough.scenarios), ("findings", self.walkthrough.findings)):
            ids = [item.id for item in items]
            if len(ids) != len(set(ids)):
                raise ValueError(f"{name} ids must be unique")
        return self


def _cross_checks(doc: UXStructure) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    task_ids = {task.id for task in doc.top_tasks}
    flow_ids = {flow.id for flow in doc.flows}
    screen_ids = {screen.id for screen in doc.screens}
    scenario_ids = {scenario.id for scenario in doc.walkthrough.scenarios}

    for flow in doc.flows:
        if flow.task_id not in task_ids:
            errors.append(f"flow {flow.id}: unknown task_id {flow.task_id}")
        lost = [path.trigger for path in flow.failure_paths if not path.keeps_user_input]
        if lost:
            warnings.append(f"flow {flow.id}: failure paths lose user input ({'; '.join(lost)}); justify or fix")
    covered = {flow.task_id for flow in doc.flows}
    for task in doc.top_tasks:
        if task.id not in covered:
            errors.append(f"top task {task.id} has no flow")

    referenced_flows: set[str] = set()
    for screen in doc.screens:
        unknown = set(screen.flows) - flow_ids
        if unknown:
            errors.append(f"screen {screen.id}: unknown flows {sorted(unknown)}")
        referenced_flows.update(screen.flows)
    for flow_id in sorted(flow_ids - referenced_flows):
        errors.append(f"flow {flow_id} has no screen in the inventory")

    if len(scenario_ids) < MIN_SCENARIOS:
        errors.append(f"walkthrough needs at least {MIN_SCENARIOS} distinct scenarios; found {len(scenario_ids)}")
    varied = {kind for scenario in doc.walkthrough.scenarios for kind in scenario.varies}
    if "failure" not in varied:
        errors.append("at least one walkthrough scenario must exercise a failure path")
    if len(varied) < 3:
        warnings.append("walkthrough scenarios vary on fewer than 3 dimensions; they may repeat the same lens")

    open_blockers, open_majors = [], []
    for finding in doc.walkthrough.findings:
        if finding.screen_id not in screen_ids:
            errors.append(f"finding {finding.id}: unknown screen {finding.screen_id}")
        missing = set(finding.scenario_ids) - scenario_ids
        if missing:
            errors.append(f"finding {finding.id}: unknown scenarios {sorted(missing)}")
        if finding.status == "open" and finding.severity == "blocker":
            open_blockers.append(finding.id)
        if finding.status == "open" and finding.severity == "major":
            open_majors.append(finding.id)

    status = doc.verdict.status
    hypotheses = [task.id for task in doc.top_tasks if task.label != "EVIDENCED"]
    hypotheses += [a.text[:40] for a in doc.audiences if a.label != "EVIDENCED"]
    if open_blockers and status != "NOT_READY":
        errors.append(f"verdict {status} contradicts open blockers {open_blockers}; verdict must be NOT_READY")
    if status == "READY" and (open_majors or hypotheses):
        errors.append("READY requires no open majors and only EVIDENCED tasks/audiences; use READY_WITH_RISKS")
    if status == "READY_WITH_RISKS":
        unlisted = sorted(set(open_majors) - set(doc.verdict.open_majors))
        if unlisted:
            errors.append(f"READY_WITH_RISKS must list open majors {unlisted} in verdict.open_majors")
        if hypotheses and not doc.verdict.hypotheses_to_validate:
            errors.append("READY_WITH_RISKS with HYPOTHESIS/UNKNOWN inputs must name hypotheses_to_validate")
    if not open_blockers and status == "NOT_READY":
        warnings.append("verdict NOT_READY without an open blocker; record the reason in next_validation")

    if doc.problem.outcome_metric.strip().upper() == "UNKNOWN":
        warnings.append("outcome metric is UNKNOWN; success cannot be measured yet")
    if doc.walkthrough.review_source == "agent-heuristic":
        warnings.append("walkthrough is agent-heuristic evidence, not participant research")
    if len(doc.navigation.persistent) > 5:
        warnings.append("more than 5 persistent navigation destinations")
    hidden = {item.casefold().strip() for item in doc.navigation.hidden}
    top3 = sorted(doc.top_tasks, key=lambda t: t.score, reverse=True)[:3]
    buried = sorted(t.id for t in top3 if t.id.casefold() in hidden or t.task.casefold().strip() in hidden)
    if buried:
        errors.append(f"top tasks hidden in navigation: {buried}")
    return errors, warnings


def check_ux_structure(data: dict) -> dict:
    try:
        doc = UXStructure.model_validate(data)
    except ValidationError as exc:
        errors = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()]
        return {"status": "FAIL", "returncode": 1, "verdict": "UNKNOWN", "errors": errors,
                "warnings": [], "usability": "UNKNOWN"}
    errors, warnings = _cross_checks(doc)
    gate_open = not errors and doc.verdict.status in ("READY", "READY_WITH_RISKS")
    return {
        "status": "PASS" if gate_open else "FAIL",
        "returncode": 0 if gate_open else 1,
        "verdict": doc.verdict.status,
        "errors": errors if errors or gate_open else ["verdict NOT_READY: visual direction must not start"],
        "warnings": warnings,
        "coverage": {
            "top_tasks": len(doc.top_tasks),
            "flows": len(doc.flows),
            "failure_paths": sum(len(flow.failure_paths) for flow in doc.flows),
            "screens": len(doc.screens),
            "scenarios": len(doc.walkthrough.scenarios),
            "findings_open": sum(1 for f in doc.walkthrough.findings if f.status == "open"),
        },
        "review_source": doc.walkthrough.review_source,
        "usability": "UNKNOWN",
    }


def export_page_ux(data: dict, evidence_ref: str) -> list[dict]:
    """Project screens into pages[].ux blocks for the visual decision contract.

    Refuses unless the structure gate passes, so an open blocker can never be carried forward.
    """
    result = check_ux_structure(data)
    if result["status"] != "PASS":
        raise ValueError("ux structure gate must PASS before export: " + "; ".join(result["errors"]))
    doc = UXStructure.model_validate(data)
    by_screen: dict[str, list[dict]] = {}
    for finding in doc.walkthrough.findings:
        item = {"observation": finding.observation, "severity": finding.severity, "status": finding.status}
        if finding.retest:
            item["retest"] = finding.retest
        by_screen.setdefault(finding.screen_id, []).append(item)
    out = []
    for screen in doc.screens:
        out.append({"route": screen.route, "ux": {
            "entry_state": screen.entry_state,
            "user_goal": screen.user_goal,
            "information_priority": screen.information_priority,
            "primary_action": screen.primary_action,
            "destination": screen.destination,
            "feedback": screen.feedback,
            "recovery": screen.recovery,
            "walkthrough_observation": screen.walkthrough_observation or "No screen-level observation recorded; see findings.",
            "evidence_ref": evidence_ref,
            "review_source": doc.walkthrough.review_source,
            "findings": by_screen.get(screen.id, []),
        }})
    return out


def check_ux_structure_file(project_root: Path, relative_path: str) -> dict:
    root = Path(project_root).resolve()
    loaded = SafeReader(root).read_text(relative_path)
    if len(loaded.content) > MAX_CONTRACT_CHARS:
        raise ValueError(f"ux structure record exceeds {MAX_CONTRACT_CHARS} chars")
    result = check_ux_structure(json.loads(loaded.content))
    result["path"] = relative_path
    result["artifact_sha256"] = "sha256:" + sha256(loaded.path.read_bytes()).hexdigest()
    return result
