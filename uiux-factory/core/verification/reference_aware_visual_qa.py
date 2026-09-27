from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from core.contracts.browser_qa_schema import BrowserQAResult, RouteViewportEvidence
from core.contracts.design_context_schema import ReferenceBoard
from core.contracts.reference_evidence_schema import ReferenceEvidenceBundle, ReferenceCaptureEvidence
from core.contracts.reference_visual_qa_schema import (
    ReferenceVisualComparison,
    ReferenceVisualQAResult,
)


PROFILE_PATTERN = re.compile(r"Profile:\s*`(pixel_faithful|preserve_and_extend|redesign|original_design)`")


class ReferenceAwareVisualQA:
    """Profile-aware reference comparison.

    A reference is evidence, not permission to clone. Whole-page pixel similarity is a hard gate
    only for an explicitly frozen `pixel_faithful` spec. `preserve_and_extend` requires an explicit
    protected-surface contract before any strict visual comparison can block. Redesign/original
    work is judged against the frozen spec/art direction instead of old-reference pixel similarity.
    """

    STRICT_MAE_MAX = 0.08
    STRICT_DIFF_RATIO_MAX = 0.20
    CHANNEL_TOLERANCE = 24

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _resolve_path(raw: str, *roots: Path) -> Path | None:
        if not raw:
            return None
        path = Path(raw)
        candidates = [path] if path.is_absolute() else [root / path for root in roots]
        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()
        return None

    @classmethod
    def _profile(cls, *, spec_manifest: Path | None, full_spec: Path) -> str:
        if spec_manifest and spec_manifest.is_file():
            try:
                payload = json.loads(spec_manifest.read_text(encoding="utf-8"))
                value = str(payload.get("spec_profile", ""))
                if value in {"pixel_faithful", "preserve_and_extend", "redesign", "original_design"}:
                    return value
            except (json.JSONDecodeError, OSError):
                pass
        text = full_spec.read_text(encoding="utf-8")
        match = PROFILE_PATTERN.search(text)
        if match:
            return match.group(1)
        raise RuntimeError("Reference-aware visual QA cannot determine the frozen spec profile.")

    @staticmethod
    def _reference_bundle(reference_board_path: Path) -> tuple[ReferenceEvidenceBundle | None, Path | None, list[str]]:
        warnings: list[str] = []
        board = ReferenceBoard.model_validate_json(reference_board_path.read_text(encoding="utf-8"))
        if not board.evidence_artifact or not board.evidence_sha256:
            return None, None, ["No deep reference evidence artifact declared by ReferenceBoard."]
        evidence_path = Path(board.evidence_artifact)
        if not evidence_path.is_file():
            return None, evidence_path, ["Declared reference evidence artifact is missing."]
        actual = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        if actual != board.evidence_sha256:
            return None, evidence_path, ["Reference evidence digest mismatch; comparison refused."]
        return ReferenceEvidenceBundle.model_validate_json(evidence_path.read_text(encoding="utf-8")), evidence_path, warnings

    @staticmethod
    def _existing_reference_captures(bundle: ReferenceEvidenceBundle) -> list[tuple[str, ReferenceCaptureEvidence]]:
        rows: list[tuple[str, ReferenceCaptureEvidence]] = []
        for page in bundle.references:
            if page.role != "existing_website" or page.status == "unavailable":
                continue
            for capture in page.captures:
                if capture.screenshot:
                    rows.append((page.url, capture))
        return rows

    @staticmethod
    def _target_candidates(browser: BrowserQAResult) -> list[RouteViewportEvidence]:
        # Existing-site reference capture maps to the canonical root route unless a future
        # route-mapping contract explicitly says otherwise.
        return [row for row in browser.evidence if row.route == "/" and row.status == "passed"]

    @classmethod
    def _image_metrics(cls, reference_path: Path, target_path: Path) -> tuple[float, float]:
        # Lazy import keeps lightweight foundation tests independent of Pillow runtime deps.
        from PIL import Image, ImageChops, ImageStat

        with Image.open(reference_path) as reference_raw, Image.open(target_path) as target_raw:
            reference = reference_raw.convert("RGB")
            target = target_raw.convert("RGB")
            if target.size != reference.size:
                target = target.resize(reference.size, Image.Resampling.LANCZOS)
            diff = ImageChops.difference(reference, target)
            stats = ImageStat.Stat(diff)
            mean = sum(stats.mean[:3]) / 3.0
            normalized_mae = max(0.0, min(1.0, mean / 255.0))

            pixels = diff.load()
            width, height = diff.size
            differing = 0
            total = max(1, width * height)
            threshold = cls.CHANNEL_TOLERANCE
            for y in range(height):
                for x in range(width):
                    red, green, blue = pixels[x, y]
                    if max(red, green, blue) > threshold:
                        differing += 1
            return normalized_mae, differing / total

    @staticmethod
    def _protected_surface_contract(full_spec: Path) -> bool:
        text = full_spec.read_text(encoding="utf-8")
        markers = (
            "[[reference-visual-surface:",
            "P0_BYTE_EXACT",
            "VISUAL_EXACT",
            "pixel-exact protected surface",
        )
        return any(marker in text for marker in markers)

    @classmethod
    def evaluate(
        cls,
        *,
        browser_report_path: Path,
        reference_analysis_path: Path,
        full_spec_path: Path,
        spec_manifest_path: Path | None = None,
    ) -> ReferenceVisualQAResult:
        browser_report_path = Path(browser_report_path).resolve()
        reference_analysis_path = Path(reference_analysis_path).resolve()
        full_spec_path = Path(full_spec_path).resolve()
        spec_manifest_path = Path(spec_manifest_path).resolve() if spec_manifest_path else None

        profile = cls._profile(spec_manifest=spec_manifest_path, full_spec=full_spec_path)
        if profile == "original_design":
            return ReferenceVisualQAResult(
                spec_profile=profile,
                mode="spec_only",
                status="inapplicable",
                blocking=False,
                policy_id="original-design-spec-only-v1",
                notes=["Original design has no visual-fidelity obligation to a reference. Evaluate rendered output against the frozen spec and quality rubric."],
            )
        if profile == "redesign":
            return ReferenceVisualQAResult(
                spec_profile=profile,
                mode="spec_only",
                status="inapplicable",
                blocking=False,
                policy_id="redesign-new-art-direction-v1",
                notes=["Redesign must not be penalized for visual distance from the old/reference UI. Preserve product/data/journey truth through the frozen spec instead."],
            )

        if profile == "preserve_and_extend" and not cls._protected_surface_contract(full_spec_path):
            return ReferenceVisualQAResult(
                spec_profile=profile,
                mode="protected_surfaces",
                status="cantTell",
                blocking=False,
                policy_id="preserve-explicit-surfaces-v1",
                notes=[
                    "No explicit pixel-exact protected-surface marker exists in the frozen spec, so whole-page reference similarity is advisory only and cannot block.",
                    "Behavior/API/visual-DNA preservation remains governed by the frozen Preserve Contract and normal rendered QA.",
                ],
            )

        bundle, evidence_path, warnings = cls._reference_bundle(reference_analysis_path)
        if bundle is None:
            return ReferenceVisualQAResult(
                spec_profile=profile,
                mode="strict_reference" if profile == "pixel_faithful" else "protected_surfaces",
                status="cantTell",
                blocking=profile == "pixel_faithful",
                policy_id="pixel-faithful-reference-v1" if profile == "pixel_faithful" else "preserve-explicit-surfaces-v1",
                notes=warnings + ["Strict fidelity cannot PASS without verified reference screenshots."],
            )

        browser = BrowserQAResult.model_validate_json(browser_report_path.read_text(encoding="utf-8"))
        references = cls._existing_reference_captures(bundle)
        targets = cls._target_candidates(browser)
        run_root = reference_analysis_path.parent
        target_root = browser_report_path.parent
        comparisons: list[ReferenceVisualComparison] = []

        for reference_url, capture in references:
            screenshot = capture.screenshot
            if screenshot is None:
                continue
            ref_path = cls._resolve_path(screenshot.path, run_root, evidence_path.parent if evidence_path else run_root)
            if ref_path is None:
                continue
            exact_target = next(
                (
                    row for row in targets
                    if row.viewport.width == capture.viewport.width and row.viewport.height == capture.viewport.height
                ),
                None,
            )
            if exact_target is None:
                continue
            target_path = cls._resolve_path(exact_target.screenshot, target_root, run_root)
            if target_path is None:
                continue
            mae, ratio = cls._image_metrics(ref_path, target_path)
            passed = mae <= cls.STRICT_MAE_MAX and ratio <= cls.STRICT_DIFF_RATIO_MAX
            comparisons.append(
                ReferenceVisualComparison(
                    route=exact_target.route,
                    viewport=f"{capture.viewport.width}x{capture.viewport.height}",
                    reference_url=reference_url,
                    reference_screenshot=str(ref_path),
                    target_screenshot=str(target_path),
                    reference_sha256=cls._sha256(ref_path),
                    target_sha256=cls._sha256(target_path),
                    normalized_mae=round(mae, 6),
                    differing_pixel_ratio=round(ratio, 6),
                    tolerance_per_channel=cls.CHANNEL_TOLERANCE,
                    status="passed" if passed else "failed",
                    blocking=profile == "pixel_faithful",
                    evidence=(
                        f"MAE={mae:.4f} (max {cls.STRICT_MAE_MAX:.2f}); pixels above channel tolerance "
                        f"{ratio:.4f} (max {cls.STRICT_DIFF_RATIO_MAX:.2f})."
                    ),
                )
            )

        if not comparisons:
            return ReferenceVisualQAResult(
                spec_profile=profile,
                mode="strict_reference" if profile == "pixel_faithful" else "protected_surfaces",
                status="cantTell",
                blocking=profile == "pixel_faithful",
                policy_id="pixel-faithful-reference-v1" if profile == "pixel_faithful" else "preserve-explicit-surfaces-v1",
                notes=warnings + [
                    "No exact viewport pair could be compared. Pixel-faithful work must provide comparable rendered reference and target screenshots; preserve-and-extend remains non-blocking unless a protected surface can be measured."
                ],
            )

        failed = any(row.status == "failed" for row in comparisons)
        if profile == "pixel_faithful":
            status = "failed" if failed else "passed"
            blocking = failed
            mode = "strict_reference"
            policy_id = "pixel-faithful-reference-v1"
        else:
            # Until per-selector target crops are captured, these same-viewport measurements are
            # supporting evidence only; never use whole-page distance to reject an extension.
            status = "passed" if not failed else "cantTell"
            blocking = False
            mode = "protected_surfaces"
            policy_id = "preserve-explicit-surfaces-v1"

        return ReferenceVisualQAResult(
            spec_profile=profile,
            mode=mode,
            status=status,
            blocking=blocking,
            policy_id=policy_id,
            comparisons=comparisons,
            notes=warnings + [
                "Image metrics are browser-output measurements, not proof of semantic correctness. Human/semantic visual review remains required.",
                "Whole-page metrics never become a blocking redesign/original-design criterion.",
            ],
        )
