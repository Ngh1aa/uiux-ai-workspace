from pathlib import Path

from core.contracts.prototype_acceptance_schema import RequirementResult
from core.verification.evidence_provenance import project_digest
from core.verification.prototype_checklist_registry import prototype_requirements


def test_registry_contains_exactly_56_unique_requirements():
    requirements = prototype_requirements()
    assert len(requirements) == 56
    assert len({item.id for item in requirements}) == 56
    counts = {stage: sum(item.stage == stage for item in requirements) for stage in range(1, 8)}
    assert counts == {1: 9, 2: 10, 3: 14, 4: 7, 5: 4, 6: 4, 7: 8}


def test_manual_human_requirements_are_not_machine_required():
    by_id = {item.id: item for item in prototype_requirements()}
    for requirement_id in ("P7-02", "P7-08"):
        item = by_id[requirement_id]
        assert item.automation_status == "manual"
        assert item.verification_mode == "manual"
        assert item.machine_required is False
        assert item.final_required is True


def test_implemented_requirements_are_explicit_machine_gates():
    implemented = [item for item in prototype_requirements() if item.automation_status == "implemented"]
    assert {item.id for item in implemented} == {
        "P1-03", "P1-06", "P2-06", "P3-08", "P3-11", "P3-13", "P3-14", "P6-02"
    }
    assert all(item.machine_required for item in implemented)


def test_outcome_contract_keeps_uncertainty_distinct():
    assert RequirementResult(requirement_id="P7-02", outcome="cantTell", rationale="human required").outcome == "cantTell"
    assert RequirementResult(requirement_id="P4-02", outcome="untested", rationale="crawler not run").outcome == "untested"
    assert RequirementResult(requirement_id="P5-02", outcome="inapplicable", rationale="no list surface").outcome == "inapplicable"


def test_project_digest_changes_when_project_changes(tmp_path: Path):
    project = tmp_path / "site"
    project.mkdir()
    (project / "index.html").write_text("<main>A</main>", encoding="utf-8")
    first = project_digest(project)
    (project / "index.html").write_text("<main>B</main>", encoding="utf-8")
    second = project_digest(project)
    assert first != second
