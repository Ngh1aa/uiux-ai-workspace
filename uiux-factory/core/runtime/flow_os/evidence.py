from __future__ import annotations

import hashlib
import json
import struct
import uuid
import zlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


TRUSTED_EVIDENCE_TYPES = frozenset({
    "design_contract_check",
    "file_read",
    "file_change",
    "search_result",
    "command_result",
    "validator_result",
    "artifact",
    "tool_observation",
    "browser_render",
    "deployment_result",
})


@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    type: str
    stage_id: str
    tool: str
    status: str
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    origin: str = "runtime"
    trusted: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceRecord":
        record = cls(
            id=str(payload["id"]),
            type=str(payload["type"]),
            stage_id=str(payload["stage_id"]),
            tool=str(payload["tool"]),
            status=str(payload["status"]),
            summary=str(payload.get("summary", "")),
            data=dict(payload.get("data", {})),
            origin=str(payload.get("origin", "runtime")),
            trusted=bool(payload.get("trusted", True)),
            created_at=str(payload.get("created_at", "")) or datetime.now(timezone.utc).isoformat(),
        )
        if record.trusted and (record.origin != "runtime" or record.type not in TRUSTED_EVIDENCE_TYPES):
            raise ValueError("trusted evidence must be emitted by the runtime with a recognized evidence type")
        return record


def _record_type(tool: str, result: Any) -> str:
    if tool == 'check_design_decisions':
        return 'design_contract_check'
    if tool in {"write_project_file", "write_artifact", "replace_text"}:
        return "file_change"
    if tool in {"search_text", "list_files_recursive"}:
        return "search_result"
    if tool in {"read_text", "list_files"}:
        return "file_read"
    if tool == "run_target_command":
        return "command_result"
    if tool == "run_validator":
        return "validator_result"
    if tool == "release_action":
        return "tool_observation"
    if isinstance(result, dict) and result.get("path"):
        return "artifact"
    return "tool_observation"


def evidence_from_tool(stage_id: str, tool: str, result: Any) -> EvidenceRecord:
    if tool == "read_skill_section":
        raw = dict(result) if isinstance(result, dict) else {}
        data = {
            key: raw[key]
            for key in (
                "skill",
                "section_id",
                "heading",
                "part",
                "parts",
                "start_line",
                "end_line",
                "sha256",
                "chars",
                "retrievals_used",
                "retrievals_limit",
                "retrieved_chars_used",
                "retrieved_chars_limit",
            )
            if key in raw
        }
        return EvidenceRecord(
            id=f"ev_{uuid.uuid4().hex[:16]}",
            type="skill_section_read",
            stage_id=str(stage_id),
            tool=str(tool),
            status="OBSERVED",
            summary=(
                f"runtime retrieved routed skill section "
                f"{data.get('skill', '(unknown)')}:{data.get('section_id', '(unknown)')}"
            ),
            data=data,
            origin="runtime",
            trusted=False,
        )

    if tool == "browser_observe":
        raw = dict(result) if isinstance(result, dict) else {}
        data = {
            "route": str(raw.get("route", ""))[:1000],
            "url": str(raw.get("url", ""))[:2000],
            "title": str(raw.get("title", ""))[:500],
            "viewport": dict(raw.get("viewport", {})) if isinstance(raw.get("viewport"), dict) else {},
            "screenshot": str(raw.get("screenshot", ""))[:500],
            "screenshot_sha256": str(raw.get("screenshot_sha256", ""))[:128],
            "browser_evidence_status": str(raw.get("browser_evidence_status", ""))[:32],
            "dom_excerpt_sha256": str(raw.get("dom_excerpt_sha256", ""))[:128],
            "aria_snapshot_sha256": str(raw.get("aria_snapshot_sha256", ""))[:128],
            "element_count": len(raw.get("elements", [])) if isinstance(raw.get("elements"), list) else 0,
            "console_message_count": len(raw.get("console_messages", [])) if isinstance(raw.get("console_messages"), list) else 0,
            "console_error_count": len(raw.get("console_errors", [])) if isinstance(raw.get("console_errors"), list) else 0,
            "page_error_count": len(raw.get("page_errors", [])) if isinstance(raw.get("page_errors"), list) else 0,
            "failed_request_count": len(raw.get("failed_requests", [])) if isinstance(raw.get("failed_requests"), list) else 0,
            "blocked_request_count": len(raw.get("blocked_requests", [])) if isinstance(raw.get("blocked_requests"), list) else 0,
        }
        return EvidenceRecord(
            id=f"ev_{uuid.uuid4().hex[:16]}",
            type="browser_observation",
            stage_id=str(stage_id),
            tool=str(tool),
            status="OBSERVED",
            summary=f"runtime exposed bounded browser observation for {data['route'] or '(unknown route)'}",
            data=data,
            origin="runtime",
            trusted=False,
        )

    evidence_type = _record_type(tool, result)
    data = dict(result) if isinstance(result, dict) else {"value": result}
    if evidence_type in {"command_result", "validator_result", "design_contract_check"}:
        returncode = int(data.get("returncode", 0))
        status = "PASS" if returncode == 0 else "FAIL"
        summary = f"{tool} exited with code {returncode}"
    elif evidence_type == "file_change":
        status = "PASS"
        summary = f"runtime changed {data.get('path', 'a workspace file')}"
    elif evidence_type == "search_result":
        status = "OBSERVED"
        count = len(data.get("matches", data.get("items", []))) if isinstance(data, dict) else 0
        summary = f"runtime observed {count} search/list result(s)"
    elif evidence_type == "file_read":
        status = "OBSERVED"
        summary = f"runtime read {data.get('path', 'project evidence')}"
    else:
        status = "OBSERVED"
        summary = f"runtime observed {tool} result"
    return EvidenceRecord(
        id=f"ev_{uuid.uuid4().hex[:16]}",
        type=evidence_type,
        stage_id=str(stage_id),
        tool=str(tool),
        status=status,
        summary=summary,
        data=data,
    )


def provider_claim_records(stage_id: str, claims: list[str]) -> list[dict[str, Any]]:
    """Preserve provider claims for traceability without upgrading them to evidence."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "id": f"claim_{uuid.uuid4().hex[:16]}",
            "type": "provider_claim",
            "stage_id": str(stage_id),
            "tool": "provider",
            "status": "CLAIMED",
            "summary": str(claim),
            "data": {},
            "origin": "provider",
            "trusted": False,
            "created_at": now,
        }
        for claim in claims
    ]


def _trusted_records(records: list[dict[str, Any]]) -> list[EvidenceRecord]:
    trusted: list[EvidenceRecord] = []
    for payload in records:
        try:
            record = EvidenceRecord.from_dict(dict(payload))
        except (KeyError, TypeError, ValueError):
            continue
        if record.trusted and record.origin == "runtime":
            trusted.append(record)
    return trusted


def trusted_stage_evidence(records: list[dict[str, Any]], stage_id: str) -> list[EvidenceRecord]:
    return [record for record in _trusted_records(records) if record.stage_id == stage_id]


def _evidence_channel(record: EvidenceRecord) -> tuple[Any, ...]:
    """Identify observations where a later retry supersedes an earlier result."""
    if record.type == "validator_result":
        return (record.type, record.tool, str(record.data.get("name", "")))
    if record.type == "command_result":
        argv = tuple(str(item) for item in record.data.get("argv", []))
        return (record.type, record.tool, argv, str(record.data.get("cwd", ".")))
    if record.type == "browser_render":
        viewport = record.data.get("viewport", {})
        if isinstance(viewport, dict):
            viewport_key = tuple(sorted((str(key), str(value)) for key, value in viewport.items()))
        else:
            viewport_key = str(viewport)
        return (record.type, str(record.data.get("route", "")), viewport_key)
    path = str(record.data.get("path", ""))
    if path:
        return (record.type, record.tool, path)
    return (record.type, record.tool)


def effective_evidence(records: list[dict[str, Any]]) -> list[EvidenceRecord]:
    """Return the latest trusted record per stage + evidence channel.

    Release readiness must evaluate the repaired current state, not permanently block
    because an earlier attempt failed. A later retry only supersedes evidence from the
    same stage and channel; unrelated evidence can never hide a failure.
    """
    latest: dict[tuple[Any, ...], EvidenceRecord] = {}
    for record in _trusted_records(records):
        latest[(record.stage_id, *_evidence_channel(record))] = record
    return list(latest.values())


def effective_stage_evidence(records: list[dict[str, Any]], stage_id: str) -> list[EvidenceRecord]:
    """Return the latest trusted record per evidence channel for one stage."""
    return [record for record in effective_evidence(records) if record.stage_id == stage_id]


def _valid_png(raw: bytes) -> bool:
    """Check encoded PNG structure and CRCs without optional image dependencies."""
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    offset = 8
    kinds: list[bytes] = []
    compressed = bytearray()
    expected_bytes = 0
    while offset + 12 <= len(raw):
        size = struct.unpack(">I", raw[offset:offset + 4])[0]
        end = offset + size + 12
        if end > len(raw):
            return False
        kind = raw[offset + 4:offset + 8]
        payload = raw[offset + 8:offset + 8 + size]
        checksum = struct.unpack(">I", raw[end - 4:end])[0]
        if checksum != zlib.crc32(kind + payload):
            return False
        if not kinds:
            if kind != b"IHDR" or size != 13:
                return False
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
            if (not width or not height or depth not in depths.get(color, set())
                    or compression or filtering or interlace not in {0, 1}):
                return False
            channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
            passes = ((0, 0, 1, 1),) if not interlace else (
                (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
                (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2),
            )
            for x, y, dx, dy in passes:
                columns = max(0, (width - x + dx - 1) // dx)
                rows = max(0, (height - y + dy - 1) // dy)
                if columns and rows:
                    expected_bytes += (1 + (columns * channels * depth + 7) // 8) * rows
        kinds.append(kind)
        if kind == b"IDAT":
            compressed.extend(payload)
        if kind == b"IEND":
            if size or end != len(raw) or not compressed:
                return False
            # Stream output in bounded chunks; full-page captures may be tall.
            decoder = zlib.decompressobj()
            remaining = bytes(compressed)
            decoded_bytes = 0
            try:
                while remaining:
                    decoded_bytes += len(decoder.decompress(remaining, 1024 * 1024))
                    if decoded_bytes > expected_bytes:
                        return False
                    remaining = decoder.unconsumed_tail
            except zlib.error:
                return False
            return decoder.eof and not decoder.unused_data and decoded_bytes == expected_bytes
        offset = end
    return False


def browser_render_errors(record: EvidenceRecord) -> list[str]:
    """Recheck capture provenance and current image bytes at acceptance time."""
    data = record.data
    if record.type != "browser_render" or record.status != "PASS" or not record.trusted or record.origin != "runtime":
        return ["browser render must be a PASS capture"]
    route = data.get("route")
    viewport = data.get("viewport")
    if not isinstance(route, str) or not route.startswith("/") or route.startswith("//"):
        return ["browser render requires a same-origin route"]
    try:
        parsed = urlsplit(str(data.get("url", "")))
        parsed_route = urlsplit(route)
    except ValueError:
        return ["browser render URL/route is malformed"]
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ["browser render requires its captured URL"]
    if parsed_route.path != parsed.path or parsed_route.query != parsed.query:
        return ["browser render route does not match captured URL"]
    if not isinstance(viewport, dict) or any(
        isinstance(viewport.get(edge), bool) or not isinstance(viewport.get(edge), int)
        or viewport[edge] <= 0 for edge in ("width", "height")
    ):
        return ["browser render requires positive viewport width and height"]
    root_raw = data.get("artifact_root")
    if not isinstance(root_raw, str) or not Path(root_raw).is_absolute():
        return ["browser render requires its runtime artifact root"]
    root = Path(root_raw)
    try:
        from core.runtime.flow_os.browser_evidence import PlaywrightBrowserEvidenceAdapter

        adapter = PlaywrightBrowserEvidenceAdapter(root.parent, {
            "browser_evidence": {"max_artifact_bytes": data.get("max_artifact_bytes", 4 * 1024 * 1024)}
        })
        root = adapter._artifact_root(root)
        image = adapter._safe_artifact(root, str(data.get("screenshot", "")), require_png=True)
        raw = image.read_bytes()
        if data.get("screenshot_sha256") != hashlib.sha256(raw).hexdigest():
            return ["browser render screenshot hash does not match current file (stale evidence)"]
        if not _valid_png(raw):
            return ["browser render screenshot is not a structurally valid PNG image"]
        width, height = struct.unpack(">II", raw[16:24])
        if width != viewport["width"] or height < viewport["height"]:
            return ["browser render image dimensions do not match captured viewport"]
        observation = adapter._safe_artifact(root, str(data.get("evidence_json", "")))
        if data.get("evidence_sha256") != hashlib.sha256(observation.read_bytes()).hexdigest():
            return ["browser render observation hash does not match current file (stale evidence)"]
        payload = json.loads(observation.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or any(
            payload.get(key) != data.get(key) for key in ("route", "url", "viewport", "screenshot")
        ):
            return ["browser render metadata does not match captured route/viewport/image"]
        if payload.get("pageErrors") or payload.get("failedRequests") or payload.get("blockedRequests") or any(
            isinstance(item, dict) and item.get("type") == "error" for item in payload.get("consoleMessages", [])
        ):
            return ["browser render observation contains failing browser signals"]
    except (OSError, TypeError, ValueError, RuntimeError) as error:
        return [f"browser render artifact validation failed: {error}"]
    return []


def native_browser_evidence_errors(report: dict[str, Any], artifact_root: Path) -> list[str]:
    """Native BrowserQA uses the same PNG/hash checks, with its declared route matrix."""
    root = Path(artifact_root).resolve()
    errors: list[str] = []
    expected = {(route, viewport.get("width"), viewport.get("height"))
                for route in report.get("routes", []) for viewport in report.get("viewports", [])}
    seen = set()
    try:
        base = urlsplit(str(report.get("base_url", "")))
    except ValueError:
        return ["browser report URL is malformed"]
    if base.scheme not in {"http", "https"} or not base.hostname or not expected:
        errors.append("browser report requires a URL and nonempty route/viewport matrix")
    for item in report.get("evidence", []):
        try:
            route = str(item.get("route", ""))
            parsed = urlsplit(route)
            viewport = dict(item.get("viewport") or {})
            key = (route, viewport.get("width"), viewport.get("height"))
            path = Path(str(item.get("screenshot", ""))).resolve()
            if (not route.startswith("/") or parsed.netloc or parsed.scheme or key not in expected
                    or any(type(viewport.get(edge)) is not int or viewport[edge] <= 0 for edge in ("width", "height"))
                    or not path.is_relative_to(root) or not path.is_file()):
                raise ValueError("capture route, viewport or screenshot path is invalid")
            raw = path.read_bytes()
            if not _valid_png(raw) or item.get("screenshot_sha256") != hashlib.sha256(raw).hexdigest():
                raise ValueError("capture image is invalid or hash is missing/stale")
            width, height = struct.unpack(">II", raw[16:24])
            if width != viewport["width"] or height < viewport["height"]:
                raise ValueError("capture image dimensions do not match viewport")
            if item.get("status") != "passed":
                raise ValueError("capture has failed browser QA")
            seen.add(key)
        except (TypeError, ValueError, OSError) as exc:
            errors.append(str(exc))
    if expected.difference(seen):
        errors.append("browser report is missing valid captures for declared routes/viewports")
    return errors


def gate_evidence_errors(
    gates: list[dict[str, Any]],
    stage_id: str,
    records: list[dict[str, Any]],
    agent: str = "",
) -> list[str]:
    """Evaluate typed evidence requirements without treating model prose as proof."""
    effective = effective_stage_evidence(records, stage_id)
    available = {record.type for record in effective if record.status != "FAIL" and record.type != "browser_render"}
    errors: list[str] = []
    for record in effective:
        if record.status == "FAIL":
            errors.append(f"runtime evidence failed: {record.type} via {record.tool} ({record.summary})")
        elif record.type == "browser_render":
            render_errors = browser_render_errors(record)
            errors.extend(render_errors)
            if not render_errors:
                available.add("browser_render")

    role_defaults = {
        "research": {"file_read", "search_result", "validator_result", "command_result"},
        "implementation": {"file_change", "validator_result", "command_result"},
        "qa": {"validator_result", "command_result", "browser_render"},
        "development": set(TRUSTED_EVIDENCE_TYPES),
    }
    for gate in gates:
        if gate.get("approval") == "human":
            continue
        gate_id = str(gate.get("id", "unnamed"))
        if gate_id in {"rendered-qa", "prototype-experience-qa", "rendered-check", "micro-rendered-check",
                       "page-rendered-check", "rendered-recruiter-path"} and "browser_render" not in available:
            errors.append(f"gate {gate_id} missing typed evidence: browser_render")
            continue
        declared = gate.get("evidence_types")
        if declared is not None:
            required = {str(item) for item in declared}
            missing = sorted(required.difference(available))
            if missing:
                errors.append(f"gate {gate_id} missing typed evidence: {', '.join(missing)}")
            if 'design_contract_check' in required:
                phase = gate.get('design_phase', 'design')
                version = gate.get('design_contract_version')
                if not any(record.type == 'design_contract_check' and record.status == 'PASS' and record.data.get('phase') == phase for record in effective):
                    errors.append(f"gate {gate_id} requires canonical design check phase={phase}; file length, general validators and provider prose cannot substitute")
                elif version and not any(record.type == 'design_contract_check' and record.status == 'PASS' and record.data.get('phase') == phase and record.data.get('contract_version') == version for record in effective):
                    errors.append(f"gate {gate_id} requires design contract version={version}; a legacy layout receipt cannot satisfy multi-axis direction requirements")
            continue
        acceptable = role_defaults.get(agent, set(TRUSTED_EVIDENCE_TYPES))
        if not available.intersection(acceptable):
            errors.append(f"gate {gate_id} has no trusted runtime evidence for stage role {agent or '(unknown)'}")
    return errors
