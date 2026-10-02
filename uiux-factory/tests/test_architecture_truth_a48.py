from __future__ import annotations

from pathlib import Path


FACTORY = Path(__file__).resolve().parents[1]
ARCH = FACTORY / "docs" / "architecture"
README = ARCH / "README.md"
RUNTIME_MAP = ARCH / "CURRENT-RUNTIME-MAP.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_a48_architecture_index_includes_current_a46_a47_a48_truth_docs() -> None:
    text = _read(README)
    required = (
        "A46-TYPED-BRAIN-MEMORY.md",
        "A46-MEMORY-RECALL-CONTEXT.md",
        "A46-MEMORY-BOUNDARY-BENCHMARK.md",
        "A47-BRAIN-SCORECARD.md",
        "A47-SCORECARD-BENCHMARK.md",
        "A48-ARCHITECTURE-TRUTH-RECONCILIATION.md",
    )
    for filename in required:
        assert filename in text
        assert (ARCH / filename).exists(), filename


def test_a48_runtime_map_names_implemented_brain_owners() -> None:
    text = _read(RUNTIME_MAP)
    required = (
        "core/brain_os/contracts.py",
        "core/brain_os/reasoning/evidence_graph.py",
        "core/brain_os/critics/",
        "core/brain_os/repair_orchestrator.py",
        "core/brain_os/memory_contracts.py",
        "core/memory/brain_memory.py",
        "core/brain_os/adapters/memory_context.py",
        "core/brain_os/scorecard.py",
    )
    for owner in required:
        assert owner in text


def test_a48_runtime_map_rejects_resolved_stale_not_implemented_claims() -> None:
    text = _read(RUNTIME_MAP)
    stale = (
        "Brain OS reasoning/control layer | not implemented",
        "Unified multi-critic orchestrator | not implemented",
        "Unified Brain benchmark scorecard | not implemented",
        "Semantic design rationale, hypothesis/decision memory and generalized knowledge retrieval remain future Brain OS capabilities",
        "repository does **not** yet have the proposed unified Brain OS Critique Orchestrator",
    )
    for claim in stale:
        assert claim not in text


def test_a48_canonical_runtime_and_evidence_owners_remain_explicit() -> None:
    readme = _read(README)
    runtime_map = _read(RUNTIME_MAP)
    for text in (readme, runtime_map):
        assert "core/runtime/flow_os/" in text
        assert "core/evaluation/run_evaluator.py" in text
        assert "core/runtime/flow_os/evidence.py" in text
    assert "skills_UIUX/" in runtime_map
    assert "uiux-factory/qa/" in runtime_map


def test_a48_remaining_provider_and_lifecycle_debt_is_not_hidden() -> None:
    text = _read(RUNTIME_MAP)
    assert "core/runtime/free_provider.py" in text
    assert "core/runtime/flow_os/provider*.py" in text
    assert "different provider entry/capability contracts" in text
    assert "distinct top-level lifecycle APIs" in text
    assert "not a second Flow OS" in text


def test_a48_reconciliation_does_not_modify_runtime_code() -> None:
    doc = _read(ARCH / "A48-ARCHITECTURE-TRUTH-RECONCILIATION.md")
    assert "documentation and documentation-truth tests only" in doc
    assert "does not:" in doc
    assert "change provider transport" in doc
    assert "change flow selection" in doc
    assert "change evidence or gate semantics" in doc
