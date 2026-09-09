from __future__ import annotations

import re
from pathlib import Path

from core.contracts.creative_review_schema import CreativeDirective
from core.contracts.design_context_schema import DesignContext
from core.contracts.schema import DesignContract
from core.contracts.visual_composition_schema import VisualComposition
from core.runtime.run_context import RunContext


def retarget_slug(slug: str, source_run_id: str, new_run_id: str) -> str:
    suffix = f"-{source_run_id}"
    if slug.endswith(suffix):
        return slug[: -len(suffix)] + f"-{new_run_id}"
    return re.sub(r"-[a-f0-9]{12}$", f"-{new_run_id}", slug) if slug else slug


def context_with_review(source: DesignContext, directive: CreativeDirective) -> DesignContext:
    block = directive.as_prompt_block()
    existing = source.guideline.strip()
    reserve = len(block) + 4
    if reserve >= 30_000:
        merged = block[:30_000]
    else:
        keep = 30_000 - reserve
        merged = ((existing[:keep] + "\n\n") if existing else "") + block
    payload = source.model_dump()
    payload["guideline"] = merged
    return DesignContext.model_validate(payload)


def review_rules(directive: CreativeDirective) -> list[str]:
    rules: list[str] = []
    if directive.overall_direction:
        rules.append(f"Creative Director direction: {directive.overall_direction}")
    for item in directive.revise:
        rules.append(
            f"Creative review [{item.priority}] route={item.route} section={item.section} "
            f"owner={item.owner}: {item.instruction}"
        )
    for item in directive.remove:
        rules.append(f"Creative review REMOVE: {item}")
    return rules


def inject_review_constraints(
    context: RunContext,
    directive: CreativeDirective,
    target: str,
) -> None:
    """Write imported review into copied revision artifacts only.

    This is deliberately dependency-light so the policy can be regression-tested
    without importing MetaGPT or any execution agent.
    """

    rules = review_rules(directive)

    raw_contract = context.artifacts.get("design_contract")
    if raw_contract and target in {
        "design_system",
        "implementation_plan",
        "visual_composition",
        "implementation",
    }:
        path = Path(raw_contract)
        contract = DesignContract.model_validate_json(path.read_text(encoding="utf-8"))
        if directive.overall_direction:
            contract.visual.attributes = list(
                dict.fromkeys(contract.visual.attributes + [directive.overall_direction])
            )
        contract.visual.layout_rules = list(
            dict.fromkeys(contract.visual.layout_rules + rules)
        )
        path.write_text(contract.model_dump_json(indent=2), encoding="utf-8")
        context.add_artifact("design_contract", path)

    raw_visual = context.artifacts.get("visual_composition")
    if raw_visual and target == "implementation":
        path = Path(raw_visual)
        visual = VisualComposition.model_validate_json(path.read_text(encoding="utf-8"))
        visual.composition_principles = list(
            dict.fromkeys(visual.composition_principles + rules)
        )
        for revision in directive.revise:
            if revision.owner != "implementation":
                continue
            for page in visual.pages:
                if revision.route not in {"*", page.path}:
                    continue
                matched = False
                for section in page.sections:
                    if revision.section in {"global", "*", section.type}:
                        section.notes = list(
                            dict.fromkeys(
                                section.notes
                                + [
                                    "Creative Director implementation directive: "
                                    + revision.instruction
                                ]
                            )
                        )
                        matched = True
                if not matched:
                    page.anti_monotony_rules = list(
                        dict.fromkeys(
                            page.anti_monotony_rules
                            + [
                                "Creative Director implementation directive: "
                                + revision.instruction
                            ]
                        )
                    )
        path.write_text(visual.model_dump_json(indent=2), encoding="utf-8")
        context.add_artifact("visual_composition", path)
