from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from core.contracts.evidence_provenance_schema import (
    EvidenceProvenanceManifest,
    EvidenceProvenanceRecord,
    SpecEvidenceLink,
)
from core.contracts.reference_evidence_schema import ReferenceEvidenceBundle


EVIDENCE_MARKER = re.compile(r"\[\[evidence:(EVID-[0-9a-f]{16})\]\]")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _stable_evidence_id(identity: dict[str, Any]) -> str:
    return "EVID-" + sha256_text(_canonical_json(identity))[:16]


def _string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return _canonical_json(value)


def _viewport_label(capture) -> str:
    viewport = capture.viewport
    return f"{viewport.label}:{viewport.width}x{viewport.height}"


def _record(
    *,
    status: str,
    kind: str,
    source_type: str,
    source_url: str,
    source_artifact: str,
    source_artifact_sha256: str,
    captured_at: str,
    viewport: str = "",
    state: str = "",
    selector: str = "",
    property_name: str = "",
    value: Any = "",
    locator: str,
) -> EvidenceProvenanceRecord:
    normalized_value = _string(value)
    identity = {
        "status": status,
        "kind": kind,
        "source_type": source_type,
        "source_url": source_url,
        "viewport": viewport,
        "state": state,
        "selector": selector,
        "property_name": property_name,
        "value": normalized_value,
        "locator": locator,
    }
    return EvidenceProvenanceRecord(
        evidence_id=_stable_evidence_id(identity),
        status=status,
        kind=kind,
        source_type=source_type,
        source_url=source_url,
        source_artifact=source_artifact,
        source_artifact_sha256=source_artifact_sha256,
        captured_at=captured_at,
        viewport=viewport,
        state=state,
        selector=selector,
        property_name=property_name,
        value=normalized_value[:6000],
        locator=locator,
    )


def build_reference_catalog(
    evidence_raw: str,
    *,
    source_artifact: str,
    source_sha256: str,
    max_records: int = 4000,
) -> list[EvidenceProvenanceRecord]:
    """Convert browser evidence into stable, individually addressable provenance records.

    IDs intentionally exclude capture timestamp and artifact path/hash so the same measured fact
    keeps the same ID across equivalent reruns. Source artifact metadata remains on each record.
    """
    bundle = ReferenceEvidenceBundle.model_validate_json(evidence_raw)
    records: list[EvidenceProvenanceRecord] = []
    seen: set[str] = set()

    def add(record: EvidenceProvenanceRecord) -> None:
        if record.evidence_id in seen or len(records) >= max_records:
            return
        seen.add(record.evidence_id)
        records.append(record)

    for page_index, page in enumerate(bundle.references):
        base = {
            "source_url": page.url,
            "source_artifact": source_artifact,
            "source_artifact_sha256": source_sha256,
            "captured_at": page.captured_at,
        }
        for name, value in page.document.model_dump().items():
            if value:
                add(_record(
                    status="VERIFIED", kind="document", source_type="document_metadata",
                    property_name=name, value=value, locator=f"references[{page_index}].document.{name}", **base,
                ))

        for capture_index, capture in enumerate(page.captures):
            viewport = _viewport_label(capture)
            capture_base = {**base, "viewport": viewport}
            for name, value in capture.root_custom_properties.items():
                add(_record(
                    status="VERIFIED", kind="style", source_type="computed_root_custom_property",
                    selector=":root", property_name=name, value=value,
                    locator=f"references[{page_index}].captures[{capture_index}].root_custom_properties.{name}",
                    **capture_base,
                ))
            for style_index, style in enumerate(capture.computed_styles):
                for name, value in style.properties.items():
                    add(_record(
                        status="VERIFIED", kind="style", source_type="computed_style",
                        selector=style.selector, property_name=name, value=value,
                        locator=f"references[{page_index}].captures[{capture_index}].computed_styles[{style_index}].properties.{name}",
                        **capture_base,
                    ))
                for name, value in style.custom_properties.items():
                    add(_record(
                        status="VERIFIED", kind="style", source_type="computed_custom_property",
                        selector=style.selector, property_name=name, value=value,
                        locator=f"references[{page_index}].captures[{capture_index}].computed_styles[{style_index}].custom_properties.{name}",
                        **capture_base,
                    ))
            for media_index, media in enumerate(capture.media_queries):
                add(_record(
                    status="VERIFIED", kind="responsive", source_type="cssom_media_query",
                    property_name="matches", value=media.matches, state=media.condition,
                    locator=f"references[{page_index}].captures[{capture_index}].media_queries[{media_index}]",
                    **capture_base,
                ))
            for asset_index, asset in enumerate(capture.assets):
                add(_record(
                    status="VERIFIED", kind="asset", source_type=asset.kind,
                    selector=asset.selector, property_name="url", value=asset.url or asset.declared_url,
                    state=asset.status,
                    locator=f"references[{page_index}].captures[{capture_index}].assets[{asset_index}]",
                    **capture_base,
                ))
            for palette_name, palette in (("css_colors", capture.css_colors), ("visual_palette", capture.visual_palette)):
                for color_index, color in enumerate(palette):
                    add(_record(
                        status=color.evidence, kind="color", source_type=color.source,
                        property_name=palette_name, value={"color": color.value, "weight": color.weight},
                        locator=f"references[{page_index}].captures[{capture_index}].{palette_name}[{color_index}]",
                        **capture_base,
                    ))
            if capture.screenshot:
                add(_record(
                    status="VERIFIED", kind="screenshot", source_type="browser_screenshot",
                    property_name="sha256", value=capture.screenshot.sha256,
                    state=capture.screenshot.path,
                    locator=f"references[{page_index}].captures[{capture_index}].screenshot",
                    **capture_base,
                ))

        for motion_index, motion in enumerate(page.motion):
            viewport = f"{motion.viewport.label}:{motion.viewport.width}x{motion.viewport.height}"
            motion_base = {**base, "viewport": viewport}
            for checkpoint_index, checkpoint in enumerate(motion.checkpoints):
                state = f"{checkpoint.label}@scrollY={checkpoint.scroll_y}"
                for name, value in checkpoint.root_custom_properties.items():
                    add(_record(
                        status="VERIFIED", kind="motion", source_type="runtime_root_custom_property",
                        selector=":root", property_name=name, value=value, state=state,
                        locator=f"references[{page_index}].motion[{motion_index}].checkpoints[{checkpoint_index}].root_custom_properties.{name}",
                        **motion_base,
                    ))
                for element_index, element in enumerate(checkpoint.elements):
                    for name, value in (
                        ("opacity", element.opacity), ("transform", element.transform),
                        ("position", element.position), ("filter", element.filter),
                        ("rect", element.rect.model_dump()),
                    ):
                        add(_record(
                            status="VERIFIED", kind="motion", source_type="runtime_element_state",
                            selector=element.selector, property_name=name, value=value, state=state,
                            locator=f"references[{page_index}].motion[{motion_index}].checkpoints[{checkpoint_index}].elements[{element_index}].{name}",
                            **motion_base,
                        ))
                for animation_index, animation in enumerate(checkpoint.animations):
                    add(_record(
                        status="VERIFIED", kind="motion", source_type="web_animation_api",
                        selector=animation.selector, property_name="timing",
                        value={
                            "duration": animation.duration, "delay": animation.delay,
                            "easing": animation.easing, "iterations": animation.iterations,
                            "play_state": animation.play_state,
                        },
                        state=state,
                        locator=f"references[{page_index}].motion[{motion_index}].checkpoints[{checkpoint_index}].animations[{animation_index}]",
                        **motion_base,
                    ))
            for listener_index, listener in enumerate(motion.listeners):
                add(_record(
                    status="VERIFIED", kind="interaction", source_type="event_listener_registration",
                    selector=listener.target, property_name=listener.event_type,
                    value={"capture": listener.capture, "once": listener.once, "passive": listener.passive},
                    locator=f"references[{page_index}].motion[{motion_index}].listeners[{listener_index}]",
                    **motion_base,
                ))
            for interaction_index, interaction in enumerate(motion.interactions):
                add(_record(
                    status="VERIFIED", kind="interaction", source_type="runtime_interaction_delta",
                    selector=interaction.selector, property_name="changed_properties",
                    value=interaction.changed_properties, state=interaction.state,
                    locator=f"references[{page_index}].motion[{motion_index}].interactions[{interaction_index}]",
                    **motion_base,
                ))

        # DOM records are valuable but lower priority than authored/runtime state, so add them last.
        for capture_index, capture in enumerate(page.captures):
            viewport = _viewport_label(capture)
            for node_index, node in enumerate(capture.dom):
                add(_record(
                    status="VERIFIED", kind="dom", source_type="dom_traversal",
                    selector=node.selector, property_name="node",
                    value={"tag": node.tag, "id": node.id, "classes": node.classes, "rect": node.rect.model_dump()},
                    state="visible" if node.visible else "not-visible",
                    locator=f"references[{page_index}].captures[{capture_index}].dom[{node_index}]",
                    source_url=page.url, source_artifact=source_artifact,
                    source_artifact_sha256=source_sha256, captured_at=page.captured_at,
                    viewport=viewport,
                ))

    return records


def catalog_sha256(records: Iterable[EvidenceProvenanceRecord]) -> str:
    payload = [record.model_dump(exclude={"source_artifact", "source_artifact_sha256", "captured_at"}) for record in records]
    return sha256_text(_canonical_json(payload))


def render_evidence_digest(records: list[EvidenceProvenanceRecord], *, limit: int = 72) -> str:
    if not records:
        return "N/A_JUSTIFIED — no measured reference evidence was available for this run."
    priority = {"document": 0, "style": 1, "responsive": 2, "motion": 3, "interaction": 4, "asset": 5, "color": 6, "screenshot": 7, "dom": 8}
    selected = sorted(records, key=lambda item: (priority.get(item.kind, 99), item.evidence_id))[:limit]
    lines = []
    for record in selected:
        subject = record.selector or record.state or record.source_url
        property_label = f" {record.property_name}=" if record.property_name else " "
        value = record.value.replace("\n", " ")[:260]
        context = " | ".join(part for part in (record.viewport, record.state) if part)
        suffix = f" @ {context}" if context else ""
        lines.append(
            f"- [[evidence:{record.evidence_id}]] **{record.status}** `{record.source_type}` — "
            f"`{subject}`{property_label}`{value}`{suffix}"
        )
    if len(records) > len(selected):
        lines.append(f"- Catalog contains {len(records)} records; digest shows {len(selected)} high-priority anchors.")
    return "\n".join(lines)


def scan_spec_links(spec_text: str, valid_ids: set[str]) -> list[SpecEvidenceLink]:
    links: list[SpecEvidenceLink] = []
    for line_number, raw_line in enumerate(spec_text.splitlines(), start=1):
        ids = [item for item in EVIDENCE_MARKER.findall(raw_line) if item in valid_ids]
        if ids:
            links.append(
                SpecEvidenceLink(
                    line_number=line_number,
                    statement=raw_line.strip()[:6000],
                    evidence_ids=list(dict.fromkeys(ids)),
                )
            )
    return links


def build_provenance_manifest(
    *,
    profile: str,
    source_artifact: str,
    source_sha256: str,
    records: list[EvidenceProvenanceRecord],
    spec_text: str,
    warnings: list[str] | None = None,
) -> EvidenceProvenanceManifest:
    return EvidenceProvenanceManifest(
        spec_profile=profile,
        source_artifact=source_artifact,
        source_sha256=source_sha256,
        catalog_sha256=catalog_sha256(records),
        spec_sha256=sha256_text(spec_text),
        records=records,
        spec_links=scan_spec_links(spec_text, {record.evidence_id for record in records}),
        downstream_consumers=[
            "02-FULL-BUILD-SPEC.md",
            "03-IMPLEMENTATION-PROMPT.md",
            "04-QA-REMEDIATION-PROMPT.md",
            "implementation",
            "browser_qa",
            "visual_qa",
            "repair",
        ],
        warnings=warnings or [],
    )


def load_verified_reference_catalog(reference_analysis: str) -> tuple[list[EvidenceProvenanceRecord], str, str, list[str]]:
    """Load deep evidence only when the ReferenceBoard digest still matches the artifact bytes."""
    warnings: list[str] = []
    try:
        board = json.loads(reference_analysis or "{}")
    except json.JSONDecodeError:
        return [], "", "", ["ReferenceBoard is not valid JSON; provenance unavailable."]
    source_artifact = str(board.get("evidence_artifact") or "")
    expected_sha = str(board.get("evidence_sha256") or "")
    if not source_artifact or not expected_sha:
        return [], "", "", ["No deep reference evidence artifact is declared by ReferenceBoard."]
    path = Path(source_artifact)
    if not path.is_file():
        return [], source_artifact, expected_sha, ["Declared deep reference evidence artifact is missing."]
    raw_bytes = path.read_bytes()
    actual_sha = sha256_bytes(raw_bytes)
    if actual_sha != expected_sha:
        return [], source_artifact, expected_sha, ["Deep reference evidence digest mismatch; provenance rejected as stale/tampered."]
    raw = raw_bytes.decode("utf-8")
    records = build_reference_catalog(raw, source_artifact=source_artifact, source_sha256=actual_sha)
    return records, source_artifact, actual_sha, warnings
