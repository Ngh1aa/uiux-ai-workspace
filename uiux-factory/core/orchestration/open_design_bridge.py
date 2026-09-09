"""Portable DESIGN.md using OpenDesign's documented nine-section convention."""

import json
from pathlib import Path

from core.contracts.design_system_schema import DesignSystemContract
from core.contracts.design_context_schema import ReferenceBoard
from core.runtime.design_tokens import token_css
from core.skills.frontend_design_policy import FRONTEND_DESIGN_POLICY, POLICY_SOURCES


def cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def design_markdown(system: DesignSystemContract, board: ReferenceBoard, goal: str) -> str:
    lines = [f"# {cell(system.brand.name or 'Proposed design system')}", "",
             f"Status: {system.status}. Final visual lock: {system.gates.final_visual_lock}.",
             "", "## Visual Theme & Atmosphere", "", goal, "",
             "Personality: " + ", ".join(system.brand.personality), ""]
    for heading, groups in [
        ("Color Palette & Roles", ["colors"]), ("Typography Rules", ["typography"]),
        ("Component Stylings", ["radius", "border"]), ("Layout Principles", ["spacing", "layout"]),
        ("Depth & Elevation", ["elevation"]),
    ]:
        lines.extend(["## " + heading, "", "| Token | Value | Status | Source |", "|---|---|---|---|"])
        for group in groups:
            for name, token in getattr(system.foundations, group).items():
                lines.append(f"| {cell(name)} | {cell(token.value)} | {token.status} | {cell(token.source)} |")
        if heading == "Component Stylings":
            lines.extend(["", *[f"- {cell(c.name)}: {cell(c.purpose)}. States: {cell(', '.join(c.states))}." for c in system.components]])
        lines.append("")
    lines.extend(["## Do's and Don'ts", "", FRONTEND_DESIGN_POLICY, "",
                  *[f"- Avoid: {cell(item)}" for item in system.brand.avoid], "",
                  "## Responsive Behavior", "",
                  "Validate at 390, 768 and 1440 px. Adapt navigation and reading order; do not merely shrink.",
                  *[f"- {cell(c.name)}: {cell('; '.join(c.responsive_behavior))}" for c in system.components], "",
                  "## Agent Prompt Guide", "", "Treat confirmed brand input as authoritative; derived/default tokens remain proposals.",
                  "References are observations, not brand approvals. Browser checks do not prove aesthetic quality.", "",
                  "### Motion tokens", "", "```json", json.dumps({k:v.model_dump() for k,v in system.foundations.motion.items()}, ensure_ascii=False, indent=2), "```", "",
                  "### Evidence and unresolved items", ""])
    for ref in board.references:
        lines.append(f"- {ref.url}: {ref.status}; {len(ref.observations)} observations. {'; '.join(ref.warnings)}")
    lines.extend(f"- {cell(item)}" for item in system.unresolved_items)
    if system.brand.conflicts:
        lines.extend(["", "Conflicts (precedence applied):", "```json", json.dumps(system.brand.conflicts, ensure_ascii=False, indent=2), "```"])
    lines.extend(["", "### Provenance", "", *[f"- {source}" for source in POLICY_SOURCES],
                  "- https://github.com/nexu-io/open-design/tree/main/design-systems", "",
                  "Portable Markdown and CSS handoff. Slides/PPTX export and OpenDesign app import have not been verified.", ""])
    return "\n".join(lines)


def export_design_package(directory: Path, system: DesignSystemContract, board: ReferenceBoard, goal: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "DESIGN.md"
    path.write_text(design_markdown(system, board, goal), encoding="utf-8")
    (directory / "tokens.css").write_text(token_css(system), encoding="utf-8")
    return path
