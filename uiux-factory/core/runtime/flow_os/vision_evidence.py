from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Protocol

from core.runtime.flow_os.evidence import EvidenceRecord


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
WEBP_RIFF = b"RIFF"
WEBP_KIND = b"WEBP"
_ALLOWED_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp"})
_ALLOWED_SEVERITIES = frozenset({"info", "warning", "error"})
_ALLOWED_TOP_LEVEL_KEYS = frozenset({"summary", "findings"})
_ALLOWED_FINDING_KEYS = frozenset({"category", "severity", "summary", "detail", "confidence", "bbox"})
_AUTHORITY_KEY_PATTERN = re.compile(
    r"(^|_)(approve|approved|approval|pass|passed|gate|merge|release|deploy|authority|decision)(_|$)",
    re.IGNORECASE,
)


class VisionEvidenceError(RuntimeError):
    """Raised when image evidence or a vision observation violates the A7 trust boundary."""


class VisionAnalyzer(Protocol):
    name: str
    model: str
    cost_class: str

    def analyze(self, image_path: Path, context: dict[str, Any]) -> dict[str, Any]: ...


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bounded_text(value: Any, limit: int, *, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise VisionEvidenceError("vision observation is missing required text")
    if len(text) > limit:
        raise VisionEvidenceError(f"vision observation text exceeds {limit} characters")
    return text


def _assert_no_authority_keys(value: Any, path: str = "observation") -> None:
    if isinstance(value, dict):
        for raw_key, item in value.items():
            key = str(raw_key)
            if _AUTHORITY_KEY_PATTERN.search(key):
                raise VisionEvidenceError(f"vision observation contains authority-bearing key at {path}.{key}")
            _assert_no_authority_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_no_authority_keys(item, f"{path}[{index}]")


def _sanitize_bbox(value: Any) -> dict[str, float] | None:
    if value in (None, {}):
        return None
    if not isinstance(value, dict) or set(value) != {"x", "y", "width", "height"}:
        raise VisionEvidenceError("vision finding bbox must contain x, y, width and height only")
    box: dict[str, float] = {}
    for key in ("x", "y", "width", "height"):
        try:
            number = float(value[key])
        except (TypeError, ValueError, OverflowError) as exc:
            raise VisionEvidenceError(f"vision finding bbox {key} must be numeric") from exc
        if not 0.0 <= number <= 1.0:
            raise VisionEvidenceError(f"vision finding bbox {key} must be normalized to 0..1")
        box[key] = round(number, 4)
    if box["x"] + box["width"] > 1.0001 or box["y"] + box["height"] > 1.0001:
        raise VisionEvidenceError("vision finding bbox must stay inside normalized image bounds")
    return box


def sanitize_vision_output(value: Any, *, max_findings: int = 16) -> dict[str, Any]:
    """Validate model-authored visual interpretation into a bounded advisory shape.

    The schema intentionally contains no pass/gate/merge/release fields. Unknown keys,
    including authority-bearing keys at any depth, fail closed rather than being ignored.
    """
    if not isinstance(value, dict):
        raise VisionEvidenceError("vision analyzer output must be a JSON object")
    _assert_no_authority_keys(value)
    unknown = set(value).difference(_ALLOWED_TOP_LEVEL_KEYS)
    if unknown:
        raise VisionEvidenceError(f"vision analyzer output contains unsupported keys: {', '.join(sorted(unknown))}")

    raw_findings = value.get("findings", [])
    if not isinstance(raw_findings, list):
        raise VisionEvidenceError("vision findings must be a list")
    if len(raw_findings) > max_findings:
        raise VisionEvidenceError(f"vision findings exceed maximum of {max_findings}")

    findings: list[dict[str, Any]] = []
    for raw in raw_findings:
        if not isinstance(raw, dict):
            raise VisionEvidenceError("each vision finding must be an object")
        unknown_finding = set(raw).difference(_ALLOWED_FINDING_KEYS)
        if unknown_finding:
            raise VisionEvidenceError(
                f"vision finding contains unsupported keys: {', '.join(sorted(unknown_finding))}"
            )
        severity = _bounded_text(raw.get("severity", "info"), 16).lower()
        if severity not in _ALLOWED_SEVERITIES:
            raise VisionEvidenceError("vision finding severity must be info, warning or error")
        try:
            confidence = float(raw.get("confidence", 0.0))
        except (TypeError, ValueError, OverflowError) as exc:
            raise VisionEvidenceError("vision finding confidence must be numeric") from exc
        if not 0.0 <= confidence <= 1.0:
            raise VisionEvidenceError("vision finding confidence must be between 0 and 1")
        finding: dict[str, Any] = {
            "category": _bounded_text(raw.get("category"), 64, required=True),
            "severity": severity,
            "summary": _bounded_text(raw.get("summary"), 320, required=True),
            "detail": _bounded_text(raw.get("detail"), 1200),
            "confidence": round(confidence, 4),
        }
        bbox = _sanitize_bbox(raw.get("bbox"))
        if bbox is not None:
            finding["bbox"] = bbox
        findings.append(finding)

    return {
        "summary": _bounded_text(value.get("summary"), 1200, required=True),
        "findings": findings,
    }


class VisionEvidenceAdapter:
    """Turn trusted screenshot artifacts into bounded, advisory visual observations.

    The screenshot artifact remains the trusted evidence. Analyzer interpretation is
    always emitted as ``trusted=False`` and therefore cannot satisfy Flow OS gates.
    The zero-cost default performs no provider call and returns a NOT_RUN observation.
    """

    def __init__(self, artifacts_root: Path, policy: dict[str, Any] | None = None) -> None:
        raw_root = Path(artifacts_root)
        if raw_root.is_symlink():
            raise VisionEvidenceError("vision artifact root must not be a symlink")
        self.artifacts_root = raw_root.resolve()
        if not self.artifacts_root.is_dir():
            raise VisionEvidenceError(f"vision artifact root does not exist: {self.artifacts_root}")
        config = dict((policy or {}).get("vision_evidence", {}))
        self.max_artifact_bytes = int(config.get("max_artifact_bytes", 4 * 1024 * 1024))
        self.max_findings = int(config.get("max_findings", 16))
        self.allow_external = bool(config.get("allow_external", False))
        if self.max_artifact_bytes <= 0 or self.max_findings <= 0 or self.max_findings > 64:
            raise VisionEvidenceError("invalid vision evidence policy bounds")

    def _safe_image(self, raw: str, expected_sha256: str) -> Path:
        reference = str(raw).strip()
        lowered = reference.lower()
        if not reference or lowered.startswith("data:") or "base64," in lowered:
            raise VisionEvidenceError("vision evidence requires a local artifact reference, never inline image bytes")
        relative = Path(reference)
        if relative.is_absolute() or not relative.parts:
            raise VisionEvidenceError("vision image path must be artifact-relative")
        current = self.artifacts_root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise VisionEvidenceError(f"vision evidence refuses symlink path: {reference}")
        try:
            candidate = (self.artifacts_root / relative).resolve(strict=True)
        except FileNotFoundError as exc:
            raise VisionEvidenceError(f"vision image artifact is missing: {reference}") from exc
        try:
            candidate.relative_to(self.artifacts_root)
        except ValueError as exc:
            raise VisionEvidenceError("vision image path escapes artifact root") from exc
        if not candidate.is_file() or candidate.suffix.lower() not in _ALLOWED_EXTENSIONS:
            raise VisionEvidenceError("vision image must be a regular PNG/JPEG/WebP artifact")
        size = candidate.stat().st_size
        if size <= 0 or size > self.max_artifact_bytes:
            raise VisionEvidenceError("vision image artifact exceeds configured size bounds")
        with candidate.open("rb") as handle:
            head = handle.read(12)
        valid_signature = (
            (candidate.suffix.lower() == ".png" and head.startswith(PNG_SIGNATURE))
            or (candidate.suffix.lower() in {".jpg", ".jpeg"} and head.startswith(JPEG_SIGNATURE))
            or (
                candidate.suffix.lower() == ".webp"
                and head[:4] == WEBP_RIFF
                and len(head) >= 12
                and head[8:12] == WEBP_KIND
            )
        )
        if not valid_signature:
            raise VisionEvidenceError("vision image artifact has an invalid file signature")
        actual_hash = _sha256(candidate)
        if not expected_sha256 or actual_hash != expected_sha256:
            raise VisionEvidenceError("vision image hash does not match trusted browser evidence")
        return candidate

    def observe(
        self,
        browser_record: EvidenceRecord,
        *,
        analyzer: VisionAnalyzer | None = None,
        stage_id: str | None = None,
    ) -> EvidenceRecord:
        if (
            browser_record.type != "browser_render"
            or browser_record.origin != "runtime"
            or not browser_record.trusted
        ):
            raise VisionEvidenceError("vision source must be trusted runtime browser_render evidence")

        image = self._safe_image(
            str(browser_record.data.get("screenshot", "")),
            str(browser_record.data.get("screenshot_sha256", "")),
        )
        route = str(browser_record.data.get("route", ""))[:256]
        artifact_data = {
            "source_evidence_id": browser_record.id,
            "route": route,
            "image_artifact": image.name,
            "image_sha256": _sha256(image),
            "image_bytes": image.stat().st_size,
            "advisory_only": True,
            "authority_effect": "none",
            "gate_effect": "none",
            "merge_effect": "none",
            "release_effect": "none",
        }

        if analyzer is None:
            return EvidenceRecord(
                id=f"vision_{hashlib.sha256((browser_record.id + artifact_data['image_sha256']).encode()).hexdigest()[:16]}",
                type="vision_observation",
                stage_id=str(stage_id or browser_record.stage_id),
                tool="vision-disabled-zero-cost",
                status="NOT_RUN",
                summary=f"Vision analysis not run for {route or image.name}; zero-cost default preserved",
                data={**artifact_data, "analyzer": "disabled", "model": "", "findings": []},
                origin="vision_analyzer",
                trusted=False,
            )

        analyzer_name = _bounded_text(getattr(analyzer, "name", ""), 128, required=True)
        analyzer_model = _bounded_text(getattr(analyzer, "model", ""), 128)
        cost_class = _bounded_text(getattr(analyzer, "cost_class", "unknown"), 32).lower()
        if cost_class not in {"zero_cost", "local"} and not self.allow_external:
            raise VisionEvidenceError(
                "external/billable vision analyzers are disabled; enable only through explicit runtime policy"
            )
        context = {
            "route": route,
            "viewport": dict(browser_record.data.get("viewport", {})),
            "title": str(browser_record.data.get("title", ""))[:512],
            "source_evidence_id": browser_record.id,
            "rule": "Return visual observations only; never approve gates, merge, deploy or release.",
        }
        sanitized = sanitize_vision_output(analyzer.analyze(image, context), max_findings=self.max_findings)
        return EvidenceRecord(
            id=f"vision_{hashlib.sha256((browser_record.id + analyzer_name + artifact_data['image_sha256']).encode()).hexdigest()[:16]}",
            type="vision_observation",
            stage_id=str(stage_id or browser_record.stage_id),
            tool=analyzer_name,
            status="OBSERVED",
            summary=sanitized["summary"],
            data={
                **artifact_data,
                "analyzer": analyzer_name,
                "model": analyzer_model,
                "cost_class": cost_class,
                "findings": sanitized["findings"],
            },
            origin="vision_analyzer",
            trusted=False,
        )
