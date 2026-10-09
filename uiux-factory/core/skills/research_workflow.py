"""Bounded pre-design research guidance; never a research or aesthetic verdict."""
from __future__ import annotations

from typing import Any, Iterable


RESEARCH_RESOURCES = {
    "product-discovery": "skills_UIUX/product-discovery/references/decision-led-research.md",
    "design-reference-research-and-benchmark": "skills_UIUX/design-reference-research-and-benchmark/references/reference-anatomy-method.md",
    "research-synthesis-and-insight-management": "skills_UIUX/research-synthesis-and-insight-management/references/evidence-to-design.md",
}


def research_workflow_packet(context: dict[str, Any], stage_id: str, skills: Iterable[str]) -> dict[str, Any]:
    """Skills are resolved by Flow (external) or activated JIT skills (managed)."""
    names = set(skills)
    explicit = "pre-design-research" in context.get("features", [])
    active = stage_id == "research" and (
        explicit or "design-reference-research-and-benchmark" in names
    )
    return {
        "active": active,
        "reason": ("pre-design-research feature" if explicit else "routed reference research") if active else "outside pre-design research",
        "resources": [path for skill, path in RESEARCH_RESOURCES.items() if active and skill in names],
        "skill_activation": "Activate Flow-routed discovery/reference/synthesis skills as needed; never load non-routed skills." if active else None,
        "evidence_schema": "skills_UIUX/research-evidence-pipeline/templates/evidence-ledger.schema.json" if active else None,
        "handoff": ["docs/research/findings.md", "docs/research/decision-log.md", "docs/design-reference-benchmark.md"] if active else [],
        "sequence": ["decision questions", "method and source selection", "inspect source/page/state", "counterevidence", "page/state design response", "verification or remaining unknowns"] if active else [],
        "output_location": "Use the task-authorized artifact location; read_only never grants writes to target files.",
        "evidence_boundary": "DESK_EVIDENCE is not DIRECT_USER; no participants means no human sessions/results. Record observed facts separately from design hypotheses.",
        "human_validation": "UNKNOWN",
        "authority_effect": "none",
        "gate_effect": "none",
        "aesthetic_quality": "UNKNOWN",
    }
