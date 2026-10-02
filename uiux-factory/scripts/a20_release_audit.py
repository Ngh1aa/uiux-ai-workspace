from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

FACTORY_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FACTORY_ROOT.parent
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.benchmarks.regression_corpus import BenchmarkCorpus


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _check(condition: bool, detail: str) -> dict[str, Any]:
    return {"passed": bool(condition), "detail": detail}


def build_report() -> dict[str, Any]:
    policy_path = REPO_ROOT / "skills_UIUX" / "runtime" / "runtime-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    corpus = BenchmarkCorpus.load(
        FACTORY_ROOT / "benchmarks" / "corpus" / "uiux-product-v2.json"
    )
    domains = {case.domain for case in corpus.cases}
    tracked = _tracked_files()

    secret_like = [
        path
        for path in tracked
        if Path(path).name == ".env"
        or Path(path).suffix.lower() in {".pem", ".p12", ".pfx"}
        or (Path(path).suffix.lower() == ".key" and "fixture" not in path.lower())
    ]

    generic_runner = (
        FACTORY_ROOT / "core" / "dogfood" / "real_project.py"
    ).read_text(encoding="utf-8")
    nova_script = (
        FACTORY_ROOT / "scripts" / "run_nova_dogfood.py"
    ).read_text(encoding="utf-8")
    quickstart = (
        FACTORY_ROOT / "docs" / "V1-QUICKSTART.md"
    ).read_text(encoding="utf-8")

    browser = dict(policy.get("browser_evidence", {}))
    sandbox = dict(policy.get("sandbox", {}))
    release_rules = list(policy.get("rules", []))
    critical = set(policy.get("critical_actions", []))

    checks = {
        "a15_legacy_module_removed": _check(
            not (FACTORY_ROOT / "core" / "dogfood" / "nova_real_project_legacy.py").exists(),
            "old Nova legacy module path is absent",
        ),
        "a15_nova_render_isolated": _check(
            (FACTORY_ROOT / "core" / "dogfood" / "nova_render_lane.py").is_file()
            and (FACTORY_ROOT / "core" / "dogfood" / "_nova_render_impl.py").is_file()
            and "nova_render_lane" in nova_script,
            "Nova rendered regression coverage is explicitly named and isolated from the generic runner",
        ),
        "a15_generic_runner_not_project_named": _check(
            all(token not in generic_runner for token in ("Nova", "Lumen", "CENNEXT", "LuxRoom")),
            "generic real-project runner contains no named-project branches across the four-project Flow 4 matrix",
        ),
        "a16_autonomous_lifecycle": _check(
            (FACTORY_ROOT / "core" / "runtime" / "flow_os" / "autonomous.py").is_file()
            and (FACTORY_ROOT / "scripts" / "run_autonomous_flow.py").is_file(),
            "canonical autonomous lifecycle API and CLI exist",
        ),
        "a17_recovery_and_rollback": _check(
            (FACTORY_ROOT / "core" / "runtime" / "flow_os" / "resilience.py").is_file(),
            "hash-verified checkpoint recovery and isolated-worktree rollback module exists",
        ),
        "a18_diverse_benchmark": _check(
            len(corpus.cases) >= 12 and len(domains) >= 12,
            f"benchmark v2 covers {len(corpus.cases)} cases across {len(domains)} domains",
        ),
        "a19_quickstart": _check(
            "prompt → audit → plan → execute → QA" in quickstart
            and "--recover-snapshot" in quickstart
            and "Do not copy a full Factory workflow into the prompt" in quickstart,
            "v1 quickstart documents compact goals, lifecycle, resume and recovery",
        ),
        "security_no_tracked_secret_files": _check(
            not secret_like,
            "no tracked .env/private-key credential files" if not secret_like
            else "suspicious tracked files: " + ", ".join(secret_like),
        ),
        "security_browser_remote_disabled": _check(
            browser.get("allow_remote") is False,
            "browser evidence remote targets are disabled by default",
        ),
        "security_sandbox_fail_closed": _check(
            sandbox.get("required") is True
            and sandbox.get("network") == "none"
            and sandbox.get("image_pull") == "never",
            "target command sandbox is required, network-disabled and does not pull images implicitly",
        ),
        "release_is_human_authorized": _check(
            {"merge", "deploy"}.issubset(critical)
            and any(
                "Release authority must come from explicit user/project authorization" in str(rule)
                for rule in release_rules
            ),
            "merge/deploy remain critical and release authority is explicitly human/project authorized",
        ),
        "a20_workflow_present": _check(
            (REPO_ROOT / ".github" / "workflows" / "a20-release-candidate.yml").is_file(),
            "dedicated A20 release-candidate workflow exists",
        ),
    }

    passed = all(row["passed"] for row in checks.values())
    return {
        "schema_version": 1,
        "release_candidate": "uiux-factory-v1",
        "benchmark_version": corpus.version,
        "benchmark_cases": len(corpus.cases),
        "benchmark_domains": len(domains),
        "checks": checks,
        "passed": passed,
        "truth_boundary": (
            "A20 PASS means the declared v1 structural/security/test/dogfood release criteria "
            "are satisfied. It is not a claim that future software can never contain bugs, "
            "and it never fabricates provider quality, human aesthetic approval, user outcomes "
            "or production-release authorization."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit UIUX Factory v1 release-candidate invariants")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = build_report()
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
