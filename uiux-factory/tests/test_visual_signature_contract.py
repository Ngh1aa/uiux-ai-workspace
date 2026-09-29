from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "VISUAL-SIGNATURE-REGRESSION-CONTRACT.md"
CONTEXT = ROOT / "PROJECT-CONTEXT.template.md"
OWNERSHIP = ROOT / "docs" / "CONTRACT-OWNERSHIP.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_visual_signature_contract_exists_and_is_generic():
    text = read(CONTRACT)
    required = [
        "Representative page/route",
        "Signature media",
        "Signature motion",
        "Signature composition",
        "Page-role hierarchy",
        "Reduced-motion behavior",
        "Canonical owners",
        "Source-owner consistency scan",
        "content/evidence/metadata migration",
        "rendered evidence",
        "PROJECT_FIX_VERIFIED",
        "FACTORY_FIX_VERIFIED",
    ]
    for term in required:
        assert term in text, f"missing visual-signature contract term: {term}"

    # The Factory contract must stay archetype-generic rather than hard-code
    # the portfolio that exposed this class of regression.
    forbidden = ["DoAnhNghia_BAPortfolio", "DO ANH NGHIA", "avatar.webp"]
    for term in forbidden:
        assert term not in text, f"project-specific leakage in generic contract: {term}"


def test_new_project_context_captures_signature_invariants():
    text = read(CONTEXT)
    required = [
        "### Visual signature compatibility",
        "Representative page / route",
        "Signature media",
        "Signature motion / interaction",
        "Signature composition / art-direction cue",
        "Page-role hierarchy to preserve",
        "Reduced-motion identity that must remain",
        "Canonical DOM/component owner",
        "Canonical style owner",
        "Canonical behavior owner",
        "Known stale / parallel visual owners",
        "Baseline rendered evidence",
        "Post-change evidence required",
        "Explicitly allowed signature changes for this task",
        "Required visual-signature regression verification",
    ]
    for term in required:
        assert term in text, f"new-project context lost signature invariant field: {term}"


def test_contract_ownership_routes_rendered_migrations_to_signature_contract():
    text = read(OWNERSHIP)
    assert "Visual-signature compatibility during non-redesign migrations" in text
    assert "docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md" in text
    assert "content/evidence migration" in text
    assert "Home/top-of-page composition" in text
