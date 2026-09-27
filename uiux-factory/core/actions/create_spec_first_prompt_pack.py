from __future__ import annotations

import json
from typing import Any

from metagpt.actions import Action

from core.contracts.prompt_pack_schema import PromptPack, PromptPackGate


class CreateSpecFirstPromptPack(Action):
    name: str = "CreateSpecFirstPromptPack"

    desc: str = (
        "Compile upstream project/design artifacts into a standalone, project-specific "
        "prompt pack that implementation must read before writing target code."
    )

    @staticmethod
    def _json(value: str) -> dict[str, Any]:
        if not value:
            return {}
        try:
            payload = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _bullets(items: list[str], empty: str = "- UNKNOWN") -> str:
        clean = [str(item).strip() for item in items if str(item).strip()]
        if not clean:
            return empty
        return "\n".join(f"- {item}" for item in clean)

    @staticmethod
    def _token_lines(foundations: dict[str, Any]) -> list[str]:
        lines: list[str] = []
        for group_name in (
            "colors",
            "semantic_colors",
            "typography",
            "spacing",
            "radius",
            "border",
            "elevation",
            "motion",
            "layout",
        ):
            group = foundations.get(group_name, {})
            if not isinstance(group, dict):
                continue
            for key, raw in group.items():
                if isinstance(raw, dict):
                    value = raw.get("value")
                    status = raw.get("status", "unresolved")
                    source = raw.get("source", "")
                    lines.append(
                        f"{group_name}.{key} = {value!r} [{status}]"
                        + (f" — source: {source}" if source else "")
                    )
                else:
                    lines.append(f"{group_name}.{key} = {raw!r}")
        return lines

    @staticmethod
    def _route_lines(routes: list[dict[str, Any]]) -> list[str]:
        result: list[str] = []
        for route in routes:
            path = route.get("path", "UNKNOWN")
            role = route.get("page_role", "UNKNOWN")
            priority = route.get("priority", "P1")
            result.append(f"`{path}` — {role} — {priority}")
        return result

    @staticmethod
    def _page_specs(pages: list[dict[str, Any]]) -> str:
        if not pages:
            return "N/A_JUSTIFIED — no page-level visual composition artifact was produced."
        chunks: list[str] = []
        for page in pages:
            sections = page.get("sections", []) if isinstance(page.get("sections"), list) else []
            section_lines: list[str] = []
            for index, section in enumerate(sections, start=1):
                section_lines.append(
                    f"{index}. **{section.get('type', 'section')}** — "
                    f"purpose: {section.get('purpose', 'UNKNOWN')}; "
                    f"composition: {section.get('composition', 'UNKNOWN')}; "
                    f"visual anchor: {section.get('visual_anchor', 'UNKNOWN')}; "
                    f"density: {section.get('density', 'UNKNOWN')}"
                )
                mobile = section.get("mobile_behavior", [])
                if mobile:
                    section_lines.append(
                        "   - Mobile: " + "; ".join(str(item) for item in mobile)
                    )
            chunks.append(
                "\n".join(
                    [
                        f"### {page.get('path', 'UNKNOWN')} — {page.get('page_role', 'UNKNOWN')}",
                        "",
                        f"**Composition family:** {page.get('composition_family', 'UNKNOWN')}",
                        "",
                        f"**First visual anchor:** {page.get('first_visual_anchor', 'UNKNOWN')}",
                        "",
                        "**Section order:**",
                        *(section_lines or ["1. UNKNOWN"]),
                        "",
                        "**Anti-monotony rules:**",
                        CreateSpecFirstPromptPack._bullets(
                            [str(item) for item in page.get("anti_monotony_rules", [])]
                        ),
                    ]
                )
            )
        return "\n\n".join(chunks)

    async def run(self, instruction: str) -> str:
        payload = json.loads(instruction)
        if not isinstance(payload, dict):
            raise ValueError("Spec compiler input must be a JSON object.")

        goal = str(payload.get("goal", "")).strip()
        if not goal:
            raise ValueError("goal is required")

        research = str(payload.get("research", "")).strip()
        ux_ia = str(payload.get("ux_ia", "")).strip()
        art_direction = str(payload.get("art_direction", "")).strip()
        reference_analysis = str(payload.get("reference_analysis", "")).strip()

        contract = self._json(str(payload.get("design_contract_content", "")))
        system = self._json(str(payload.get("design_system_content", "")))
        plan = self._json(str(payload.get("implementation_plan_content", "")))
        visual = self._json(str(payload.get("visual_composition_content", "")))

        project = contract.get("project", {}) if isinstance(contract.get("project"), dict) else {}
        ux = contract.get("ux", {}) if isinstance(contract.get("ux"), dict) else {}
        visual_contract = contract.get("visual", {}) if isinstance(contract.get("visual"), dict) else {}
        constraints = contract.get("constraints", {}) if isinstance(contract.get("constraints"), dict) else {}
        foundations = system.get("foundations", {}) if isinstance(system.get("foundations"), dict) else {}
        routes = plan.get("routes", []) if isinstance(plan.get("routes"), list) else []
        files = plan.get("files", []) if isinstance(plan.get("files"), list) else []
        pages = visual.get("pages", []) if isinstance(visual.get("pages"), list) else []
        components = system.get("components", []) if isinstance(system.get("components"), list) else []

        domain = str(project.get("domain") or system.get("domain") or visual.get("domain") or "UNKNOWN")
        framework = str(plan.get("framework", "UNKNOWN"))
        language = str(plan.get("language", "UNKNOWN"))
        styling = str(plan.get("styling", "UNKNOWN"))
        output_dir = str(plan.get("output_dir", "UNKNOWN"))
        responsive_scope = "responsive_all" if system.get("gates", {}).get("responsive_contracts_defined") else "UNKNOWN"

        route_lines = self._route_lines(routes)
        file_lines = [
            f"`{item.get('path', 'UNKNOWN')}` — {item.get('purpose', 'UNKNOWN')}"
            for item in files
            if isinstance(item, dict)
        ]
        token_lines = self._token_lines(foundations)

        unresolved: list[str] = []
        for source in (contract, system, plan, visual):
            values = source.get("unresolved_items", []) if isinstance(source, dict) else []
            if isinstance(values, list):
                unresolved.extend(str(item) for item in values if str(item).strip())
        unresolved = list(dict.fromkeys(unresolved))

        preserve_notes = []
        if constraints.get("preserve_page_role_diversity"):
            preserve_notes.append("VERIFIED — preserve page-role composition diversity from the Design Contract.")
        if constraints.get("avoid_shared_hero_everywhere"):
            preserve_notes.append("VERIFIED — do not flatten page roles into one repeated hero/shell pattern.")
        if reference_analysis:
            preserve_notes.append(
                "VERIFIED — reference-analysis evidence exists; preserve only values explicitly supported by that artifact."
            )
        if not preserve_notes:
            preserve_notes.append(
                "UNKNOWN — no byte-for-byte or behavior-preserve contract is proven by the supplied upstream artifacts."
            )

        visual_attributes = [str(item) for item in visual_contract.get("attributes", [])]
        typography_rules = [str(item) for item in visual_contract.get("typography_rules", [])]
        layout_rules = [str(item) for item in visual_contract.get("layout_rules", [])]
        media_rules = [str(item) for item in visual_contract.get("media_rules", [])]
        motion_rules = [str(item) for item in visual_contract.get("motion_rules", [])]
        primary_journey = [str(item) for item in ux.get("primary_journey", [])]
        ux_principles = [str(item) for item in ux.get("principles", [])]

        component_accessibility: list[str] = []
        component_responsive: list[str] = []
        for component in components:
            if not isinstance(component, dict):
                continue
            name = component.get("name", "Component")
            for rule in component.get("accessibility", []) or []:
                component_accessibility.append(f"{name}: {rule}")
            for rule in component.get("responsive_behavior", []) or []:
                component_responsive.append(f"{name}: {rule}")

        project_context = f"""# Project Context\n\n## Goal\n{goal}\n\n## Project classification\n- Domain: {domain}\n- Framework: {framework}\n- Language: {language}\n- Styling: {styling}\n- Output directory: `{output_dir}`\n- Responsive scope: {responsive_scope}\n\n## Source-of-truth artifacts\n- reference analysis: {'VERIFIED' if reference_analysis else 'UNKNOWN'}\n- research: {'VERIFIED' if research else 'UNKNOWN'}\n- UX/IA: {'VERIFIED' if ux_ia else 'UNKNOWN'}\n- art direction: {'VERIFIED' if art_direction else 'UNKNOWN'}\n- design contract: {'VERIFIED' if contract else 'UNKNOWN'}\n- design system: {'VERIFIED' if system else 'UNKNOWN'}\n- implementation plan: {'VERIFIED' if plan else 'UNKNOWN'}\n- visual composition: {'VERIFIED' if visual else 'UNKNOWN'}\n\n## Routes\n{self._bullets(route_lines)}\n\n## Preserve / constraints\n{self._bullets(preserve_notes)}\n\n## Unresolved\n{self._bullets(unresolved, '- N/A_JUSTIFIED — no unresolved items declared upstream.')}\n"""

        research_prompt = (
            "# Pre-Design / Revalidation Prompt\n\n"
            "Research only questions that can still change the approved project direction.\n\n"
            + (
                "N/A_JUSTIFIED — a research artifact already exists for this run. Re-open research only when a later spec decision requires evidence that the current artifact does not contain.\n"
                if research
                else "Research is still required. Ground mutable facts in authoritative sources and distinguish facts from inference.\n"
            )
            + "\nDo not copy requirements from example projects.\n"
        )

        route_tree = self._bullets(route_lines)
        file_tree = self._bullets(file_lines)
        tokens = self._bullets(token_lines, "- UNKNOWN — no resolved design tokens were supplied.")
        unresolved_text = self._bullets(unresolved, "- N/A_JUSTIFIED — no unresolved items declared upstream.")

        full_build_spec = f"""# Project — Full Build Specification\n\n> **Goal:** {goal}\n> **Evidence rule:** VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED.\n\n## 0. Mission\n\nBuild the project described by the upstream Design Contract and implementation artifacts without relying on hidden conversation history.\n\n- Domain: **{domain}**\n- Framework: **{framework}**\n- Language: **{language}**\n- Styling: **{styling}**\n- Responsive scope: **{responsive_scope}**\n- Execution order: **compile spec → read/freeze spec → implement → rendered QA → root-cause repair**\n\n## 1. Source of truth\n\n1. Latest explicit user goal: `{goal}`\n2. Design Contract and Design System artifacts from this run.\n3. Implementation Plan and Visual Composition artifacts from this run.\n4. Current repository/runtime/reference evidence when supplied.\n5. Applicable UIUX Factory rules.\n6. Inference/assumption only when clearly labelled.\n\n## 2. Current verified architecture\n\n- Framework: `{framework}`\n- Language: `{language}`\n- Styling: `{styling}`\n- Planned output: `{output_dir}`\n\n### Routes\n{route_tree}\n\n### Planned files\n{file_tree}\n\n## 3. Immutable / preserve contract\n\n{self._bullets(preserve_notes)}\n\nByte-for-byte preservation, public DOM/API preservation, and protected runtime behavior remain `UNKNOWN` unless the target audit/reference evidence explicitly proves them. Do not invent protected owners.\n\n## 4. Current problems and gaps\n\n### Declared unresolved items\n{unresolved_text}\n\nFor each newly discovered implementation issue use `CURRENT → PROBLEM → IMPACT → PROPOSED RESOLUTION` and repair the earliest responsible owner.\n\n## 5. Product / UX direction\n\n### UX principles\n{self._bullets(ux_principles)}\n\n### Primary journey\n{self._bullets(primary_journey)}\n\nDo not fabricate user research, conversion metrics, or production outcomes.\n\n## 6. Sitemap and information architecture\n\n{route_tree}\n\nTreat every listed route as VERIFIED from the Implementation Plan. Any additional route is PROPOSED until the spec explicitly adds it.\n\n## 7. Page-by-page specification\n\n{self._page_specs(pages)}\n\n## 8. Design system / visual direction\n\n### Visual signature\n{visual.get('visual_signature') or visual_contract.get('signature') or 'UNKNOWN'}\n\n### Attributes\n{self._bullets(visual_attributes)}\n\n### Layout rules\n{self._bullets(layout_rules)}\n\n### Typography rules\n{self._bullets(typography_rules)}\n\n### Media rules\n{self._bullets(media_rules)}\n\n### Resolved/declared tokens\n{tokens}\n\n## 9. Motion and interaction contract\n\n{self._bullets(motion_rules, '- UNKNOWN — no motion rules were supplied upstream.')}\n\nExisting protected animation/function ownership must come from target-source evidence; do not infer exact timings/selectors/functions from visual similarity alone.\n\n## 10. Responsive behavior\n\n- Declared scope: `{responsive_scope}`\n\n### Component responsive rules\n{self._bullets(component_responsive, '- UNKNOWN — no component-level responsive rules were supplied.')}\n\nFor `responsive_all`, verify representative mobile/tablet/desktop widths and repair overflow/clipping/crop/state issues before release.\n\n## 11. Technical architecture and file structure\n\n### Planned files\n{file_tree}\n\n### Implementation order\n{self._bullets([str(item) for item in plan.get('implementation_order', [])])}\n\n### Dependency / framework contract\n- Framework: `{framework}`\n- Language: `{language}`\n- Styling: `{styling}`\n- Avoid unrelated dependencies/refactors.\n- Verify the real target repository before editing; this generated plan does not override newer source truth.\n\n## 12. Accessibility / performance / SEO\n\n### Accessibility\n{self._bullets(component_accessibility, '- UNKNOWN — component accessibility requirements were not supplied upstream.')}\n\n### Performance\n- PROPOSED — no project-code console/runtime errors during the critical journey.\n- PROPOSED — no broken required media or route resources.\n- UNKNOWN — explicit performance budget unless supplied elsewhere.\n\n### SEO / metadata\n- UNKNOWN — inspect target head/metadata ownership before adding or replacing SEO configuration.\n- If SEO is DUE NOW, specify exact title/description/OG/canonical/robots/sitemap ownership in this file before implementation.\n\n## 13. Deployment\n\n- UNKNOWN — inspect the target repository and declared release authority before prescribing GitHub Pages, Vercel, or another platform.\n- If deployment is DUE NOW, this section must be refined to exact config paths/keys, build command, output directory, base-path rules, environment requirements, workflow steps and production verification.\n- Never report “deployed” from a proposed deployment contract alone.\n\n## 14. QA checklist\n\n- [ ] All declared routes load successfully.\n- [ ] Representative rendered pages match the approved page roles and visual composition.\n- [ ] No project-code console errors during the critical journey.\n- [ ] Required media loads without broken resources.\n- [ ] Keyboard/focus behavior satisfies declared component accessibility contracts.\n- [ ] No serious/critical accessibility issue is knowingly hidden.\n- [ ] For responsive scope, representative mobile/tablet/desktop views have no unintended horizontal overflow or clipping.\n- [ ] Visual review is based on actual rendered pixels, not build success alone.\n- [ ] Any deployment due now is verified on the real target environment.\n\n## 15. Deliverables\n\n### Planned project files\n{file_tree}\n\n### Required process artifacts\n- `00-PROJECT-CONTEXT.md`\n- `01-RESEARCH-PROMPT.md`\n- `02-FULL-BUILD-SPEC.md`\n- `03-IMPLEMENTATION-PROMPT.md`\n- `04-QA-REMEDIATION-PROMPT.md`\n- rendered QA evidence for material UI changes\n- implementation deviation record when the frozen spec cannot be followed exactly\n\n## 16. Definition of Done\n\n- [ ] `02-FULL-BUILD-SPEC.md` was compiled before target implementation.\n- [ ] Implementation read the frozen spec before editing target code.\n- [ ] Declared routes/files/components were implemented within scope.\n- [ ] Applicable rendered/responsive/accessibility/runtime checks passed.\n- [ ] QA evaluated the implementation against this same spec.\n- [ ] No blocker or UNKNOWN was silently converted into PASS.\n- [ ] Deviations from this spec are documented with evidence.\n\n```text\nDONE_VERIFIED = [only evidence-backed completed requirements]\nN/A_JUSTIFIED = [intentionally irrelevant requirements]\nPENDING_FUTURE_PHASE = [valid later work]\nBLOCKED = [current blockers]\n```\n"""

        implementation_prompt = f"""# Project — Implementation Prompt\n\nGoal: {goal}\n\n## SPEC-FIRST RULE\nRead `02-FULL-BUILD-SPEC.md` completely before editing target code. Treat that frozen file as the implementation source of truth unless the user's latest explicit correction overrides it.\n\n1. Verify current target source before editing.\n2. Preserve every protected item at its declared preservation level.\n3. Implement only the declared scope/routes/files/states.\n4. Do not independently redesign around the spec.\n5. Record unavoidable deviations with evidence and rationale.\n6. Render representative pages before broad rollout.\n7. Repair root causes instead of weakening tests.\n8. Merge/deploy only within explicit authority.\n"""

        qa_prompt = f"""# Project — QA / Remediation Prompt\n\nGoal: {goal}\n\nAudit the implementation against the same frozen `02-FULL-BUILD-SPEC.md`.\n\nCheck functional behavior, declared routes, rendered visual hierarchy, responsive scope, interaction/motion, media integrity, accessibility, console/runtime errors, SEO/deployment requirements when due now, and delivery inventory.\n\nWhen implementation differs from the spec, identify the earliest responsible owner, repair there, then rerun all affected downstream gates. Do not weaken QA to manufacture a PASS.\n"""

        pack = PromptPack(
            project_context=project_context,
            research_prompt=research_prompt,
            full_build_spec=full_build_spec,
            implementation_prompt=implementation_prompt,
            qa_remediation_prompt=qa_prompt,
            gates=PromptPackGate(
                goal_scope_consistent=True,
                preserve_change_consistent=True,
                responsive_scope_consistent=True,
                qa_maps_to_spec=True,
                implementation_reads_full_spec=True,
                no_hidden_chat_dependency=True,
                no_example_project_leakage=True,
            ),
        )
        return pack.model_dump_json(indent=2)
