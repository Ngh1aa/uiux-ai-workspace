from __future__ import annotations

from pathlib import Path

from core.dogfood.p174_policy_drift import build_policy_drift_matrix
from core.runtime.flow_os.repository_policy_drift import inspect_repository_policy_drift
from core.runtime.flow_os.repository_policy_registry import registered_repository_policies, resolve_repository_policy


def _write(root: Path, relative: str, content: str = "{}\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_registry_freshness_rules_cover_every_registered_provider() -> None:
    allowed_channels = {"repository-static", "external-observed"}
    for policy in registered_repository_policies():
        rules = {rule.provider: rule for rule in policy.integration_freshness}
        assert set(rules) == set(policy.known_integration_providers)
        assert all(rule.evidence_channels for rule in rules.values())
        assert all(set(rule.evidence_channels).issubset(allowed_channels) for rule in rules.values())


def test_monitor_matrix_is_derived_from_registry_without_duplicate_target_list() -> None:
    matrix = build_policy_drift_matrix()
    repositories = [item["repository"] for item in matrix["include"]]
    assert repositories == [policy.repository for policy in registered_repository_policies()]
    assert len(repositories) == len(set(repositories))


def test_static_lane_is_in_sync_but_partial_for_external_only_pages(tmp_path: Path) -> None:
    _write(tmp_path, "vercel.json")
    assessment = inspect_repository_policy_drift("Ngh1aa/Nova", tmp_path)

    assert assessment.status == "IN_SYNC"
    assert assessment.in_sync is True
    assert assessment.coverage_complete is False
    assert assessment.inspection_channels == ("repository-static",)
    assert assessment.detected_providers == ("vercel",)
    assert assessment.registered_providers == ("github-pages", "vercel")
    assert assessment.unresolved_providers == ("github-pages",)
    assert assessment.removed_providers == ()


def test_static_required_vercel_removal_is_still_detected_with_external_only_pages(tmp_path: Path) -> None:
    assessment = inspect_repository_policy_drift("Ngh1aa/Nova", tmp_path)

    assert assessment.status == "DRIFT_REMOVED_PROVIDER"
    assert assessment.in_sync is False
    assert assessment.removed_providers == ("vercel",)
    assert assessment.unresolved_providers == ("github-pages",)


def test_added_netlify_provider_is_detected_without_registry_change(tmp_path: Path) -> None:
    _write(tmp_path, "vercel.json")
    _write(tmp_path, "netlify.toml", "[build]\n  publish = '.'\n")
    assessment = inspect_repository_policy_drift("Ngh1aa/Nova", tmp_path)

    assert assessment.status == "DRIFT_ADDED_PROVIDER"
    assert assessment.in_sync is False
    assert assessment.added_providers == ("netlify",)
    assert assessment.unresolved_providers == ("github-pages",)


def test_lumen_static_lane_has_complete_coverage(tmp_path: Path) -> None:
    _write(tmp_path, "vercel.json")
    _write(
        tmp_path,
        ".github/workflows/pages.yml",
        "name: pages\nsteps:\n  - uses: actions/deploy-pages@v4\n",
    )
    assessment = inspect_repository_policy_drift("Ngh1aa/Lumen", tmp_path)

    assert assessment.status == "IN_SYNC"
    assert assessment.coverage_complete is True
    assert assessment.unresolved_providers == ()
    assert set(assessment.detected_providers) == {"github-pages", "vercel"}

    (tmp_path / ".github/workflows/pages.yml").unlink()
    drift = inspect_repository_policy_drift("Ngh1aa/Lumen", tmp_path)
    assert drift.status == "DRIFT_REMOVED_PROVIDER"
    assert drift.removed_providers == ("github-pages",)


def test_add_and_remove_can_be_reported_in_same_static_scan(tmp_path: Path) -> None:
    _write(tmp_path, "render.yaml", "services: []\n")
    assessment = inspect_repository_policy_drift("Ngh1aa/Nova", tmp_path)

    assert assessment.status == "DRIFT_ADDED_AND_REMOVED_PROVIDER"
    assert assessment.added_providers == ("render",)
    assert assessment.removed_providers == ("vercel",)
    assert assessment.unresolved_providers == ("github-pages",)


def test_missing_checkout_is_unknown_not_false_removed() -> None:
    assessment = inspect_repository_policy_drift("Ngh1aa/Nova", "/path/that/does/not/exist")
    assert assessment.status == "UNKNOWN_POLICY_DRIFT"
    assert assessment.inspection_complete is False
    assert assessment.in_sync is False


def test_registry_preview_authority_is_not_changed_by_external_pages_freshness() -> None:
    nova = resolve_repository_policy("Ngh1aa/Nova")
    rules = {rule.provider: rule.evidence_channels for rule in nova.integration_freshness}

    assert nova.preview_policy == "pr-preview-allowed"
    assert nova.allowed_preview_providers == ("vercel",)
    assert nova.known_integration_providers == ("vercel", "github-pages")
    assert rules == {
        "vercel": ("repository-static",),
        "github-pages": ("external-observed",),
    }
    assert nova.mutation_scope == ("branch-create", "branch-push", "pr-create", "pr-update")
    assert nova.release_boundary.allow_merge is False
    assert nova.release_boundary.allow_production_deploy is False
    assert nova.release_boundary.allow_release is False
