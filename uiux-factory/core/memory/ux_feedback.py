"""Reuse A5 memory for external browser feedback and bounded advisory recall."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.memory.evaluation_memory import EvaluationMemoryError, EvaluationMemoryStore
from core.memory.quality_pattern_recall import build_quality_pattern_insight


def recall_external_quality(target_root: Path | str | None, policy: dict[str, Any]) -> dict[str, Any]:
    if target_root is None:
        return {"status": "NOT_PROVIDED", "advisory_only": True, "insight": None}
    try:
        store = EvaluationMemoryStore(Path(target_root), policy)
        insight = build_quality_pattern_insight(store)
    except (EvaluationMemoryError, OSError, ValueError) as exc:
        # Advisory history cannot block routing or become a QA pass.
        return {"status": "UNKNOWN", "advisory_only": True, "insight": None, "diagnostic": type(exc).__name__}
    return {"status": "DISABLED" if not store.enabled else "AVAILABLE" if insight else "EMPTY", "advisory_only": True, "insight": insight}


def record_browser_feedback(project_root: Path, reports_dir: Path, policy: dict[str, Any]) -> dict[str, Any]:
    """Import local evaluator receipts, not raw chat or a model's claim of success.

    Records only the existing A5 categorical allowlist. Render artifacts stay with QA.
    Missing, malformed or non-evaluator receipts never become learned outcomes.
    """
    store = EvaluationMemoryStore(project_root, policy)
    if not store.enabled:
        return {"status": "DISABLED", "reports": 0, "patterns": 0, "advisory_only": True}
    if not reports_dir.is_dir() or reports_dir.is_symlink():
        raise ValueError("reports_dir must be a local directory, not a symlink")
    files = sorted(reports_dir.glob("*.json"))
    if not files:
        return {"status": "NO_REPORTS", "reports": 0, "patterns": 0, "advisory_only": True}
    if len(files) > 500:
        raise ValueError("feedback import is limited to 500 report files")
    validated = []
    for path in files:
        if path.is_symlink() or path.stat().st_size > 1_000_000:
            raise ValueError("feedback receipt must be bounded and not a symlink")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != 1 or payload.get("evaluator") != "uiux-rendered-regression" or payload.get("scope") != "automated_checks_only":
            raise ValueError("feedback must be a rendered UX evaluator receipt")
        requirements = payload.get("requirements")
        if not isinstance(requirements, dict) or not requirements or len(requirements) > 67:
            raise ValueError("feedback requirements must be a bounded nonempty object")
        for key, result in requirements.items():
            if not isinstance(key, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", key) or not isinstance(result, dict) or result.get("outcome") not in {"passed", "failed", "cantTell"} or type(result.get("applicable")) is not bool:
                raise ValueError("invalid observed feedback requirement")
        # Validate the whole batch before the first write; no partial import on bad input.
        validated.append(payload)
    patterns = sum(store.record_post_render_report(payload) for payload in validated)
    return {"status": "RECORDED", "reports": len(validated), "patterns": patterns, "advisory_only": True, "gate_effect": "none"}
