from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent


def test_public_flow_os_docs_use_real_repo_root_paths() -> None:
    doc = (WORKSPACE / "skills_UIUX" / "FLOW-AGENT-OS.md").read_text(encoding="utf-8")
    assert "python -B skills_UIUX/scripts/uiux-agent.py" in doc
    assert "python -B skills_UIUX/scripts/validate-flows.py" in doc
    assert "python -B skills_UIUX/scripts/validate-runtime-foundation.py" in doc
    assert ".github/workflows/flow-os-validate.yml" not in doc
    assert ".github/workflows/uiux-factory-ci.yml" in doc


def test_managed_cli_documents_and_exposes_lifecycle_overrides() -> None:
    cli = (WORKSPACE / "skills_UIUX" / "scripts" / "uiux-agent.py").read_text(encoding="utf-8")
    readme = (WORKSPACE / "README.md").read_text(encoding="utf-8")

    for flag in ("--domain", "--product-archetype", "--validation-lane"):
        assert flag in cli
        assert flag in readme


def test_cloud_qa_external_defaults_do_not_point_at_internal_fixture() -> None:
    workflow = (WORKSPACE / ".github" / "workflows" / "cloud-qa-toolchain.yml").read_text(
        encoding="utf-8"
    )

    assert "run: npm ci --no-audit --no-fund" in workflow
    assert 'export QA_ROUTES="${INPUT_ROUTES:-/}"' in workflow
    assert 'TARGET_RELATIVE="uiux-factory/qa"' in workflow
    assert 'export QA_ROUTES="${INPUT_ROUTES:-/fixture/,/fixture/index.html}"' in workflow
    assert 'INPUT_TARGET_DIR: ${{ github.event.inputs.target_dir || \'\' }}' in workflow
    assert 'INPUT_ROUTES: ${{ github.event.inputs.routes || \'\' }}' in workflow
