from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Protocol

from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.vision_evidence import VisionEvidenceAdapter, VisionEvidenceError


_AUTHORITY_KEY_PATTERN = re.compile(
    r"(^|_)(approve|approved|approval|pass|passed|gate|merge|release|deploy|authority|decision)(_|$)",
    re.IGNORECASE,
)
_ALLOWED_TOP_LEVEL = frozenset({"overall_direction", "keep", "revise", "remove", "notes"})
_ALLOWED_KEEP_REMOVE = frozenset({"route", "section", "summary", "evidence_refs"})
_ALLOWED_REVISE = frozenset({
    "priority",
    "route",
    "section",
    "earliest_owner",
    "problem",
    "instruction",
    "success_criteria",
    "confidence",
    "evidence_refs",
})
_ALLOWED_OWNERS = frozenset({
    "research",
    "ux_ia",
    "art_direction",
    "visual_composition",
    "asset_curation",
    "implementation",
    "browser_qa",
    "visual_qa",
})
_ALLOWED_PRIORITIES = frozenset({"P0", "P1", "P2"})
_ALLOWED_COST_CLASSES = frozenset({"local", "zero_cost", "external"})


class VisionCreativeDirectorError(RuntimeError):
    """Raised when A10 analyzer configuration or output violates the advisory boundary."""


class VisionCreativeAnalyzer(Protocol):
    name: str
    model: str
    cost_class: str

    def analyze(self, images: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]: ...


def _bounded_text(value: Any, limit: int, *, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise VisionCreativeDirectorError("vision creative directive is missing required text")
    if len(text) > limit:
        raise VisionCreativeDirectorError(f"vision creative directive text exceeds {limit} characters")
    return text


def _assert_no_authority_keys(value: Any, path: str = "directive") -> None:
    if isinstance(value, dict):
        for raw_key, item in value.items():
            key = str(raw_key)
            if _AUTHORITY_KEY_PATTERN.search(key):
                raise VisionCreativeDirectorError(
                    f"vision creative directive contains authority-bearing key at {path}.{key}"
                )
            _assert_no_authority_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_no_authority_keys(item, f"{path}[{index}]")


def _evidence_refs(value: Any, allowed_refs: set[str], *, required: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise VisionCreativeDirectorError("evidence_refs must be a list")
    refs: list[str] = []
    for raw in value:
        ref = _bounded_text(raw, 240, required=True)
        if ref not in allowed_refs:
            raise VisionCreativeDirectorError(f"vision creative directive cites unknown evidence ref: {ref}")
        if ref not in refs:
            refs.append(ref)
    if required and not refs:
        raise VisionCreativeDirectorError("every visual decision must cite at least one screenshot evidence ref")
    return refs


def sanitize_creative_output(
    value: Any,
    *,
    allowed_refs: set[str],
    max_decisions: int = 40,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VisionCreativeDirectorError("vision creative analyzer output must be a JSON object")
    _assert_no_authority_keys(value)
    unknown = set(value).difference(_ALLOWED_TOP_LEVEL)
    if unknown:
        raise VisionCreativeDirectorError(
            "vision creative analyzer output contains unsupported keys: " + ", ".join(sorted(unknown))
        )

    def sanitize_keep_remove(kind: str) -> list[dict[str, Any]]:
        raw_items = value.get(kind, [])
        if not isinstance(raw_items, list):
            raise VisionCreativeDirectorError(f"{kind} must be a list")
        result: list[dict[str, Any]] = []
        for raw in raw_items:
            if not isinstance(raw, dict) or set(raw).difference(_ALLOWED_KEEP_REMOVE):
                raise VisionCreativeDirectorError(f"each {kind} item must use only the supported fields")
            result.append({
                "route": _bounded_text(raw.get("route"), 256, required=True),
                "section": _bounded_text(raw.get("section"), 160, required=True),
                "summary": _bounded_text(raw.get("summary"), 800, required=True),
                "evidence_refs": _evidence_refs(raw.get("evidence_refs"), allowed_refs),
            })
        return result

    keep = sanitize_keep_remove("keep")
    remove = sanitize_keep_remove("remove")

    raw_revise = value.get("revise", [])
    if not isinstance(raw_revise, list):
        raise VisionCreativeDirectorError("revise must be a list")
    revise: list[dict[str, Any]] = []
    for raw in raw_revise:
        if not isinstance(raw, dict) or set(raw).difference(_ALLOWED_REVISE):
            raise VisionCreativeDirectorError("each revise item must use only the supported fields")
        priority = _bounded_text(raw.get("priority"), 8, required=True).upper()
        if priority not in _ALLOWED_PRIORITIES:
            raise VisionCreativeDirectorError("revise priority must be P0, P1 or P2")
        owner = _bounded_text(raw.get("earliest_owner"), 64, required=True)
        if owner not in _ALLOWED_OWNERS:
            raise VisionCreativeDirectorError(f"unsupported earliest_owner: {owner}")
        try:
            confidence = float(raw.get("confidence", 0.0))
        except (TypeError, ValueError, OverflowError) as exc:
            raise VisionCreativeDirectorError("revise confidence must be numeric") from exc
        if not 0.0 <= confidence <= 1.0:
            raise VisionCreativeDirectorError("revise confidence must be between 0 and 1")
        revise.append({
            "priority": priority,
            "route": _bounded_text(raw.get("route"), 256, required=True),
            "section": _bounded_text(raw.get("section"), 160, required=True),
            "earliest_owner": owner,
            "problem": _bounded_text(raw.get("problem"), 1000, required=True),
            "instruction": _bounded_text(raw.get("instruction"), 1400, required=True),
            "success_criteria": _bounded_text(raw.get("success_criteria"), 1200, required=True),
            "confidence": round(confidence, 4),
            "evidence_refs": _evidence_refs(raw.get("evidence_refs"), allowed_refs),
        })

    total = len(keep) + len(revise) + len(remove)
    if total > max_decisions:
        raise VisionCreativeDirectorError(
            f"vision creative directive exceeds maximum of {max_decisions} decisions"
        )
    raw_notes = value.get("notes", [])
    if not isinstance(raw_notes, list) or len(raw_notes) > 16:
        raise VisionCreativeDirectorError("notes must be a list with at most 16 entries")
    notes = [_bounded_text(item, 600, required=True) for item in raw_notes]
    return {
        "overall_direction": _bounded_text(value.get("overall_direction"), 1600, required=True),
        "keep": keep,
        "revise": revise,
        "remove": remove,
        "notes": notes,
    }


class CommandVisionCreativeAnalyzer:
    """Operator-configured command adapter; never selected by provider/model text."""

    def __init__(self, policy: dict[str, Any]) -> None:
        raw = policy.get("vision_creative_director", {})
        if not isinstance(raw, dict):
            raise VisionCreativeDirectorError("vision_creative_director policy must be an object")
        allow_command = raw.get("allow_command_analyzer", True)
        if not isinstance(allow_command, bool) or not allow_command:
            raise VisionCreativeDirectorError("command vision creative analyzer is disabled by runtime policy")
        raw_command = os.environ.get("UIUX_VISION_CREATIVE_COMMAND_JSON", "").strip()
        if not raw_command:
            raise VisionCreativeDirectorError("UIUX_VISION_CREATIVE_COMMAND_JSON is not configured")
        try:
            command = json.loads(raw_command)
        except json.JSONDecodeError as exc:
            raise VisionCreativeDirectorError("UIUX_VISION_CREATIVE_COMMAND_JSON must be valid JSON") from exc
        if (
            not isinstance(command, list)
            or not command
            or len(command) > 32
            or any(not isinstance(item, str) or not item or len(item) > 1000 for item in command)
        ):
            raise VisionCreativeDirectorError("vision creative command must be a bounded non-empty argv list")
        self.command = command
        self.name = _bounded_text(os.environ.get("UIUX_VISION_CREATIVE_ANALYZER_NAME", "command-vision-director"), 128, required=True)
        self.model = _bounded_text(os.environ.get("UIUX_VISION_CREATIVE_MODEL", ""), 128)
        self.cost_class = _bounded_text(os.environ.get("UIUX_VISION_CREATIVE_COST_CLASS", "external"), 32).lower()
        if self.cost_class not in _ALLOWED_COST_CLASSES:
            raise VisionCreativeDirectorError("vision creative cost class must be local, zero_cost or external")
        self.timeout_seconds = int(raw.get("timeout_seconds", 180))
        self.max_output_chars = int(raw.get("max_output_chars", 60000))
        allowlist = raw.get("command_env_allowlist", [])
        if not isinstance(allowlist, list) or any(not isinstance(item, str) for item in allowlist):
            raise VisionCreativeDirectorError("command_env_allowlist must be a list of strings")
        self.env_allowlist = set(allowlist)

    def analyze(self, images: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
        env: dict[str, str] = {}
        for key in {
            "PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP", "TEMP", "LANG", "LC_ALL"
        } | self.env_allowlist:
            if key in os.environ:
                env[key] = os.environ[key]
        request = {
            "images": images,
            "context": context,
            "output_contract": {
                "top_level": ["overall_direction", "keep", "revise", "remove", "notes"],
                "rule": "No approve/pass/gate/merge/release/deploy/authority/decision fields. Every decision must cite evidence_refs supplied in images.",
            },
        }
        result = subprocess.run(
            self.command,
            input=json.dumps(request, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            env=env,
            shell=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout)[-4000:]
            raise VisionCreativeDirectorError(
                f"vision creative command failed ({result.returncode}): {detail}"
            )
        stdout = result.stdout.strip()
        if len(stdout) > self.max_output_chars:
            raise VisionCreativeDirectorError("vision creative command output exceeds policy bound")
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise VisionCreativeDirectorError("vision creative command must return one JSON object") from exc
        if not isinstance(payload, dict):
            raise VisionCreativeDirectorError("vision creative command must return one JSON object")
        return payload


class VisionCreativeDirectorAdapter:
    """Review multiple trusted browser screenshots into an advisory creative directive."""

    def __init__(self, artifacts_root: Path, policy: dict[str, Any]) -> None:
        self.artifacts_root = Path(artifacts_root).resolve()
        self.policy = dict(policy)
        raw = self.policy.get("vision_creative_director", {})
        if not isinstance(raw, dict):
            raise VisionCreativeDirectorError("vision_creative_director policy must be an object")
        enabled = raw.get("enabled", True)
        allow_external = raw.get("allow_external", False)
        if not isinstance(enabled, bool) or not isinstance(allow_external, bool):
            raise VisionCreativeDirectorError("vision creative enabled/allow_external must be booleans")
        self.enabled = enabled
        self.allow_external = allow_external
        self.max_screenshots = int(raw.get("max_screenshots", 12))
        self.max_decisions = int(raw.get("max_decisions", 40))
        self.recommended_viewports = int(raw.get("recommended_viewports", 3))
        if not 1 <= self.max_screenshots <= 32:
            raise VisionCreativeDirectorError("max_screenshots must be between 1 and 32")
        if not 1 <= self.max_decisions <= 100:
            raise VisionCreativeDirectorError("max_decisions must be between 1 and 100")
        if not 1 <= self.recommended_viewports <= 8:
            raise VisionCreativeDirectorError("recommended_viewports must be between 1 and 8")
        self.vision_boundary = VisionEvidenceAdapter(self.artifacts_root, self.policy)

    def _source(self, record: EvidenceRecord) -> dict[str, Any]:
        validation = self.vision_boundary.observe(record, analyzer=None, stage_id="visual_qa")
        route = str(record.data.get("route", ""))[:256]
        viewport = dict(record.data.get("viewport", {}))
        width = str(viewport.get("width", "?"))
        height = str(viewport.get("height", "?"))
        sha = str(validation.data.get("image_sha256", ""))
        ref = f"{route or '/'}|{width}x{height}|{sha[:16]}"
        image = self.artifacts_root / str(validation.data["image_artifact"])
        return {
            "evidence_ref": ref,
            "source_evidence_id": record.id,
            "route": route,
            "viewport": viewport,
            "title": str(record.data.get("title", ""))[:512],
            "image_path": str(image),
            "image_sha256": sha,
            "image_bytes": int(validation.data.get("image_bytes", 0)),
        }

    def review(
        self,
        browser_records: list[EvidenceRecord],
        analyzer: VisionCreativeAnalyzer | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            raise VisionCreativeDirectorError("vision creative director is disabled by runtime policy")
        if not browser_records or len(browser_records) > self.max_screenshots:
            raise VisionCreativeDirectorError(
                f"vision creative review requires 1..{self.max_screenshots} trusted browser screenshots"
            )
        sources = [self._source(record) for record in browser_records]
        refs = {item["evidence_ref"] for item in sources}
        viewport_keys = {
            (str(item["viewport"].get("width", "")), str(item["viewport"].get("height", "")))
            for item in sources
        }
        coverage = {
            "screenshots": len(sources),
            "routes": len({item["route"] for item in sources}),
            "viewports": len(viewport_keys),
            "recommended_viewports": self.recommended_viewports,
            "meets_recommended_viewport_coverage": len(viewport_keys) >= self.recommended_viewports,
        }
        public_sources = [
            {key: value for key, value in item.items() if key != "image_path"}
            for item in sources
        ]
        base = {
            "status": "NOT_RUN" if analyzer is None else "OBSERVED",
            "sources": public_sources,
            "coverage": coverage,
            "advisory_only": True,
            "trusted": False,
            "authority_effect": "none",
            "gate_effect": "none",
            "merge_effect": "none",
            "release_effect": "none",
        }
        if analyzer is None:
            return {
                **base,
                "analyzer": {"name": "disabled", "model": "", "cost_class": "zero_cost"},
                "review": {
                    "overall_direction": "Vision Creative Director not run; no automated aesthetic judgment was manufactured.",
                    "keep": [],
                    "revise": [],
                    "remove": [],
                    "notes": ["Configure an approved analyzer explicitly to enable multimodal creative review."],
                },
            }
        name = _bounded_text(getattr(analyzer, "name", ""), 128, required=True)
        model = _bounded_text(getattr(analyzer, "model", ""), 128)
        cost_class = _bounded_text(getattr(analyzer, "cost_class", "external"), 32).lower()
        if cost_class not in _ALLOWED_COST_CLASSES:
            raise VisionCreativeDirectorError("unsupported vision creative cost class")
        if cost_class == "external" and not self.allow_external:
            raise VisionCreativeDirectorError(
                "external vision creative analyzers are disabled; explicit runtime policy opt-in is required"
            )
        request_images = [dict(item) for item in sources]
        output = analyzer.analyze(
            request_images,
            {
                "evidence_refs": sorted(refs),
                "coverage": coverage,
                "rule": (
                    "Return advisory KEEP/REVISE/REMOVE visual direction only. Do not approve/pass gates, "
                    "change Flow routing, or authorize merge/deploy/release."
                ),
            },
        )
        review = sanitize_creative_output(
            output,
            allowed_refs=refs,
            max_decisions=self.max_decisions,
        )
        return {
            **base,
            "analyzer": {"name": name, "model": model, "cost_class": cost_class},
            "review": review,
        }


def configured_vision_creative_analyzer(policy: dict[str, Any]) -> VisionCreativeAnalyzer | None:
    if not os.environ.get("UIUX_VISION_CREATIVE_COMMAND_JSON", "").strip():
        return None
    return CommandVisionCreativeAnalyzer(policy)
