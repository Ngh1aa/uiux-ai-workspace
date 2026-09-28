from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from core.dogfood.cross_project import (
    ProjectDogfoodProfile,
    evaluate_cross_project_contract,
    project_profile,
)
from core.runtime.flow_os.flow import FlowResolver
from core.runtime.flow_os.safe_read import SafeReader


class RealProjectDogfoodError(RuntimeError):
    """Raised when a pinned real-project dogfood invariant is not satisfied."""


def _git_sha(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=15,
        shell=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value if len(value) == 40 else None


def _visible_files(root: Path) -> list[str]:
    output: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if ".git" in relative.parts or ".uiux-agent-runs" in relative.parts:
            continue
        output.append(relative.as_posix())
    return sorted(output)


class RealProjectDogfoodRunner:
    """Project-agnostic, read-only Factory dogfood over a pinned checkout.

    Project differences are supplied as `ProjectDogfoodProfile` data. This runner owns
    no domain aliases, project names, repository-specific branches or specialist-skill
    exceptions. It validates repository evidence, canonical Task Contract inference and
    declarative Flow routing with the exact same core used by normal Factory execution.

    Render/browser/provider/human/release verdicts intentionally remain outside this
    generic lane unless another evidence adapter explicitly runs them. A legacy A13
    render lane is retained separately as a compatibility adapter during migration.
    """

    def __init__(
        self,
        *,
        skills_root: Path,
        factory_root: Path,
        project_root: Path,
        profile: ProjectDogfoodProfile | None = None,
        project_id: str | None = None,
    ) -> None:
        if profile is not None and project_id is not None:
            raise RealProjectDogfoodError("provide either profile or project_id, not both")
        if profile is None and project_id is None:
            raise RealProjectDogfoodError("generic dogfood requires an explicit profile or project_id")

        self.skills_root = Path(skills_root).resolve()
        self.factory_root = Path(factory_root).resolve()
        self.project_root = Path(project_root).resolve()
        self.profile = profile if profile is not None else project_profile(str(project_id))
        self.profile.validate()

        if not self.skills_root.is_dir():
            raise RealProjectDogfoodError(f"skills root does not exist: {self.skills_root}")
        if not self.factory_root.is_dir():
            raise RealProjectDogfoodError(f"factory root does not exist: {self.factory_root}")
        if not self.project_root.is_dir():
            raise RealProjectDogfoodError(f"project root does not exist: {self.project_root}")
        self.reader = SafeReader(self.project_root)

    def _project_shape(self) -> dict[str, Any]:
        has_package = (self.project_root / "package.json").is_file()
        html_entrypoints = [
            path
            for path in ("index.html", "app.html", "prototype.html")
            if (self.project_root / path).is_file()
        ]
        if has_package:
            kind = "package_project"
        elif html_entrypoints:
            kind = "static_html"
        else:
            kind = "content_or_unknown"
        return {
            "kind": kind,
            "has_package_json": has_package,
            "html_entrypoints": html_entrypoints,
        }

    def run(
        self,
        *,
        expected_target_sha: str | None = None,
        report_path: Path | None = None,
        task_description: str | None = None,
        change_boundary: str | None = None,
    ) -> dict[str, Any]:
        target_sha = _git_sha(self.project_root)
        if expected_target_sha and target_sha != expected_target_sha:
            raise RealProjectDogfoodError(
                f"dogfood target SHA mismatch: expected {expected_target_sha}, got {target_sha or '(not a git checkout)'}"
            )

        available_paths = _visible_files(self.project_root)
        contract_report = evaluate_cross_project_contract(
            self.profile,
            available_paths=available_paths,
            task_description=task_description,
            change_boundary=change_boundary,
        )
        source_truth = contract_report.get("source_truth")
        source_truth_loaded = False
        if isinstance(source_truth, str) and source_truth:
            source_truth_loaded = bool(self.reader.read_text(source_truth).content.strip())

        contract = dict(contract_report["contract"])
        resolver = FlowResolver(self.skills_root / "flows")
        flow_path: Path | None = None
        flow_document: dict[str, Any] | None = None
        flow_score: int | None = None
        flow_error: str | None = None
        try:
            flow_path, flow_document, flow_score = resolver.resolve(contract)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            flow_error = str(exc)

        resolved_flow_id = str(flow_document.get("id")) if flow_document else None
        checks = dict(contract_report["checks"])
        checks.update(
            {
                "source_truth_loaded": source_truth_loaded,
                "flow_resolved": flow_document is not None,
                "expected_flow_preserved": resolved_flow_id == self.profile.expected_flow_id,
                "target_sha_bound": not expected_target_sha or target_sha == expected_target_sha,
            }
        )

        report = {
            "schema_version": 2,
            "phase": "A14-fix-once-validate-across-projects",
            "target": self.profile.repo,
            "target_sha": target_sha,
            "expected_target_sha": expected_target_sha,
            "project": self.profile.project_id,
            "project_shape": self._project_shape(),
            "source_truth": source_truth,
            "contract": contract,
            "flow": {
                "id": resolved_flow_id,
                "expected_id": self.profile.expected_flow_id,
                "score": flow_score,
                "source": str(flow_path) if flow_path is not None else None,
                "error": flow_error,
            },
            "evidence": {
                "model": self.profile.evidence_model,
                "required_paths": list(self.profile.evidence_paths),
                "missing_paths": list(contract_report["missing_evidence"]),
            },
            "checks": checks,
            "passed": all(checks.values()),
            "browser": {"status": "NOT_RUN"},
            "provider_reasoning": {"status": "NOT_RUN"},
            "human_review": {"status": "pending", "verdict": None},
            "release": {"status": "NOT_ATTEMPTED"},
            "truth_boundary": (
                "A14 generic PASS means the pinned checkout, source truth, adaptive Task Contract and "
                "declarative Flow route satisfied one project-agnostic Factory contract. Browser/render, "
                "provider-quality, aesthetic-human-review, deploy and release verdicts are not manufactured."
            ),
        }

        if report_path is not None:
            output = Path(report_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return report
