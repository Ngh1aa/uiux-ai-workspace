from __future__ import annotations

import json
from pathlib import Path

import pytest

import core.dogfood.real_project as dogfood_module
from core.dogfood.real_project import RealProjectDogfoodRunner
from core.runtime.flow_os.browser_evidence import BrowserEvidenceError, PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.evidence import EvidenceRecord


REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY_ROOT = REPO_ROOT / "uiux-factory"
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _nova_fixture(root: Path) -> Path:
    project = root / "Nova"
    project.mkdir()
    (project / ".uiux-profile.json").write_text(
        json.dumps(
            {
                "project": "Nova — Personal Banking & Money Planning",
                "mode": "interactive_prototype",
                "request_type": "whole_product_redesign",
                "domain": "consumer_fintech_personal_banking",
                "responsive_scope": "responsive_all",
                "implementation": {
                    "stack": "static HTML/CSS/JavaScript",
                    "entry_points": ["index.html", "app.html", "prototype.html"],
                },
            }
        ),
        encoding="utf-8",
    )
    (project / "PROJECT-CONTEXT.md").write_text(
        "# Nova\n\nResponsive consumer-finance personal banking prototype.\n",
        encoding="utf-8",
    )
    for name in ("index.html", "app.html", "prototype.html"):
        (project / name).write_text("<!doctype html><main>Nova</main>\n", encoding="utf-8")
    workflow = project / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "nova-cloud-qa.yml").write_text(
        "steps:\n  - run: npm ci\n  - run: python .factory/uiux-factory/run.py qa --project-slug Nova\n",
        encoding="utf-8",
    )
    return project


class _FakeBrowser:
    def __init__(self, _qa_root: Path, _policy: dict) -> None:
        pass

    def capture(self, _base_url: str, _routes: list[str], artifacts_dir: Path, viewports: list[dict]):
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        return [
            EvidenceRecord(
                id=f"browser-{row['name']}",
                type="browser_render",
                stage_id="qa",
                tool="playwright",
                status="PASS",
                summary="fixture",
                data={
                    "route": "/app.html?screen=home",
                    "url": "http://127.0.0.1:4173/app.html?screen=home",
                    "title": "Nova",
                    "viewport": dict(row),
                    "screenshot": f"{row['name']}.png",
                    "screenshot_sha256": "a" * 64,
                },
                origin="runtime",
                trusted=True,
            )
            for row in viewports
        ]


class _FakeObservation:
    def __init__(self, _qa_root: Path, _policy: dict) -> None:
        pass

    def observe(self, _artifacts_dir: Path, route: str | None = None):
        return {
            "observation_id": "browser_obs_fixture",
            "route": route,
            "trusted": False,
            "advisory_only": True,
            "browser_evidence_status": "PASS",
        }


class _FakeVision:
    def __init__(self, _root: Path, _policy: dict) -> None:
        pass

    def review(self, records: list[EvidenceRecord], analyzer=None):
        assert analyzer is None
        return {
            "status": "NOT_RUN",
            "trusted": False,
            "advisory_only": True,
            "coverage": {"viewports": len(records)},
            "review": {"keep": [], "revise": [], "remove": []},
        }


def test_a13_real_project_lane_routes_legacy_nova_profile_without_faking_taxonomy_or_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _nova_fixture(tmp_path)
    monkeypatch.setattr(dogfood_module, "PlaywrightBrowserEvidenceAdapter", _FakeBrowser)
    monkeypatch.setattr(dogfood_module, "PlaywrightBrowserObservationAdapter", _FakeObservation)
    monkeypatch.setattr(dogfood_module, "VisionCreativeDirectorAdapter", _FakeVision)

    report = RealProjectDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
    ).run(
        base_url="http://127.0.0.1:4173",
        report_path=tmp_path / "a13-report.json",
    )

    assert report["passed"] is True
    assert report["project_shape"]["kind"] == "static_html"
    assert report["profile"]["source_domain"] == "consumer_fintech_personal_banking"
    assert report["profile"]["normalized_flow_domain"] == "financial-services"
    assert report["profile"]["product_archetype"] is None
    assert report["profile"]["validation_lane"] is None
    assert report["profile"]["missing_optional_fields"] == ["product_archetype", "validation_lane"]
    assert report["runtime_task_context"]["domain"] == "financial-services"
    assert report["flow"]["id"] == "professional-website-redesign"
    assert report["jit_section"]["skill"] == "financial-product-intelligence"
    assert report["browser"]["viewports"] == ["desktop", "mobile", "tablet"]
    assert report["vision"]["status"] == "NOT_RUN"
    assert report["provider_reasoning"]["status"] == "NOT_RUN"
    assert report["human_review"] == {"status": "pending", "verdict": None}
    assert report["release"]["status"] == "NOT_ATTEMPTED"
    finding_ids = {item["id"] for item in report["target_findings"]}
    assert {
        "stale-package-install",
        "stale-factory-cli",
        "legacy-domain-taxonomy",
        "partial-profile-taxonomy",
    }.issubset(finding_ids)
    assert "provider-quality" in report["truth_boundary"]


def test_a13_unsupported_domain_taxonomy_fails_closed(tmp_path: Path) -> None:
    project = _nova_fixture(tmp_path)
    profile = json.loads((project / ".uiux-profile.json").read_text(encoding="utf-8"))
    profile["domain"] = "generic"
    (project / ".uiux-profile.json").write_text(json.dumps(profile), encoding="utf-8")

    runner = RealProjectDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
    )
    with pytest.raises(Exception, match="unsupported Nova domain taxonomy"):
        runner._profile()


def test_a13_canonical_financial_domain_remains_identity_mapping(tmp_path: Path) -> None:
    project = _nova_fixture(tmp_path)
    profile = json.loads((project / ".uiux-profile.json").read_text(encoding="utf-8"))
    profile["domain"] = "financial-services"
    profile["product_archetype"] = "mobile-finance-control-app"
    profile["validation_lane"] = "PRODUCT"
    (project / ".uiux-profile.json").write_text(json.dumps(profile), encoding="utf-8")

    runner = RealProjectDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
    )
    loaded = runner._profile()
    assert loaded["domain"] == "financial-services"
    findings = runner._target_findings(runner._project_shape(), loaded)
    assert "legacy-domain-taxonomy" not in {item["id"] for item in findings}
    assert "partial-profile-taxonomy" not in {item["id"] for item in findings}


def test_a13_viewport_contract_is_bounded_and_strict(tmp_path: Path) -> None:
    qa_root = tmp_path / "qa"
    qa_root.mkdir()
    adapter = PlaywrightBrowserEvidenceAdapter(qa_root, POLICY)

    assert adapter._validate_viewports(
        [
            {"name": "desktop", "width": 1440, "height": 1000},
            {"name": "mobile", "width": 390, "height": 844},
        ]
    ) == [
        {"name": "desktop", "width": 1440, "height": 1000},
        {"name": "mobile", "width": 390, "height": 844},
    ]

    with pytest.raises(BrowserEvidenceError, match="names must be unique"):
        adapter._validate_viewports(
            [
                {"name": "mobile", "width": 390, "height": 844},
                {"name": "mobile", "width": 430, "height": 900},
            ]
        )
    with pytest.raises(BrowserEvidenceError, match="width must be an integer"):
        adapter._validate_viewports([{"name": "mobile", "width": True, "height": 844}])
    with pytest.raises(BrowserEvidenceError, match="between 240 and 4096"):
        adapter._validate_viewports([{"name": "mobile", "width": 120, "height": 844}])


def test_a13_expected_target_sha_fails_closed_before_browser_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _nova_fixture(tmp_path)
    monkeypatch.setattr(dogfood_module, "_git_sha", lambda _root: "1" * 40)
    runner = RealProjectDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
    )

    with pytest.raises(Exception, match="target SHA mismatch"):
        runner.run(
            base_url="http://127.0.0.1:4173",
            expected_target_sha="2" * 40,
        )
