"""Exercise the public adapter, not a substituted retrieval fixture."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUERY = ROOT / "skills_UIUX/design-intelligence-retrieval/scripts/query.py"


def query(*args):
    result = subprocess.run([sys.executable, "-B", str(QUERY), *args], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_unknown_industrial_profile_exposes_fallback_in_text():
    output = query("industrial automation engineering technical services", "--design-system")
    assert "NO_VERIFIED_PRODUCT_MATCH" in output
    assert "Government Portal / Civic Services" in output
    assert "ADOPT / ADAPT / REJECT" in output


def test_json_retains_upstream_payload_and_adds_review_boundary():
    payload = json.loads(query("industrial automation engineering technical services", "--design-system", "--json"))
    assert payload["design_system"]["reasoning_default"] is True
    assert payload["design_system"]["source_identities"]["product"] is None
    assert payload["factory_retrieval_review"]["status"] == "NO_VERIFIED_PRODUCT_MATCH"
    assert "persistence" in payload
    assert payload["factory_retrieval_review"]["adopted"] is False


def test_known_profile_does_not_report_missing_product():
    payload = json.loads(query("Government Portal / Civic Services", "--design-system", "--json"))
    assert payload["factory_retrieval_review"]["status"] == "MATCHED_CANDIDATE"
    assert payload["factory_retrieval_review"]["adopted"] is False


def test_focused_search_keeps_its_existing_json_contract():
    payload = json.loads(query("technical documentation mono", "--domain", "typography", "--json"))
    assert payload["domain"] == "typography"
    assert payload["count"] > 0
    assert "factory_retrieval_review" not in payload


def test_density_and_persistence_are_not_lost(tmp_path):
    args = ("Government Portal / Civic Services", "--design-system", "--density", "8", "--persist", "--output-dir", str(tmp_path), "--project-name", "Test candidate", "--json")
    first = json.loads(query(*args))
    assert first["design_system"]["spacing_scale"]["md"] == "8px"
    assert first["persistence"]["created_files"]
    saved = next(tmp_path.rglob("MASTER.md"))
    before = saved.read_bytes()
    second = json.loads(query(*args))
    assert second["persistence"]["status"] == "skipped_exists"
    assert saved.read_bytes() == before


def test_markdown_also_exposes_review_boundary():
    output = query("industrial automation engineering technical services", "--design-system", "--format", "markdown")
    assert "NO_VERIFIED_PRODUCT_MATCH" in output
    assert "### Pattern" in output


def test_invalid_cli_options_still_fail():
    result = subprocess.run([sys.executable, "-B", str(QUERY), "SaaS", "--design-system", "--density", "99"], capture_output=True)
    assert result.returncode != 0
