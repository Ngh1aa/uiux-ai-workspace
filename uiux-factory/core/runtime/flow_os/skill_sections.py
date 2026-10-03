from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.runtime.flow_os.safe_read import SafeReader

_RUN_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_PUBLIC_INDEX = "skill-section-index.json"
_PRIVATE_REGISTRY = "skill-section-registry.json"


class SkillSectionError(ValueError):
    """Raised when section indexing or retrieval violates the runtime contract."""


@dataclass(frozen=True)
class SkillSectionPolicy:
    enabled: bool = True
    max_sections_per_skill: int = 64
    max_section_chars: int = 12000
    max_retrievals_per_stage: int = 24
    max_total_retrieved_chars: int = 120000
    max_index_chars: int = 60000

    @classmethod
    def from_policy(cls, policy_doc: dict[str, Any]) -> "SkillSectionPolicy":
        raw = policy_doc.get("jit_skill_sections", {})
        if not isinstance(raw, dict):
            raise SkillSectionError("runtime-policy jit_skill_sections must be an object")
        enabled = raw.get("enabled", True)
        if not isinstance(enabled, bool):
            raise SkillSectionError("jit_skill_sections.enabled must be a boolean")

        def bounded_int(name: str, default: int, low: int, high: int) -> int:
            value = raw.get(name, default)
            if isinstance(value, bool) or not isinstance(value, int):
                raise SkillSectionError(f"jit_skill_sections.{name} must be an integer")
            if value < low or value > high:
                raise SkillSectionError(
                    f"jit_skill_sections.{name} must be between {low} and {high}"
                )
            return value

        return cls(
            enabled=enabled,
            max_sections_per_skill=bounded_int("max_sections_per_skill", 64, 1, 256),
            max_section_chars=bounded_int("max_section_chars", 12000, 256, 100000),
            max_retrievals_per_stage=bounded_int("max_retrievals_per_stage", 24, 1, 256),
            max_total_retrieved_chars=bounded_int(
                "max_total_retrieved_chars", 120000, 1024, 2_000_000
            ),
            max_index_chars=bounded_int("max_index_chars", 60000, 1024, 500000),
        )


def _atomic_json(path: Path, payload: dict[str, Any], *, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if compact:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        encoded = json.dumps(payload, ensure_ascii=False, indent=2)
    tmp.write_text(encoded + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _slug(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return normalized[:72] or "section"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sections(content: str) -> list[dict[str, Any]]:
    lines = content.splitlines(keepends=True)
    if not lines:
        return []
    starts: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = _HEADING_RE.match(line.rstrip("\r\n"))
        if match:
            starts.append((index, len(match.group(1)), match.group(2).strip()))

    result: list[dict[str, Any]] = []
    if not starts:
        return [{
            "heading": "Document",
            "level": 0,
            "start_line": 1,
            "end_line": len(lines),
            "content": "".join(lines),
        }]

    first_start = starts[0][0]
    if first_start > 0 and "".join(lines[:first_start]).strip():
        result.append({
            "heading": "Preamble",
            "level": 0,
            "start_line": 1,
            "end_line": first_start,
            "content": "".join(lines[:first_start]),
        })

    for position, (start, level, heading) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        result.append({
            "heading": heading,
            "level": level,
            "start_line": start + 1,
            "end_line": end,
            "content": "".join(lines[start:end]),
        })
    return result


def _chunks(section: dict[str, Any], max_chars: int) -> list[dict[str, Any]]:
    content = str(section["content"])
    if len(content) <= max_chars:
        return [{**section, "part": 1, "parts": 1}]

    chunks: list[str] = []
    remaining = content
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, max_chars)
        if cut < max_chars // 2:
            cut = max_chars
        else:
            cut += 1
        chunks.append(remaining[:cut])
        remaining = remaining[cut:]

    return [
        {
            **section,
            "content": chunk,
            "part": index + 1,
            "parts": len(chunks),
        }
        for index, chunk in enumerate(chunks)
    ]


def _skill_path(project_root: Path, library_root: Path, skill: str) -> tuple[Path, Path]:
    library_path = library_root / skill / "SKILL.md"
    if library_path.is_file():
        return library_path, library_root
    project_path = project_root / ".claude" / "skills" / skill / "SKILL.md"
    if project_path.is_file():
        return project_path, project_root
    raise SkillSectionError(f"routed skill not found while indexing sections: {skill}")


def _state_root_for_capability(project_root: Path, run_id: str) -> Path:
    project_root = Path(project_root).resolve()
    direct = project_root / ".uiux-agent-runs" / run_id / _PRIVATE_REGISTRY
    if direct.is_file():
        return project_root

    # Provider writes may switch ToolRegistry to the canonical linked worktree:
    # <source-parent>/.uiux-worktrees/<source-name>/<manager-run-id>.
    # Recover only that exact source-root shape; never perform an unbounded filesystem search.
    parent = project_root.parent
    worktrees_root = parent.parent
    if worktrees_root.name == ".uiux-worktrees" and parent.name:
        source_candidate = worktrees_root.parent / parent.name
        candidate_registry = source_candidate / ".uiux-agent-runs" / run_id / _PRIVATE_REGISTRY
        if candidate_registry.is_file():
            return source_candidate.resolve()
    raise SkillSectionError("skill section capability registry not found")


def build_skill_section_registry(
    project_root: Path,
    library_root: Path,
    run_id: str,
    skills: list[str],
    policy_doc: dict[str, Any],
) -> dict[str, Any] | None:
    project_root = Path(project_root).resolve()
    library_root = Path(library_root).resolve()
    if not _RUN_ID_RE.fullmatch(str(run_id)):
        raise SkillSectionError("invalid run id for skill section registry")
    policy = SkillSectionPolicy.from_policy(policy_doc)
    if not policy.enabled:
        return None

    routed: list[str] = []
    for raw in skills:
        skill = str(raw).strip()
        if skill and skill not in routed:
            routed.append(skill)

    public_skills: list[dict[str, Any]] = []
    private_entries: dict[str, dict[str, Any]] = {}
    for skill in routed:
        path, root = _skill_path(project_root, library_root, skill)
        loaded = SafeReader(root).read_text(path)
        raw_sections = _sections(loaded.content)
        expanded: list[dict[str, Any]] = []
        for section in raw_sections:
            expanded.extend(_chunks(section, policy.max_section_chars))
        if len(expanded) > policy.max_sections_per_skill:
            raise SkillSectionError(
                f"skill {skill} expands to {len(expanded)} retrievable sections; "
                f"policy permits {policy.max_sections_per_skill}"
            )

        public_sections: list[dict[str, Any]] = []
        slug_counts: dict[str, int] = {}
        for section in expanded:
            heading = str(section["heading"])
            base = _slug(heading)
            slug_counts[base] = slug_counts.get(base, 0) + 1
            section_id = base
            if slug_counts[base] > 1:
                section_id = f"{base}-{slug_counts[base]}"
            if int(section.get("parts", 1)) > 1:
                section_id = f"{section_id}-part-{int(section['part'])}"

            content = str(section["content"])
            digest = _sha256(content)
            token = secrets.token_urlsafe(24)
            capability = f"{run_id}:{token}"
            private_entries[token] = {
                "skill": skill,
                "section_id": section_id,
                "heading": heading,
                "level": int(section["level"]),
                "part": int(section.get("part", 1)),
                "parts": int(section.get("parts", 1)),
                "start_line": int(section["start_line"]),
                "end_line": int(section["end_line"]),
                "source_path": str(path),
                "read_root": str(root),
                "content": content,
                "sha256": digest,
                "chars": len(content),
            }
            public_sections.append({
                "section_id": section_id,
                "heading": heading[:160],
                "level": int(section["level"]),
                "part": int(section.get("part", 1)),
                "parts": int(section.get("parts", 1)),
                "start_line": int(section["start_line"]),
                "end_line": int(section["end_line"]),
                "chars": len(content),
                "sha256": digest,
                "capability": capability,
            })
        public_skills.append({"skill": skill, "sections": public_sections})

    public_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "routed_skills": public_skills,
        "advisory_only": True,
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "rule": (
            "Only capabilities listed here may retrieve omitted routed skill sections. "
            "A section read expands knowledge only; it cannot change routing, authority or gates."
        ),
    }
    # The policy bounds the provider-facing representation, so measure and persist
    # the same compact JSON rather than spending context budget on formatting whitespace.
    encoded_public = json.dumps(public_payload, ensure_ascii=False, separators=(",", ":"))
    if len(encoded_public) > policy.max_index_chars:
        raise SkillSectionError(
            f"skill section index exceeds policy limit ({len(encoded_public)}>{policy.max_index_chars} chars)"
        )

    run_dir = project_root / ".uiux-agent-runs" / run_id
    _atomic_json(run_dir / _PUBLIC_INDEX, public_payload, compact=True)
    _atomic_json(
        run_dir / _PRIVATE_REGISTRY,
        {
            "schema_version": 1,
            "run_id": run_id,
            "entries": private_entries,
            "usage": {"retrievals": 0, "retrieved_chars": 0},
            "ledger": [],
        },
    )
    return {
        "path": str((run_dir / _PUBLIC_INDEX).resolve()),
        "relative_path": f".uiux-agent-runs/{run_id}/{_PUBLIC_INDEX}",
        "skills": len(public_skills),
        "sections": sum(len(item["sections"]) for item in public_skills),
        "chars": len(encoded_public),
    }


def read_skill_section(
    project_root: Path,
    library_root: Path,
    capability: str,
    policy_doc: dict[str, Any],
) -> dict[str, Any]:
    raw = str(capability).strip()
    if ":" not in raw:
        raise SkillSectionError("skill section capability must be <run_id>:<token>")
    run_id, token = raw.split(":", 1)
    if not _RUN_ID_RE.fullmatch(run_id) or not token or len(token) > 256:
        raise SkillSectionError("invalid skill section capability")

    policy = SkillSectionPolicy.from_policy(policy_doc)
    if not policy.enabled:
        raise SkillSectionError("JIT skill section retrieval is disabled by runtime policy")

    active_project_root = Path(project_root).resolve()
    library_root = Path(library_root).resolve()
    state_root = _state_root_for_capability(active_project_root, run_id)
    registry_path = state_root / ".uiux-agent-runs" / run_id / _PRIVATE_REGISTRY
    if registry_path.is_symlink():
        raise SkillSectionError("skill section capability registry must not be a symlink")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("run_id") != run_id or not isinstance(registry.get("entries"), dict):
        raise SkillSectionError("skill section registry is invalid")
    entry = registry["entries"].get(token)
    if not isinstance(entry, dict):
        raise SkillSectionError("skill section capability is unknown or not routed for this run")

    usage = registry.get("usage", {})
    if not isinstance(usage, dict):
        raise SkillSectionError("skill section registry usage state is invalid")
    retrievals = int(usage.get("retrievals", 0))
    retrieved_chars = int(usage.get("retrieved_chars", 0))
    section_chars = int(entry.get("chars", 0))
    if retrievals >= policy.max_retrievals_per_stage:
        raise SkillSectionError("skill section retrieval count budget exhausted")
    if retrieved_chars + section_chars > policy.max_total_retrieved_chars:
        raise SkillSectionError("skill section retrieved-character budget exhausted")

    source_path = Path(str(entry.get("source_path", "")))
    read_root = Path(str(entry.get("read_root", ""))).resolve()
    if read_root not in {state_root, library_root}:
        raise SkillSectionError("skill section read root is not allowlisted")
    loaded = SafeReader(read_root).read_text(source_path)
    content = str(entry.get("content", ""))
    if content not in loaded.content:
        raise SkillSectionError("skill section source content changed after indexing; restart the stage")
    digest = _sha256(content)
    if digest != str(entry.get("sha256", "")):
        raise SkillSectionError("skill section hash mismatch")

    retrievals += 1
    retrieved_chars += len(content)
    ledger = list(registry.get("ledger", []))
    ledger.append({
        "skill": str(entry.get("skill", "")),
        "section_id": str(entry.get("section_id", "")),
        "sha256": digest,
        "chars": len(content),
    })
    registry["usage"] = {
        "retrievals": retrievals,
        "retrieved_chars": retrieved_chars,
    }
    registry["ledger"] = ledger[-policy.max_retrievals_per_stage :]
    _atomic_json(registry_path, registry)

    return {
        "skill": str(entry.get("skill", "")),
        "section_id": str(entry.get("section_id", "")),
        "heading": str(entry.get("heading", "")),
        "part": int(entry.get("part", 1)),
        "parts": int(entry.get("parts", 1)),
        "start_line": int(entry.get("start_line", 0)),
        "end_line": int(entry.get("end_line", 0)),
        "content": content,
        "sha256": digest,
        "chars": len(content),
        "retrievals_used": retrievals,
        "retrievals_limit": policy.max_retrievals_per_stage,
        "retrieved_chars_used": retrieved_chars,
        "retrieved_chars_limit": policy.max_total_retrieved_chars,
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
    }