from __future__ import annotations

import json
from pathlib import Path

import pytest

import core.dogfood._nova_render_impl as nova_impl
from core.dogfood.nova_render_lane import NovaRenderDogfoodRunner
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


def test_a13_nova_render_lane_keeps_historical_profile_coverage_without_generic_coupling(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _nova_fixture(tmp_path)
    monkeypatch.setattr(nova_impl, "PlaywrightBrowserEvidenceAdapter", _FakeBrowser)
    monkeypatch.setattr(nova_impl, "PlaywrightBrowserObservationAdapter", _FakeObservation)
    monkeypatch.setattr(nova_impl, "VisionCreativeDirectorAdapter", _FakeVision)

    report = NovaRenderDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
    ).run(
        base_url="http://127.0.0.1:4173",
        report_path=tmp_path / "a13-report.json",
    )

    assert report["passed"] is True
    assert report["profile"]["normalized_flow_domain"] == "financial-services"
    assert report["flow"]["id"] == "audit-review"
    assert report["runtime_task_context"]["authority"] == "read_only"
    assert report["flow"]["stage_ids"] == ["research", "qa"]
    assert report["jit_section"]["skill"] == "financial-product-intelligence"
    assert report["browser"]["viewports"] == ["desktop", "mobile", "tablet"]
    assert report["vision"]["status"] == "NOT_RUN"
    assert report["provider_reasoning"]["status"] == "NOT_RUN"
    assert report["human_review"] == {"status": "pending", "verdict": None}
    assert report["release"]["status"] == "NOT_ATTEMPTED"


def test_a13_unsupported_nova_taxonomy_fails_closed(tmp_path: Path) -> None:
    project = _nova_fixture(tmp_path)
    profile = json.loads((project / ".uiux-profile.json").read_text(encoding="utf-8"))
    profile["domain"] = "generic"
    (project / ".uiux-profile.json").write_text(json.dumps(profile), encoding="utf-8")
    runner = NovaRenderDogfoodRunner(
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
    runner = NovaRenderDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
    )
    loaded = runner._profile()
    findings = runner._target_findings(runner._project_shape(), loaded)
    assert "legacy-domain-taxonomy" not in {item["id"] for item in findings}
    assert "partial-profile-taxonomy" not in {item["id"] for item in findings}


def test_a13_viewport_contract_remains_bounded_and_strict(tmp_path: Path) -> None:
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


def test_a13_expected_target_sha_fails_closed_before_browser_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _nova_fixture(tmp_path)
    monkeypatch.setattr(nova_impl, "_git_sha", lambda _root: "1" * 40)
    runner = NovaRenderDogfoodRunner(
        skills_root=SKILLS_ROOT,
        factory_root=FACTORY_ROOT,
        project_root=project,
    )
    with pytest.raises(Exception, match="target SHA mismatch"):
        runner.run(
            base_url="http://127.0.0.1:4173",
            expected_target_sha="2" * 40,
        )
