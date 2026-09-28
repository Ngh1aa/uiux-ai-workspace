from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CORPUS_SCHEMA_VERSION = 1
REQUIRED_CASE_KEYS = {
    "id",
    "domain",
    "product_archetype",
    "brief",
    "source_truth",
    "representative_routes",
    "required_page_roles",
    "reference_constraints",
    "required_evidence",
    "human_review",
    "screenshot_pack",
}
ALLOWED_HUMAN_REVIEW_STATUS = {"pending", "recorded"}
ALLOWED_SCREENSHOT_STATUS = {"pending", "recorded"}


class BenchmarkCorpusError(ValueError):
    """Raised when a benchmark corpus/result violates the deterministic contract."""


def _nonempty_strings(value: Any, *, field: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
        raise BenchmarkCorpusError(f"{field} must be a non-empty array of non-empty strings")
    return [item.strip() for item in value]


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    domain: str
    product_archetype: str
    brief: str
    source_truth: list[str]
    representative_routes: list[str]
    required_page_roles: list[str]
    reference_constraints: list[str]
    required_evidence: list[str]
    human_review: dict[str, Any]
    screenshot_pack: dict[str, Any]
    tags: list[str]
    content_hash: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "BenchmarkCase":
        if not isinstance(raw, dict):
            raise BenchmarkCorpusError("benchmark case must be an object")
        missing = sorted(REQUIRED_CASE_KEYS.difference(raw))
        if missing:
            raise BenchmarkCorpusError("benchmark case missing keys: " + ", ".join(missing))
        unknown = sorted(set(raw).difference(REQUIRED_CASE_KEYS | {"tags"}))
        if unknown:
            raise BenchmarkCorpusError("benchmark case has unknown keys: " + ", ".join(unknown))

        case_id = str(raw["id"]).strip()
        domain = str(raw["domain"]).strip()
        archetype = str(raw["product_archetype"]).strip()
        brief = str(raw["brief"]).strip()
        if not case_id or not domain or not archetype or not brief:
            raise BenchmarkCorpusError("id/domain/product_archetype/brief must be non-empty")

        routes = _nonempty_strings(raw["representative_routes"], field=f"{case_id}.representative_routes")
        if any(not route.startswith("/") for route in routes):
            raise BenchmarkCorpusError(f"{case_id}.representative_routes must use absolute route paths")

        human_review = raw["human_review"]
        if not isinstance(human_review, dict):
            raise BenchmarkCorpusError(f"{case_id}.human_review must be an object")
        review_status = human_review.get("status")
        if review_status not in ALLOWED_HUMAN_REVIEW_STATUS:
            raise BenchmarkCorpusError(f"{case_id}.human_review.status must be pending or recorded")
        if review_status == "recorded" and not str(human_review.get("artifact", "")).strip():
            raise BenchmarkCorpusError(f"{case_id}.human_review recorded status requires artifact")
        if review_status == "pending" and human_review.get("verdict") not in {None, ""}:
            raise BenchmarkCorpusError(f"{case_id}.human_review pending status cannot fabricate a verdict")

        screenshot_pack = raw["screenshot_pack"]
        if not isinstance(screenshot_pack, dict):
            raise BenchmarkCorpusError(f"{case_id}.screenshot_pack must be an object")
        screenshot_status = screenshot_pack.get("status")
        if screenshot_status not in ALLOWED_SCREENSHOT_STATUS:
            raise BenchmarkCorpusError(f"{case_id}.screenshot_pack.status must be pending or recorded")
        viewports = _nonempty_strings(screenshot_pack.get("required_viewports"), field=f"{case_id}.screenshot_pack.required_viewports")
        if screenshot_status == "recorded" and not str(screenshot_pack.get("artifact", "")).strip():
            raise BenchmarkCorpusError(f"{case_id}.screenshot_pack recorded status requires artifact")

        normalized = {
            "id": case_id,
            "domain": domain,
            "product_archetype": archetype,
            "brief": brief,
            "source_truth": _nonempty_strings(raw["source_truth"], field=f"{case_id}.source_truth"),
            "representative_routes": routes,
            "required_page_roles": _nonempty_strings(raw["required_page_roles"], field=f"{case_id}.required_page_roles"),
            "reference_constraints": _nonempty_strings(raw["reference_constraints"], field=f"{case_id}.reference_constraints"),
            "required_evidence": _nonempty_strings(raw["required_evidence"], field=f"{case_id}.required_evidence"),
            "human_review": dict(human_review),
            "screenshot_pack": {**dict(screenshot_pack), "required_viewports": viewports},
            "tags": [str(item).strip() for item in raw.get("tags", []) if str(item).strip()],
        }
        return cls(**normalized, content_hash=_stable_hash(normalized))


@dataclass(frozen=True)
class BenchmarkCorpus:
    corpus_id: str
    version: str
    cases: tuple[BenchmarkCase, ...]
    content_hash: str

    @classmethod
    def load(cls, path: Path) -> "BenchmarkCorpus":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise BenchmarkCorpusError("benchmark corpus must be an object")
        if payload.get("schema_version") != CORPUS_SCHEMA_VERSION:
            raise BenchmarkCorpusError(f"schema_version must be {CORPUS_SCHEMA_VERSION}")
        allowed = {"schema_version", "corpus_id", "version", "description", "cases"}
        unknown = sorted(set(payload).difference(allowed))
        if unknown:
            raise BenchmarkCorpusError("benchmark corpus has unknown keys: " + ", ".join(unknown))
        corpus_id = str(payload.get("corpus_id", "")).strip()
        version = str(payload.get("version", "")).strip()
        raw_cases = payload.get("cases")
        if not corpus_id or not version or not isinstance(raw_cases, list) or not raw_cases:
            raise BenchmarkCorpusError("corpus_id/version/cases are required")
        cases = tuple(BenchmarkCase.from_dict(item) for item in raw_cases)
        ids = [case.id for case in cases]
        if len(ids) != len(set(ids)):
            raise BenchmarkCorpusError("benchmark case ids must be unique")
        domains = {case.domain for case in cases}
        if len(cases) < 8 or len(domains) < 8:
            raise BenchmarkCorpusError("A12 corpus requires at least 8 cases across 8 distinct domains")
        hash_payload = {
            "schema_version": CORPUS_SCHEMA_VERSION,
            "corpus_id": corpus_id,
            "version": version,
            "cases": [case.content_hash for case in cases],
        }
        return cls(corpus_id, version, cases, _stable_hash(hash_payload))

    def manifest(self) -> dict[str, Any]:
        return {
            "schema_version": CORPUS_SCHEMA_VERSION,
            "corpus_id": self.corpus_id,
            "version": self.version,
            "case_count": len(self.cases),
            "content_hash": self.content_hash,
            "cases": [
                {
                    "id": case.id,
                    "domain": case.domain,
                    "product_archetype": case.product_archetype,
                    "content_hash": case.content_hash,
                    "human_review_status": case.human_review["status"],
                    "screenshot_pack_status": case.screenshot_pack["status"],
                }
                for case in self.cases
            ],
        }


def evaluate_case_result(case: BenchmarkCase, result: dict[str, Any]) -> dict[str, Any]:
    """Evaluate objective benchmark coverage only; never manufacture an aesthetic verdict."""
    if not isinstance(result, dict):
        raise BenchmarkCorpusError("benchmark result must be an object")
    if str(result.get("case_id", "")) != case.id:
        raise BenchmarkCorpusError(f"result case_id must equal {case.id}")

    routes = {str(item) for item in result.get("routes", [])}
    roles = {str(item) for item in result.get("page_roles", [])}
    evidence = {str(item) for item in result.get("evidence_types", [])}
    viewports = {str(item) for item in result.get("screenshot_viewports", [])}
    hard_failures = result.get("hard_rule_failures", [])
    if not isinstance(hard_failures, list):
        raise BenchmarkCorpusError("hard_rule_failures must be an array")

    checks = {
        "routes": set(case.representative_routes).issubset(routes),
        "page_roles": set(case.required_page_roles).issubset(roles),
        "evidence": set(case.required_evidence).issubset(evidence),
        "viewports": set(case.screenshot_pack["required_viewports"]).issubset(viewports),
        "hard_rules": len(hard_failures) == 0,
    }
    objective_pass = all(checks.values())

    human_status = str(result.get("human_review_status", "pending"))
    human_verdict = result.get("human_verdict")
    if human_status not in ALLOWED_HUMAN_REVIEW_STATUS:
        raise BenchmarkCorpusError("human_review_status must be pending or recorded")
    if human_status == "pending" and human_verdict not in {None, ""}:
        raise BenchmarkCorpusError("pending human review cannot include a verdict")

    return {
        "case_id": case.id,
        "case_hash": case.content_hash,
        "checks": checks,
        "objective_pass": objective_pass,
        "human_review_status": human_status,
        "human_verdict": human_verdict if human_status == "recorded" else None,
        "overall_status": "reviewed" if objective_pass and human_status == "recorded" else ("objective_pass_pending_human" if objective_pass else "objective_fail"),
    }


def build_benchmark_report(corpus: BenchmarkCorpus, results: list[dict[str, Any]], *, run_label: str) -> dict[str, Any]:
    by_id = {str(item.get("case_id", "")): item for item in results if isinstance(item, dict)}
    if len(by_id) != len(results):
        raise BenchmarkCorpusError("benchmark result case_ids must be unique and non-empty")
    unknown = sorted(set(by_id).difference(case.id for case in corpus.cases))
    if unknown:
        raise BenchmarkCorpusError("results contain unknown cases: " + ", ".join(unknown))

    rows = [evaluate_case_result(case, by_id[case.id]) for case in corpus.cases if case.id in by_id]
    missing = [case.id for case in corpus.cases if case.id not in by_id]
    return {
        "schema_version": 1,
        "run_label": str(run_label),
        "corpus_id": corpus.corpus_id,
        "corpus_version": corpus.version,
        "corpus_hash": corpus.content_hash,
        "case_count": len(corpus.cases),
        "submitted_count": len(rows),
        "missing_cases": missing,
        "objective_pass_count": sum(1 for row in rows if row["objective_pass"]),
        "human_reviewed_count": sum(1 for row in rows if row["human_review_status"] == "recorded"),
        "complete": not missing,
        "objective_pass": not missing and all(row["objective_pass"] for row in rows),
        "cases": rows,
    }


def compare_benchmark_reports(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Compare objective benchmark coverage without ranking providers or aesthetic quality."""
    for report in (baseline, candidate):
        if report.get("corpus_hash") is None:
            raise BenchmarkCorpusError("benchmark report missing corpus_hash")
    if baseline["corpus_hash"] != candidate["corpus_hash"]:
        raise BenchmarkCorpusError("cannot compare reports from different corpus hashes")

    baseline_cases = {row["case_id"]: row for row in baseline.get("cases", [])}
    candidate_cases = {row["case_id"]: row for row in candidate.get("cases", [])}
    case_ids = sorted(set(baseline_cases) | set(candidate_cases))
    rows: list[dict[str, Any]] = []
    for case_id in case_ids:
        before = baseline_cases.get(case_id)
        after = candidate_cases.get(case_id)
        before_pass = bool(before and before.get("objective_pass"))
        after_pass = bool(after and after.get("objective_pass"))
        if before_pass == after_pass:
            change = "unchanged"
        elif after_pass:
            change = "objective_recovery"
        else:
            change = "objective_regression"
        rows.append({"case_id": case_id, "change": change, "baseline_objective_pass": before_pass, "candidate_objective_pass": after_pass})

    return {
        "schema_version": 1,
        "corpus_hash": baseline["corpus_hash"],
        "baseline": baseline.get("run_label", "baseline"),
        "candidate": candidate.get("run_label", "candidate"),
        "objective_regressions": [row["case_id"] for row in rows if row["change"] == "objective_regression"],
        "objective_recoveries": [row["case_id"] for row in rows if row["change"] == "objective_recovery"],
        "cases": rows,
    }
