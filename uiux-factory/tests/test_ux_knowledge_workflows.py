"""Check bounded retrieval and cross-resource contracts, not aesthetic quality."""
import json
from pathlib import Path

import pytest

from core.skills.design_knowledge import retrieve_design_knowledge

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills_UIUX"
DATA = SKILLS / "visual-design-direction/data"
KNOWLEDGE = json.loads((DATA / "design-knowledge.json").read_text(encoding="utf-8"))
WORKFLOWS = json.loads((DATA / "domain-workflows.json").read_text(encoding="utf-8"))
ANATOMIES = json.loads((DATA / "reference-anatomies.json").read_text(encoding="utf-8"))
CASES = json.loads((SKILLS / "visual-design-direction/examples/decision-lab/cases.json").read_text(encoding="utf-8"))
LOOKUPS = [(profile, role) for profile in KNOWLEDGE["domain_profiles"] for role in profile["role_ids"]]


@pytest.mark.parametrize("profile,role", LOOKUPS, ids=[p["id"] + ":" + r for p, r in LOOKUPS])
def test_each_declared_domain_role_has_scoped_workflow_and_traceable_anatomy(profile, role):
    context = {key: values[0] for key, values in profile["match"].items()}
    result = retrieve_design_knowledge(SKILLS, context, role)
    workflow = result["domain_workflow"]
    assert workflow["status"] == "CONTEXT_MATCHED_CANDIDATES"
    assert len(workflow["profiles"]) == 1
    record = workflow["profiles"][0]
    assert record["profile_id"] == profile["id"]
    assert record["page_task"] == WORKFLOWS["profiles"][profile["id"]]["role_tasks"][role]
    assert "role_tasks" not in record  # Other roles do not enter active context.
    assert all(item["definition"] and item["guardrail"] for item in record["metrics"])
    assert record["actors"] and record["state_model"] and record["failure_and_recovery"]
    assert all((ROOT / source).is_file() for source in record["source_refs"])
    assert workflow["adopted"] is False
    assert result["reference_anatomy"]["status"] == "CONTEXT_MATCHED_CANDIDATES"
    assert result["aesthetic_quality"] == "UNKNOWN"


def test_no_role_no_deep_context_and_unknown_identity_gets_no_domain_workflow():
    context = {"website_type": "healthcare", "domain": "healthcare"}
    initial = retrieve_design_knowledge(SKILLS, context)
    assert initial["domain_workflow"]["status"] == "ROLE_NOT_REQUESTED"
    assert initial["domain_workflow"]["profiles"] == []
    unknown = retrieve_design_knowledge(SKILLS, {"domain": "aquaculture"}, "orientation")
    assert unknown["domain_workflow"]["status"] == "NO_CURATED_DOMAIN_PROFILE"
    assert unknown["domain_workflow"]["profiles"] == []
    unsupported = retrieve_design_knowledge(SKILLS, context, "catalog")
    assert unsupported["domain_workflow"]["status"] == "ROLE_NOT_SUPPORTED_FOR_DOMAIN"
    assert unsupported["reference_anatomy"]["cards"] == []


def test_resource_graph_has_no_orphan_duplicate_or_unlabelled_reference():
    pairs = [(card["profile_id"], card["page_role"]) for card in ANATOMIES["cards"]]
    assert len(pairs) == len(set(pairs))
    assert set(pairs) == {(p["id"], role) for p, role in LOOKUPS}
    assert set(WORKFLOWS["profiles"]) == {p["id"] for p in KNOWLEDGE["domain_profiles"]}
    for card in ANATOMIES["cards"]:
        for source_id in card["reference_ids"]:
            source = ANATOMIES["sources"][source_id]
            assert source["boundary"] and source["human_usability"] == "UNKNOWN"
            if not source["url"].startswith("https://"):
                assert (ROOT / source["url"]).is_file()
    for case in CASES["cases"].values():
        assert case["profile_id"] in WORKFLOWS["profiles"]
        assert set(case["roles"]) <= set(WORKFLOWS["profiles"][case["profile_id"]]["role_tasks"])
        assert case["facts"] and case["annotations"] and case["do_not_transfer"]
        assert all(note["observation"] and note["change"] and note["trade_off"] for note in case["annotations"])
