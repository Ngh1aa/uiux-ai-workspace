from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.provider_parity_regression import (
    evaluate_provider_parity_benchmark,
    load_provider_parity_benchmark,
)
from core.dogfood.cross_project import project_ids
from core.runtime.flow_os.flow import FlowPlanner


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
CORPUS = ROOT / "benchmarks/provider-parity-v1.json"
POLICY = SKILLS / "runtime/runtime-policy.json"


def _planner() -> FlowPlanner:
    return FlowPlanner(SKILLS, json.loads(POLICY.read_text(encoding="utf-8")))


def test_a48_provider_parity_corpus_declares_non_product_evidence_scope() -> None:
    payload = load_provider_parity_benchmark(CORPUS)

    assert payload["scope"] == "offline_contract_parity_not_live_provider_or_product_evidence"
    assert len(payload["cases"]) >= 8


def test_a48_provider_parity_smoke_covers_every_registered_real_project_profile() -> None:
    payload = load_provider_parity_benchmark(CORPUS)
    covered = {str(item["project_id"]) for item in payload["project_smokes"]}

    assert covered == set(project_ids())


def test_a48_provider_parity_benchmark_passes_all_contract_and_project_smoke_cases() -> None:
    results = evaluate_provider_parity_benchmark(
        CORPUS,
        factory_root=ROOT,
        planner=_planner(),
    )

    failures = [result for result in results if not result.passed]
    assert not failures, [(item.case_id, item.detail) for item in failures]
    assert {item.kind for item in results} == {
        "contract",
        "provider_contract",
        "project_profile_smoke",
    }


def test_a48_project_smoke_never_labels_fixture_output_as_product_evidence() -> None:
    results = evaluate_provider_parity_benchmark(
        CORPUS,
        factory_root=ROOT,
        planner=_planner(),
    )

    project_results = [item for item in results if item.kind == "project_profile_smoke"]
    assert project_results
    assert all("not product evidence" in item.detail for item in project_results)
